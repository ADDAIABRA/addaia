from django.contrib import admin
from .models import (
    PerfilEmpresa,
    CanalAquisicaoCliente,
    SistemaUtilizado,
    PerfilEmpresaCanaisAquisicao,
    PerfilEmpresaSistemasUtilizados,
    ObjetivoProximo12Meses,
    PerfilEmpresaObjetivos,
    RestricaoCritica,
    PerfilEmpresaRestricoes,
)


class CanaisAquisicaoInline(admin.TabularInline):
    model = PerfilEmpresaCanaisAquisicao
    extra = 1


class SistemasUtilizadosInline(admin.TabularInline):
    model = PerfilEmpresaSistemasUtilizados
    extra = 1


class ObjetivosInline(admin.TabularInline):
    model = PerfilEmpresaObjetivos
    extra = 1


class RestricoesInline(admin.TabularInline):
    model = PerfilEmpresaRestricoes
    extra = 1


@admin.register(PerfilEmpresa)
class PerfilEmpresaAdmin(admin.ModelAdmin):
    list_display = (
        "nome_empresa",
        "usuario",
        "cargo",
        "setor_atuacao",
        "fase_negocio",
        "criado_em",
    )
    list_filter = ("fase_negocio", "setor_atuacao", "regime_tributario")
    search_fields = ("nome_empresa", "usuario__username", "setor_atuacao", "cargo")
    inlines = [
        CanaisAquisicaoInline,
        SistemasUtilizadosInline,
        ObjetivosInline,
        RestricoesInline,
    ]

    fieldsets = (
        ("Identificação", {
            "fields": ("usuario", "nome_empresa", "cargo", "cargo_outro", "setor_atuacao", "setor_outro", "segmento_especifico")
        }),
        ("Estrutura e Estágio", {
            "fields": ("fase_negocio", "faixa_ano_fundacao", "faixa_funcionarios")
        }),
        ("Decisão e Tecnologia", {
            "fields": ("decisao_estrategica", "responsavel_tecnologia_processos", "possui_equipe_ti_dados", "alfabetizacao_digital_equipe")
        }),
        ("Financeiro", {
            "fields": ("regime_tributario", "faturamento_anual_aproximado", "orcamento_anual_ti")
        }),
        ("Modelo de Negócio e Vendas", {
            "fields": ("modelo_negocio", "tipo_receita_predominante", "ticket_medio_venda", "principal_canal_vendas")
        }),
        ("Escala e Operação", {
            "fields": ("estrutura_operacional", "quantidade_unidades", "abrangencia_geografica", "sazonalidade_negocio", "meses_pico")
        }),
        ("Localização", {
            "fields": ("pais", "estado", "cidade")
        }),
        ("Gestão e Dados", {
            "fields": ("ferramentas_gestao", "residencia_dados", "sistemas_outros", "tipo_volume_mensal", "faixa_volume_mensal")
        }),
        ("Estratégia", {
            "fields": ("prioridade_estrategica_ano", "conformidade_lgpd", "preferencia_entrega_recomendacoes")
        }),
        ("Metadados", {
            "fields": ("criado_em", "atualizado_em"),
            "classes": ("collapse",),
        }),
    )

    readonly_fields = ("criado_em", "atualizado_em")


@admin.register(CanalAquisicaoCliente)
class CanalAquisicaoClienteAdmin(admin.ModelAdmin):
    search_fields = ("nome",)


@admin.register(SistemaUtilizado)
class SistemaUtilizadoAdmin(admin.ModelAdmin):
    search_fields = ("nome",)


@admin.register(ObjetivoProximo12Meses)
class ObjetivoProximo12MesesAdmin(admin.ModelAdmin):
    search_fields = ("nome",)


@admin.register(RestricaoCritica)
class RestricaoCriticaAdmin(admin.ModelAdmin):
    search_fields = ("nome",)
