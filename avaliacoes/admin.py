from django.contrib import admin
from .models import AvaliacaoProjeto

@admin.register(AvaliacaoProjeto)
class AvaliacaoProjetoAdmin(admin.ModelAdmin):
    list_display = ('projeto', 'perfil', 'nivel_interesse', 'criado_em')
    list_filter = ('nivel_interesse', 'criado_em', 'projeto__area')
    search_fields = ('projeto__nome_projeto', 'perfil__nome_empresa', 'feedback_texto')
    readonly_fields = ('criado_em', 'atualizado_em')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('projeto', 'perfil')
