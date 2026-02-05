import json
import logging
import time
from django.conf import settings
from groq import Groq
from .models import Projeto

logger = logging.getLogger(__name__)

def gerar_projetos_ia(perfil, avaliacao):
    """
    Gera projetos recomendados utilizando LLM com base no perfil e avaliação do usuário.
    """
    api_key = getattr(settings, "GROQ_API_KEY", None)
    if not api_key:
        logger.error("GROQ_API_KEY não configurada.")
        return False

    client = Groq(api_key=api_key)

    model = getattr(settings, "LLM_MODEL", "openai/gpt-oss-120b")
    
    # Coletar contexto detalhado do perfil
    perfil_data = {
        "nome_empresa": perfil.nome_empresa,
        "setor": perfil.get_setor_atuacao_display(),
        "segmento_especifico": perfil.segmento_especifico,
        "fase": perfil.get_fase_negocio_display(),
        "funcionarios": perfil.get_faixa_funcionarios_display(),
        "faturamento": perfil.get_faturamento_anual_aproximado_display(),
        "orcamento_ti": perfil.get_orcamento_anual_ti_display(),
        "modelo_negocio": perfil.get_modelo_negocio_display(),
        "tipo_receita": perfil.get_tipo_receita_predominante_display(),
        "ticket_medio": perfil.get_ticket_medio_venda_display(),
        "canal_vendas": perfil.get_principal_canal_vendas_display(),
        "estrutura_operacional": perfil.get_estrutura_operacional_display(),
        "abrangencia": perfil.get_abrangencia_geografica_display(),
        "sazonalidade": perfil.get_sazonalidade_negocio_display(),
        "equipe_ti": perfil.get_possui_equipe_ti_dados_display(),
        "alfabetizacao_digital": perfil.get_alfabetizacao_digital_equipe_display(),
        "ferramentas_gestao": perfil.get_ferramentas_gestao_display(),
        "residencia_dados": perfil.get_residencia_dados_display(),
        "prioridade_ano": perfil.get_prioridade_estrategica_ano_display(),
        "restricoes": [r.restricao.nome for r in perfil.restricoes_criticas.all()],
        "objetivos": [o.objetivo.nome for o in perfil.objetivos_12_meses.all()],
        "sistemas": [s.sistema_utilizado.nome for s in perfil.sistemas_utilizados.all()],
    }

    # Coletar contexto detalhado da avaliação
    avaliacao_data = {
        "estagio_geral": avaliacao.get_estagio_geral_display(),
        "pontuacao_geral": float(avaliacao.pontuacao_geral),
        "pilares": []
    }
    for resp_pilar in avaliacao.respostas_pilares.all():
        pilar_info = {
            "nome": resp_pilar.pilar.get_pilar_display(),
            "nivel": resp_pilar.get_estagio_pilar_display(),
            "pontuacao": float(resp_pilar.pontuacao_pilar),
            "detalhes_respostas": []
        }
        for rp in resp_pilar.respostas_perguntas.select_related("pergunta").all():
            alt_attr = f"alternativa_{rp.alternativa_escolhida.lower()}"
            pilar_info["detalhes_respostas"].append({
                "pergunta": rp.pergunta.enunciado,
                "resposta": getattr(rp.pergunta, alt_attr, "N/A")
            })
        avaliacao_data["pilares"].append(pilar_info)

    contexto_negocio = f"""
    DADOS DA EMPRESA:
    {json.dumps(perfil_data, indent=2, ensure_ascii=False)}

    RESULTADOS DO DIAGNÓSTICO DE MATURIDADE:
    {json.dumps(avaliacao_data, indent=2, ensure_ascii=False)}
    """
    
    # Áreas especializadas solicitadas
    areas = [
        "Análise de Dados (Analytics)",
        "Business Intelligence (BI) Dashboards",
        "Data Science",
        "Automações RPA",
        "Inteligência Artificial - LLM e Agentes",
        "IA Machine Learning Supervisionado",
        "IA Machine Learning Não supervisionado",
        "IA Natural Language Processing (NLP)",
        "IA Visão Computacional"
    ]
    areas_str = "\n".join([f"- {a}" for a in areas])
    setor_nome = perfil.get_setor_atuacao_display()

    prompt_system = f"""
    Seu objetivo é criar exatamente TRÊS PROJETOS impactantes para CADA área listada abaixo:
    {areas_str}

    Cada projeto deve ser exclusivo de sua área e totalmente aplicado ao setor '{setor_nome}'.

    Regras obrigatórias:
    - Responda exclusivamente em JSON válido.
    - O JSON deve conter uma lista de objetos na chave "projetos".
    - Linguagem PT-BR, executiva, clara e pragmática, evitando jargões ou termos técnicos.
    - Considere o CONTEXTO COMPLETO da empresa e os RESULTADOS DO DIAGNÓSTICO fornecidos nos dados de entrada para gerar recomendações ultra-personalizadas.
    - Atente-se às ferramentas de gestão já utilizadas e aos sistemas atuais para sugerir integrações ou mudanças pertinentes.
    - Utilize preços e prazos diferentes e variados com base no contexto do usuário e na realidade do mercado brasileiro.

    Formato do objeto de projeto:
    {{
      "area": "Nome da Área",
      "nome_projeto": "Nome impactante",
      "descricao": "Resumo breve",
      "segmento": "{setor_nome}",
      "objetivo_principal": "...",
      "objetivos_secundarios": ["...", "..."],
      "problema": "...",
      "causa_raiz": "...",
      "impacto_do_problema": "...",
      "publico_impactado": "...",
      "solucao": "...",
      "beneficios": ["...", "..."],
      "impacto_operacional": "...",
      "impacto_financeiro": "...",
      "impacto_tempo": "...",
      "indicadores_chave": ["...", "..."],
      "fases_projeto": ["...", "..."],
      "entregaveis": ["...", "..."],
      "riscos": ["...", "..."],
      "mitigacao_riscos": ["...", "..."],
      "dados_necessarios": ["...", "..."],
      "vantagem_competitiva": "...",
      "casos_uso_futuros": ["..."],
      "prazo_minimo": "...",
      "prazo_maximo": "...",
      "prazo_estimado": "...",
      "preco_minimo": "...",
      "preco_maximo": "...",
      "preco_estimado": "...",
    }}
    """

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": prompt_system},
                {"role": "user", "content": f"Com base no contexto a seguir, gere os projetos recomendados:\n\n{contexto_negocio}"}
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
        )
        
        data = json.loads(response.choices[0].message.content)
        projetos_data = data.get("projetos", [])

        if not projetos_data:
            return False

        # Salvar no banco de dados
        # Opcional: Limpar projetos anteriores se quiser regenerar tudo
        # Projeto.objects.filter(perfil=perfil).delete()

        for p_data in projetos_data:
            Projeto.objects.create(
                perfil=perfil,
                area=p_data.get("area", "Geral"),
                nome_projeto=p_data.get("nome_projeto", "Sem nome"),
                descricao=p_data.get("descricao", ""),
                segmento=p_data.get("segmento", setor_nome),
                objetivo_principal=p_data.get("objetivo_principal", ""),
                objetivos_secundarios=p_data.get("objetivos_secundarios", []),
                problema=p_data.get("problema", ""),
                causa_raiz=p_data.get("causa_raiz", ""),
                impacto_do_problema=p_data.get("impacto_do_problema", ""),
                publico_impactado=p_data.get("publico_impactado", ""),
                solucao=p_data.get("solucao", ""),
                beneficios=p_data.get("beneficios", []),
                impacto_operacional=p_data.get("impacto_operacional", ""),
                impacto_financeiro=p_data.get("impacto_financeiro", ""),
                impacto_tempo=p_data.get("impacto_tempo", ""),
                indicadores_chave=p_data.get("indicadores_chave", []),
                fases_projeto=p_data.get("fases_projeto", []),
                entregaveis=p_data.get("entregaveis", []),
                riscos=p_data.get("riscos", []),
                mitigacao_riscos=p_data.get("mitigacao_riscos", []),
                dados_necessarios=p_data.get("dados_necessarios", []),
                vantagem_competitiva=p_data.get("vantagem_competitiva", ""),
                casos_uso_futuros=p_data.get("casos_uso_futuros", []),
                prazo_minimo=p_data.get("prazo_minimo", 0),
                prazo_maximo=p_data.get("prazo_maximo", 0),
                prazo_estimado=p_data.get("prazo_estimado", 0),
                preco_minimo=p_data.get("preco_minimo", 0),
                preco_maximo=p_data.get("preco_maximo", 0),
                preco_estimado=p_data.get("preco_estimado", 0)
            )
        
        return True

    except Exception as e:
        logger.error(f"Erro ao gerar projetos: {e}")
        return False
