"""
Configuração do Django Admin para os models de pagamentos.
"""
from django.contrib import admin
from .models import Oferta, Compra, AcessoUsuario, EventoStripe


@admin.register(Oferta)
class OfertaAdmin(admin.ModelAdmin):
    """
    Admin para o model Oferta.
    """
    list_display = ['nome_exibicao', 'slug', 'valor_centavos_display', 
                    'lookup_key', 'ativo', 'criado_em']
    list_filter = ['ativo', 'slug']
    search_fields = ['nome_exibicao', 'slug', 'lookup_key']
    readonly_fields = ['criado_em', 'atualizado_em']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('slug', 'nome_exibicao', 'descricao', 'ativo')
        }),
        ('Preço', {
            'fields': ('valor_centavos', 'moeda')
        }),
        ('Stripe', {
            'fields': ('stripe_product_id', 'stripe_price_id', 'lookup_key')
        }),
        ('Datas', {
            'fields': ('criado_em', 'atualizado_em'),
            'classes': ('collapse',)
        }),
    )
    
    def valor_centavos_display(self, obj):
        return f"R$ {obj.valor_reais()}"
    valor_centavos_display.short_description = 'Valor'


@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):
    """
    Admin para o model Compra.
    """
    list_display = ['id', 'usuario', 'oferta', 'status', 'criado_em']
    list_filter = ['status', 'criado_em', 'oferta']
    search_fields = ['usuario__username', 'usuario__email', 
                    'stripe_session_id', 'stripe_payment_intent_id']
    readonly_fields = ['criado_em', 'atualizado_em']
    raw_id_fields = ['usuario', 'oferta']
    
    fieldsets = (
        ('Compra', {
            'fields': ('usuario', 'oferta', 'status')
        }),
        ('Stripe', {
            'fields': ('stripe_session_id', 'stripe_payment_intent_id')
        }),
        ('Datas', {
            'fields': ('criado_em', 'atualizado_em')
        }),
    )
    
    def has_delete_permission(self, request, obj=None):
        # Não permitir deletar compras pagas
        if obj and obj.status == 'paga':
            return False
        return super().has_delete_permission(request, obj)


@admin.register(AcessoUsuario)
class AcessoUsuarioAdmin(admin.ModelAdmin):
    """
    Admin para o model AcessoUsuario.
    """
    list_display = ['usuario', 'nivel', 'status', 'concedido_em', 'atualizado_em']
    list_filter = ['nivel', 'status', 'concedido_em']
    search_fields = ['usuario__username', 'usuario__email']
    readonly_fields = ['concedido_em', 'atualizado_em']
    raw_id_fields = ['usuario', 'ultima_compra']
    
    fieldsets = (
        ('Usuário', {
            'fields': ('usuario',)
        }),
        ('Acesso', {
            'fields': ('nivel', 'status', 'ultima_compra')
        }),
        ('Datas', {
            'fields': ('concedido_em', 'atualizado_em')
        }),
    )


@admin.register(EventoStripe)
class EventoStripeAdmin(admin.ModelAdmin):
    """
    Admin para o model EventoStripe (apenas leitura).
    """
    list_display = ['event_id', 'tipo', 'processado_em']
    list_filter = ['tipo', 'processado_em']
    search_fields = ['event_id', 'tipo']
    readonly_fields = ['event_id', 'tipo', 'processado_em', 'dados_json']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
