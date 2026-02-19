from django.contrib import admin
from .models import Coleta, Lead


@admin.register(Coleta)
class ColetaAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'keyword', 'cidade', 'bairro', 'usar_raio', 'raio_km', 'status', 'criado_em')
    list_filter = ('status', 'usar_raio')
    search_fields = ('keyword', 'cidade', 'bairro')
    readonly_fields = ('criado_em', 'atualizado_em')


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('id', 'categoria', 'cidade', 'bairro', 'nome', 'telefone', 'usuario', 'coleta', 'nota', 'total_avaliacoes', 'criado_em')
    list_filter = ('coleta', 'usuario', 'categoria', 'cidade')
    search_fields = ('nome', 'telefone', 'endereco', 'categoria', 'cidade', 'bairro')
    readonly_fields = ('criado_em',)
