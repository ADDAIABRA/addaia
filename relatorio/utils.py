import json
import logging
import re
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

from django.conf import settings
from django.utils import timezone
from groq import Groq

try:
    import jsonschema
    from jsonschema import validate
except Exception:  # pragma: no cover
    jsonschema = None  # type: ignore


logger = logging.getLogger(__name__)


# =========================
# Helpers / Config
# =========================

@dataclass(frozen=True)
class LLMResult:
    data: Dict[str, Any]
    raw: str


def _safe_getattr(obj: Any, attr: str, default: Any = "") -> Any:
    try:
        return getattr(obj, attr, default)
    except Exception:
        return default


def _compact_json(obj: Any) -> str:
    # Compacta para reduzir tokens e chances de "escapar" formatação
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))


def _normalize_plan_slug(perfil: Any) -> str:
    plano = "bronze"
    try:
        usuario = _safe_getattr(perfil, "usuario", None)
        acesso = _safe_getattr(usuario, "acesso", None)
        nivel = _safe_getattr(acesso, "nivel", None)
        if isinstance(nivel, str) and nivel.strip():
            plano = nivel.strip().lower()
    except Exception:
        pass

    if plano not in {"bronze", "prata", "ouro"}:
        plano = "bronze"
    return plano


def _strip_code_fences(text: str) -> str:
    """
    Remove ```json ... ``` caso o modelo insista em mandar fences.
    """
    t = text.strip()
    if t.startswith("```"):
        t = re.sub(r"^```[a-zA-Z]*\s*", "", t)
        t = re.sub(r"\s*```$", "", t)
    return t.strip()


def _try_parse_json(text: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Tenta parsear JSON. Retorna (obj, erro_str).
    """
    cleaned = _strip_code_fences(text)
    try:
        parsed = json.loads(cleaned)
        if not isinstance(parsed, dict):
            return None, "JSON raiz não é objeto (dict)."
        return parsed, None
    except Exception as e:
        return None, str(e)


def _require_jsonschema() -> bool:
    """
    Se jsonschema não estiver instalado, ainda dá pra funcionar,
    mas perde validação estrutural. Recomendado instalar.
    """
    return jsonschema is not None


def _validate_schema(instance: Dict[str, Any], schema: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    if not _require_jsonschema():
        # Sem jsonschema, só valida parse + tipo dict
        return True, None
    try:
        validate(instance=instance, schema=schema)
        return True, None
    except jsonschema.ValidationError as e:  # type: ignore
        return False, e.message
    except Exception as e:
        return False, str(e)


# =========================
# JSON Schemas (contract)
# =========================

# Observação: schemas abaixo são "contrato mínimo" e intencionalmente objetivos.
# Você pode endurecer (minItems, maxItems, enums estritas) conforme maturar.

OURO_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "metadados",
        "capa",
        "destaques_estrategicos",
        "sumario_executivo_alta_gestao",
        "benchmark_e_riscos",
        "diagnostico_completo_maturidade",
        "arquitetura_alvo_conceitual",
        "roadmap_12_meses",
        "portfolio_projetos_completo",
        "governanca_minima_e_adocao",
        "plano_capacitacao",
        "proximos_30_dias",
        "notas_e_limites",
    ],
    "properties": {
        "metadados": {
            "type": "object",
            "additionalProperties": False,
            "required": ["nome_plano", "nome_template", "data_geracao", "versao"],
            "properties": {
                "nome_plano": {"type": "string"},
                "nome_template": {"type": "string"},
                "data_geracao": {"type": "string"},
                "versao": {"type": "string"},
            },
        },
        "capa": {
            "type": "object",
            "additionalProperties": False,
            "required": ["nome_empresa", "setor_atuacao", "segmento_especifico", "data_diagnostico", "frase_subtitulo"],
            "properties": {
                "nome_empresa": {"type": "string"},
                "setor_atuacao": {"type": "string"},
                "segmento_especifico": {"type": "string"},
                "data_diagnostico": {"type": "string"},
                "frase_subtitulo": {"type": "string"},
            },
        },
        "destaques_estrategicos": {
            "type": "object",
            "additionalProperties": False,
            "required": ["diagnostico_nivel_atual", "identificacao_gargalos", "foco_estrategico", "proximos_passos"],
            "properties": {
                "diagnostico_nivel_atual": {"type": "string"},
                "identificacao_gargalos": {"type": "string"},
                "foco_estrategico": {"type": "string"},
                "proximos_passos": {"type": "string"},
            },
        },
        "sumario_executivo_alta_gestao": {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "diagnostico_resumido",
                "visao_12_meses",
                "onde_investir",
                "onde_nao_investir_agora",
                "impactos_esperados_por_area",
            ],
            "properties": {
                "diagnostico_resumido": {"type": "string"},
                "visao_12_meses": {"type": "string"},
                "onde_investir": {"type": "array", "items": {"type": "string"}},
                "onde_nao_investir_agora": {"type": "array", "items": {"type": "string"}},
                "impactos_esperados_por_area": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["area", "impacto"],
                        "properties": {"area": {"type": "string"}, "impacto": {"type": "string"}},
                    },
                },
            },
        },
        "benchmark_e_riscos": {
            "type": "object",
            "additionalProperties": False,
            "required": ["benchmark_por_porte_segmento", "riscos_estrategicos", "dependencias_criticas"],
            "properties": {
                "benchmark_por_porte_segmento": {"type": "string"},
                "riscos_estrategicos": {"type": "array", "items": {"type": "string"}},
                "dependencias_criticas": {"type": "array", "items": {"type": "string"}},
            },
        },
        "diagnostico_completo_maturidade": {
            "type": "object",
            "additionalProperties": False,
            "required": ["pilares"],
            "properties": {
                "pilares": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["nome", "nivel", "lacunas", "riscos", "dependencias"],
                        "properties": {
                            "nome": {"type": "string"},
                            "nivel": {"type": "string"},
                            "lacunas": {"type": "array", "items": {"type": "string"}},
                            "riscos": {"type": "array", "items": {"type": "string"}},
                            "dependencias": {"type": "array", "items": {"type": "string"}},
                        },
                    },
                }
            },
        },
        "arquitetura_alvo_conceitual": {
            "type": "object",
            "additionalProperties": False,
            "required": ["camadas", "principios"],
            "properties": {
                "camadas": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["nome", "descricao", "essencial"],
                        "properties": {"nome": {"type": "string"}, "descricao": {"type": "string"}, "essencial": {"type": "boolean"}},
                    },
                },
                "principios": {"type": "array", "items": {"type": "string"}},
            },
        },
        "roadmap_12_meses": {
            "type": "object",
            "additionalProperties": False,
            "required": ["trimestre_1", "trimestre_2", "trimestre_3", "trimestre_4"],
            "properties": {
                "trimestre_1": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["objetivo", "entregas", "decisoes", "indicadores_sucesso", "riscos"],
                    "properties": {
                        "objetivo": {"type": "string"},
                        "entregas": {"type": "array", "items": {"type": "string"}},
                        "decisoes": {"type": "array", "items": {"type": "string"}},
                        "indicadores_sucesso": {"type": "array", "items": {"type": "string"}},
                        "riscos": {"type": "array", "items": {"type": "string"}},
                    },
                },
                "trimestre_2": {"type": "object"},
                "trimestre_3": {"type": "object"},
                "trimestre_4": {"type": "object"},
            },
        },
        "portfolio_projetos_completo": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["nome", "objetivo", "opcao_mvp", "opcao_completa", "complexidade", "observacoes"],
                "properties": {
                    "nome": {"type": "string"},
                    "objetivo": {"type": "string"},
                    "opcao_mvp": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["escopo", "prazo_faixa", "investimento_faixa"],
                        "properties": {
                            "escopo": {"type": "array", "items": {"type": "string"}},
                            "prazo_faixa": {"type": "string"},
                            "investimento_faixa": {"type": "string"},
                        },
                    },
                    "opcao_completa": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["escopo", "prazo_faixa", "investimento_faixa"],
                        "properties": {
                            "escopo": {"type": "array", "items": {"type": "string"}},
                            "prazo_faixa": {"type": "string"},
                            "investimento_faixa": {"type": "string"},
                        },
                    },
                    "complexidade": {"type": "string"},
                    "observacoes": {"type": "string"},
                },
            },
        },
        "governanca_minima_e_adocao": {
            "type": "object",
            "additionalProperties": False,
            "required": ["papeis_responsabilidades", "rotinas_minimas", "cadencia_revisao"],
            "properties": {
                "papeis_responsabilidades": {"type": "array", "items": {"type": "string"}},
                "rotinas_minimas": {"type": "array", "items": {"type": "string"}},
                "cadencia_revisao": {"type": "string"},
            },
        },
        "plano_capacitacao": {
            "type": "object",
            "additionalProperties": False,
            "required": ["o_que_aprender", "ordem_sugerida"],
            "properties": {
                "o_que_aprender": {"type": "array", "items": {"type": "string"}},
                "ordem_sugerida": {"type": "array", "items": {"type": "string"}},
            },
        },
        "proximos_30_dias": {
            "type": "object",
            "additionalProperties": False,
            "required": ["checklist", "decisoes_que_precisam_ser_tomadas"],
            "properties": {
                "checklist": {"type": "array", "items": {"type": "string"}},
                "decisoes_que_precisam_ser_tomadas": {"type": "array", "items": {"type": "string"}},
            },
        },
        "notas_e_limites": {
            "type": "object",
            "additionalProperties": False,
            "required": ["o_que_este_relatorio_nao_cobre", "premissas"],
            "properties": {
                "o_que_este_relatorio_nao_cobre": {"type": "array", "items": {"type": "string"}},
                "premissas": {"type": "array", "items": {"type": "string"}},
            },
        },
    },
}

PRATA_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "metadados",
        "capa",
        "destaques_estrategicos",
        "sumario_executivo",
        "contexto_e_restricoes",
        "avaliacao_maturidade_detalhada",
        "matriz_impacto_esforco",
        "roadmap_90_dias",
        "recomendacoes_detalhadas",
        "portfolio_projetos",
        "notas_e_limites",
    ],
    "properties": {
        "metadados": {
            "type": "object",
            "additionalProperties": False,
            "required": ["nome_plano", "nome_template", "data_geracao", "versao"],
            "properties": {
                "nome_plano": {"type": "string"},
                "nome_template": {"type": "string"},
                "data_geracao": {"type": "string"},
                "versao": {"type": "string"},
            },
        },
        "capa": {
            "type": "object",
            "additionalProperties": False,
            "required": ["nome_empresa", "setor_atuacao", "data_diagnostico", "frase_subtitulo"],
            "properties": {
                "nome_empresa": {"type": "string"},
                "setor_atuacao": {"type": "string"},
                "data_diagnostico": {"type": "string"},
                "frase_subtitulo": {"type": "string"},
            },
        },
        "destaques_estrategicos": {
            "type": "object",
            "additionalProperties": False,
            "required": ["diagnostico_nivel_atual", "identificacao_gargalos", "foco_estrategico", "proximos_passos"],
            "properties": {
                "diagnostico_nivel_atual": {"type": "string"},
                "identificacao_gargalos": {"type": "string"},
                "foco_estrategico": {"type": "string"},
                "proximos_passos": {"type": "string"},
            },
        },
        "sumario_executivo": {
            "type": "object",
            "additionalProperties": False,
            "required": ["estagio_geral", "top_3_prioridades", "o_que_nao_fazer_agora", "resultado_esperado_em_90_dias"],
            "properties": {
                "estagio_geral": {"type": "string"},
                "top_3_prioridades": {"type": "array", "items": {"type": "string"}},
                "o_que_nao_fazer_agora": {"type": "array", "items": {"type": "string"}},
                "resultado_esperado_em_90_dias": {"type": "string"},
            },
        },
        "contexto_e_restricoes": {
            "type": "object",
            "additionalProperties": False,
            "required": ["objetivo_estrategico_ano", "capacidade_investimento", "restricoes_criticas"],
            "properties": {
                "objetivo_estrategico_ano": {"type": "string"},
                "capacidade_investimento": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["orcamento_anual_ti"],
                    "properties": {"orcamento_anual_ti": {"type": "string"}},
                },
                "restricoes_criticas": {"type": "array", "items": {"type": "string"}},
            },
        },
        "avaliacao_maturidade_detalhada": {
            "type": "object",
            "additionalProperties": False,
            "required": ["pilares"],
            "properties": {
                "pilares": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["nome", "nivel", "principais_lacunas"],
                        "properties": {
                            "nome": {"type": "string"},
                            "nivel": {"type": "string"},
                            "principais_lacunas": {"type": "array", "items": {"type": "string"}},
                        },
                    },
                }
            },
        },
        "matriz_impacto_esforco": {
            "type": "object",
            "additionalProperties": False,
            "required": ["ganhos_rapidos", "estrategicos"],
            "properties": {
                "ganhos_rapidos": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["iniciativa", "impacto", "esforco"],
                        "properties": {"iniciativa": {"type": "string"}, "impacto": {"type": "string"}, "esforco": {"type": "string"}},
                    },
                },
                "estrategicos": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["iniciativa", "impacto", "esforco"],
                        "properties": {"iniciativa": {"type": "string"}, "impacto": {"type": "string"}, "esforco": {"type": "string"}},
                    },
                },
            },
        },
        "roadmap_90_dias": {
            "type": "object",
            "required": ["fase_1", "fase_2", "fase_3"],
            "properties": {
                "fase_1": {
                    "type": "object",
                    "required": ["objetivo", "entregaveis"],
                    "properties": {
                        "objetivo": {"type": "string"},
                        "entregaveis": {"type": "array", "items": {"type": "string"}}
                    }
                },
                "fase_2": {
                    "type": "object",
                    "required": ["objetivo", "entregaveis"],
                    "properties": {
                        "objetivo": {"type": "string"},
                        "entregaveis": {"type": "array", "items": {"type": "string"}}
                    }
                },
                "fase_3": {
                    "type": "object",
                    "required": ["objetivo", "entregaveis"],
                    "properties": {
                        "objetivo": {"type": "string"},
                        "entregaveis": {"type": "array", "items": {"type": "string"}}
                    }
                }
            }
        },
        "recomendacoes_detalhadas": {
            "type": "array",
            "minItems": 3,
            "items": {
                "type": "object",
                "required": ["titulo", "esforco_estimado", "o_que_fazer", "impacto_esperado", "por_que_agora"],
                "properties": {
                    "titulo": {"type": "string"},
                    "esforco_estimado": {"type": "string", "enum": ["Baixo", "Médio", "Alto"]},
                    "o_que_fazer": {"type": "string"},
                    "impacto_esperado": {"type": "string"},
                    "por_que_agora": {"type": "string"}
                }
            }
        },
        "portfolio_projetos": {"type": "array", "items": {"type": "object"}},
        "notas_e_limites": {
            "type": "object",
            "additionalProperties": False,
            "required": ["o_que_este_relatorio_nao_cobre", "premissas"],
            "properties": {
                "o_que_este_relatorio_nao_cobre": {"type": "array", "items": {"type": "string"}},
                "premissas": {"type": "array", "items": {"type": "string"}},
            },
        },
    },
}

BRONZE_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "metadados",
        "capa",
        "destaques_estrategicos",
        "sumario_executivo",
        "avaliacao_maturidade",
        "dores_identificadas",
        "recomendacoes_prioritarias",
        "plano_30_dias",
    ],
    "properties": {
        "metadados": {
            "type": "object",
            "additionalProperties": False,
            "required": ["nome_plano", "nome_template", "data_geracao", "versao"],
            "properties": {
                "nome_plano": {"type": "string"},
                "nome_template": {"type": "string"},
                "data_geracao": {"type": "string"},
                "versao": {"type": "string"},
            },
        },
        "capa": {
            "type": "object",
            "additionalProperties": False,
            "required": ["nome_empresa", "setor_atuacao", "frase_subtitulo"],
            "properties": {"nome_empresa": {"type": "string"}, "setor_atuacao": {"type": "string"}, "frase_subtitulo": {"type": "string"}},
        },
        "destaques_estrategicos": {
            "type": "object",
            "additionalProperties": False,
            "required": ["diagnostico_nivel_atual", "identificacao_gargalos", "foco_estrategico", "proximos_passos"],
            "properties": {
                "diagnostico_nivel_atual": {"type": "string"},
                "identificacao_gargalos": {"type": "string"},
                "foco_estrategico": {"type": "string"},
                "proximos_passos": {"type": "string"},
            },
        },
        "sumario_executivo": {
            "type": "object",
            "additionalProperties": False,
            "required": ["estagio_geral", "principal_gargalo", "maior_oportunidade_imediata", "risco_principal_se_nada_for_feito"],
            "properties": {
                "estagio_geral": {"type": "string"},
                "principal_gargalo": {"type": "string"},
                "maior_oportunidade_imediata": {"type": "string"},
                "risco_principal_se_nada_for_feito": {"type": "string"},
            },
        },
        "avaliacao_maturidade": {
            "type": "object",
            "additionalProperties": False,
            "required": ["pilares"],
            "properties": {
                "pilares": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["nome", "nivel", "o_que_significa"],
                        "properties": {
                            "nome": {"type": "string"},
                            "nivel": {"type": "string"},
                            "o_que_significa": {"type": "string"},
                        },
                    },
                }
            },
        },
        "dores_identificadas": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["dor", "impacto"],
                "properties": {
                    "dor": {"type": "string"},
                    "impacto": {"type": "string"}
                }
            }
        },
        "recomendacoes_prioritarias": {
            "type": "array",
            "minItems": 3,
            "items": {
                "type": "object",
                "required": ["titulo", "esforco_estimado", "o_que_fazer", "impacto_esperado", "por_que_agora"],
                "properties": {
                    "titulo": {"type": "string"},
                    "esforco_estimado": {"type": "string", "enum": ["Baixo", "Médio", "Alto"]},
                    "o_que_fazer": {"type": "string"},
                    "impacto_esperado": {"type": "string"},
                    "por_que_agora": {"type": "string"}
                }
            }
        },
        "plano_30_dias": {
            "type": "object",
            "required": ["semana_1", "semana_2", "semana_3_4"],
            "properties": {
                "semana_1": {"type": "array", "items": {"type": "string"}},
                "semana_2": {"type": "array", "items": {"type": "string"}},
                "semana_3_4": {"type": "array", "items": {"type": "string"}}
            }
        },
    },
}


def _schema_for_plan(plano_slug: str) -> Dict[str, Any]:
    if plano_slug == "ouro":
        return OURO_SCHEMA
    if plano_slug == "prata":
        return PRATA_SCHEMA
    return BRONZE_SCHEMA


# =========================
# Prompt builder (safer)
# =========================

def _build_prompt(plano_slug: str, perfil_data: Dict[str, Any], avaliacao_detalhada: Dict[str, Any], data_atual: str) -> str:
    """
    Importante:
    - Não inserimos valores dinâmicos dentro do "schema contrato".
    - Mantemos o contrato curto e direto.
    - Reduzimos chance de arrays quebrados ao enfatizar 'cada item é um objeto'.
    """
    if plano_slug == "ouro":
        contract = _compact_json(OURO_SCHEMA)
        nome_plano = "Avançado"
        template = "Plano Diretor Digital & IA – 12 Meses"
    elif plano_slug == "prata":
        contract = _compact_json(PRATA_SCHEMA)
        nome_plano = "Intermediário"
        template = "Roadmap Executável de 90 Dias"
    else:
        contract = _compact_json(BRONZE_SCHEMA)
        nome_plano = "Básico"
        template = "Diagnóstico Essencial & Próximos Passos"

    return f"""
Gere um relatório executivo PROFISSIONAL em JSON.

REGRAS DE SAÍDA (obrigatórias):
- Responda SOMENTE com um JSON válido (sem Markdown, sem texto extra).
- O JSON raiz deve ser um OBJETO ({{...}}).
- Siga EXATAMENTE o contrato JSON Schema fornecido em CONTRATO.
- Não crie chaves fora do contrato. Não remova chaves obrigatórias.
- Em arrays, cada item deve ser um objeto completo ({{...}}) ou string, conforme o contrato.
- Linguagem PT-BR, executiva, clara e pragmática, evitando jargões ou termos técnicos.
- Não invente números financeiros sem base; quando estimar, use faixas realistas e indique como faixa.
- Respeite restrições informadas.

CONTEXTO:
- Plano: {nome_plano}
- Template: {template}
- Data geração: {data_atual}

DADOS (use como base):
PERFIL={_compact_json(perfil_data)}
AVALIACAO_DETALHADA={_compact_json(avaliacao_detalhada)}

DETALHAMENTO DOS DESTAQUES ESTRATÉGICOS:
- diagnostico_nivel_atual: Explique o nível de maturidade digital atual da empresa de forma clara.
- identificacao_gargalos: Identifique onde a empresa está perdendo dinheiro e tempo (ineficiências).
- foco_estrategico: Diga explicitamente o que a empresa NÃO deve priorizar ou investir agora.
- proximos_passos: Forneça um plano claro e prático para execução imediata.

CONTRATO (JSON Schema):
{contract}
""".strip()


def _build_repair_prompt(plano_slug: str, invalid_text: str, schema: Dict[str, Any]) -> str:
    """
    Prompt de correção: recebe a tentativa inválida e manda "consertar".
    """
    return f"""
Você recebeu uma saída que deveria ser JSON, mas está inválida ou fora do contrato.

TAREFA:
- Corrija o conteúdo para gerar SOMENTE um JSON válido.
- O JSON deve seguir EXATAMENTE o contrato (JSON Schema) abaixo.
- Não inclua Markdown, comentários, nem texto extra.
- Não crie chaves fora do contrato e não remova chaves obrigatórias.
- Garanta que arrays contenham itens completos (objetos bem formados).

CONTRATO (JSON Schema):
{_compact_json(schema)}

SAÍDA INVÁLIDA (para corrigir):
{invalid_text}
""".strip()


# =========================
# LLM call with retries + validation + repair
# =========================

def _call_llm(client: Groq, model: str, messages: list, temperature: float) -> str:
    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        # JSON mode (provider-level). Ainda assim validamos localmente.
        response_format={"type": "json_object"},
        temperature=temperature,
    )
    return (resp.choices[0].message.content or "").strip()


def gerar_conteudo_relatorio(avaliacao) -> Optional[Dict[str, Any]]:
    """
    Gera o conteúdo do relatório utilizando LLM, com validação + reparo.
    Planos: bronze (Básico), prata (Intermediário), ouro (Avançado).
    Retorna dict JSON validado ou None.
    """
    api_key = getattr(settings, "GROQ_API_KEY", None)
    if not api_key:
        logger.error("GROQ_API_KEY não configurada.")
        return None

    client = Groq(api_key=api_key)

    model = getattr(settings, "LLM_MODEL", "openai/gpt-oss-120b")
    # Se você tiver um modelo específico que suporta melhor JSON mode, fixe aqui.

    perfil = getattr(avaliacao, "perfil_empresa", None)
    if not perfil:
        return None

    plano_slug = _normalize_plan_slug(perfil)
    schema = _schema_for_plan(plano_slug)

    # Dados
    data_atual = timezone.now().strftime("%d/%m/%Y")

    perfil_data = {
        "nome_empresa": perfil.nome_empresa,
        "setor_atuacao": perfil.get_setor_atuacao_display(),
        "segmento_especifico": perfil.segmento_especifico or "",
        "fase_negocio": perfil.get_fase_negocio_display(),
        "faixa_funcionarios": perfil.get_faixa_funcionarios_display(),
        "regime_tributario": perfil.get_regime_tributario_display(),
        "faturamento_anual_aproximado": perfil.get_faturamento_anual_aproximado_display(),
        "orcamento_anual_ti": perfil.get_orcamento_anual_ti_display(),
        "modelo_negocio": perfil.get_modelo_negocio_display(),
        "tipo_receita_predominante": perfil.get_tipo_receita_predominante_display(),
        "principal_canal_vendas": perfil.get_principal_canal_vendas_display(),
        "abrangencia_geografica": perfil.get_abrangencia_geografica_display(),
        "estrutura_operacional": perfil.get_estrutura_operacional_display(),
        "quantidade_unidades": (
            perfil.get_quantidade_unidades_display()
            if hasattr(perfil, "get_quantidade_unidades_display")
            else getattr(perfil, "quantidade_unidades", "")
        ),
        "localizacao": {"pais": perfil.pais, "estado": perfil.estado, "cidade": perfil.cidade},
        "possui_equipe_ti_dados": perfil.get_possui_equipe_ti_dados_display(),
        "alfabetizacao_digital_equipe": perfil.get_alfabetizacao_digital_equipe_display(),
        "ferramentas_gestao": perfil.get_ferramentas_gestao_display(),
        "residencia_dados": perfil.get_residencia_dados_display(),
        "prioridade_estrategica_ano": perfil.get_prioridade_estrategica_ano_display(),
        "conformidade_lgpd": perfil.get_conformidade_lgpd_display(),
        "restricoes_criticas": [r.restricao.nome for r in perfil.restricoes_criticas.all()],
        "canais_aquisicao": [c.canal_aquisicao.nome for c in perfil.canais_aquisicao.all()],
        "sistemas_utilizados": [s.sistema_utilizado.nome for s in perfil.sistemas_utilizados.all()],
        "objetivos_12_meses": [o.objetivo.nome for o in perfil.objetivos_12_meses.all()],
        "ticket_medio_venda": perfil.get_ticket_medio_venda_display(),
        "sazonalidade": perfil.get_sazonalidade_negocio_display(),
    }

    avaliacao_detalhada: Dict[str, Any] = {
        "estagio_geral": avaliacao.get_estagio_geral_display(),
        "pontuacao_geral": float(avaliacao.pontuacao_geral),
        "pilares": {},
    }

    for resp_pilar in avaliacao.respostas_pilares.all():
        pilar_key = resp_pilar.pilar.pilar.lower()
        respostas_lista = []
        for rp in resp_pilar.respostas_perguntas.select_related("pergunta").all():
            alt_attr = f"alternativa_{rp.alternativa_escolhida.lower()}"
            respostas_lista.append(
                {
                    "pergunta": rp.pergunta.enunciado,
                    "resposta": getattr(rp.pergunta, alt_attr, "N/A"),
                }
            )
        avaliacao_detalhada["pilares"][pilar_key] = {
            "nivel": resp_pilar.get_estagio_pilar_display(),
            "pontuacao": float(resp_pilar.pontuacao_pilar),
            "diagnostico_base": respostas_lista,
        }

    system_msg = (
        "Você é uma API geradora de relatórios executivos para PMEs. "
        "Retorne apenas JSON válido conforme o contrato (JSON Schema) fornecido."
    )

    prompt = _build_prompt(plano_slug, perfil_data, avaliacao_detalhada, data_atual)

    # Estratégia:
    # 1) gerar normalmente (temp baixa)
    # 2) se falhar parse/validação: reparar usando o texto inválido
    # 3) última tentativa: gerar do zero com temp=0
    max_attempts = 3
    last_raw = None
    last_err = None

    for attempt in range(1, max_attempts + 1):
        try:
            if attempt == 1:
                temperature = 0.2
                messages = [{"role": "system", "content": system_msg}, {"role": "user", "content": prompt}]
            elif attempt == 2 and last_raw:
                temperature = 0.0
                repair_prompt = _build_repair_prompt(plano_slug, last_raw, schema)
                messages = [{"role": "system", "content": system_msg}, {"role": "user", "content": repair_prompt}]
            else:
                temperature = 0.0
                messages = [{"role": "system", "content": system_msg}, {"role": "user", "content": prompt}]

            raw = _call_llm(client, model, messages, temperature=temperature)
            last_raw = raw

            parsed, parse_err = _try_parse_json(raw)
            if parse_err:
                last_err = f"parse_err: {parse_err}"
                continue

            ok, val_err = _validate_schema(parsed, schema)
            if not ok:
                last_err = f"schema_err: {val_err}"
                continue

            return parsed

        except Exception as e:
            last_err = str(e)
            # backoff simples (evita martelar provider)
            time.sleep(0.6 * attempt)

    logger.error("Falha ao gerar relatório (%s). Erro=%s Raw=%s", plano_slug, last_err, (last_raw or "")[:5000])
    return None
