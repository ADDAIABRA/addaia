from django.contrib import admin
from .models import Projeto

@admin.register(Projeto)
class ProjetoAdmin(admin.ModelAdmin):
    list_display = ('nome_projeto', 'area', 'get_empresa', 'criado_em')
    list_filter = ('area', 'perfil__nome_empresa', 'criado_em')
    search_fields = ('nome_projeto', 'descricao', 'perfil__nome_empresa')
    readonly_fields = ('criado_em', 'atualizado_em')
    
    fieldsets = (
        ('Identificação', {
            'fields': ('perfil', 'area', 'nome_projeto', 'segmento')
        }),
        ('Descrição e Objetivos', {
            'fields': ('descricao', 'objetivo_principal', 'objetivos_secundarios')
        }),
        ('Análise do Problema', {
            'fields': ('problema', 'causa_raiz', 'impacto_do_problema', 'publico_impactado')
        }),
        ('Solução e Benefícios', {
            'fields': ('solucao', 'beneficios', 'vantagem_competitiva')
        }),
        ('Impactos Estimados', {
            'fields': ('impacto_operacional', 'impacto_financeiro', 'impacto_tempo')
        }),
        ('Planejamento de Execução', {
            'fields': ('indicadores_chave', 'fases_projeto', 'entregaveis')
        }),
        ('Gestão de Riscos', {
            'fields': ('riscos', 'mitigacao_riscos')
        }),
        ('Requisitos e Futuro', {
            'fields': ('dados_necessarios', 'casos_uso_futuros')
        }),
        ('Datas', {
            'fields': ('criado_em', 'atualizado_em'),
            'classes': ('collapse',)
        }),
    )

    def get_empresa(self, obj):
        return obj.perfil.nome_empresa
    get_empresa.short_description = 'Empresa'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # Se for um usuário comum do admin (staff), vê apenas o que pertence a ele
        # (Isso assume que o perfil_empresa está vinculado ao usuário)
        return qs.filter(perfil__usuario=request.user)
