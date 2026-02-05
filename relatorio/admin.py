from django.contrib import admin
from .models import Relatorio

@admin.register(Relatorio)
class RelatorioAdmin(admin.ModelAdmin):
    list_display = ('id', 'avaliacao', 'criado_em')
    search_fields = ('avaliacao__perfil_empresa__nome_empresa',)
    readonly_fields = ('criado_em', 'atualizado_em')
