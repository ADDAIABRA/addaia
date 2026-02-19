"""
Configuração do Django Admin para os models de pagamentos.
"""
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from django.contrib import admin
from .models import Oferta, Compra, Assinatura, AcessoUsuario, EventoMercadoPago


class OfertaResource(resources.ModelResource):
    class Meta:
        model = Oferta
        fields = (
            "id",
            "slug",
            "nome_exibicao",
            "descricao",
            "valor_centavos",
            "moeda",
            "leads_mensais",
            "periodicidade",
            "ativo",
            "criado_em",
            "atualizado_em",
        )
        export_order = fields


class AssinaturaResource(resources.ModelResource):
    class Meta:
        model = Assinatura
        fields = ("id", "usuario", "oferta", "status", "mercadopago_preapproval_id", "criado_em", "atualizado_em")
        export_order = fields


class CompraResource(resources.ModelResource):
    class Meta:
        model = Compra
        fields = (
            "id",
            "usuario",
            "oferta",
            "status",
            "mercadopago_preference_id",
            "mercadopago_preapproval_id",
            "mercadopago_payment_id",
            "criado_em",
            "atualizado_em",
        )
        export_order = fields


class AcessoUsuarioResource(resources.ModelResource):
    class Meta:
        model = AcessoUsuario
        fields = (
            "id",
            "usuario",
            "nivel",
            "status",
            "leads_limite_mensal",
            "leads_consumidos_mes",
            "mes_referencia",
            "concedido_em",
            "atualizado_em",
            "ultima_compra",
            "ultima_assinatura",
        )
        export_order = fields


class EventoMercadoPagoResource(resources.ModelResource):
    class Meta:
        model = EventoMercadoPago
        fields = (
            "id",
            "event_id",
            "tipo",
            "processado_em",
            "dados_json",
        )
        export_order = fields


@admin.register(Oferta)
class OfertaAdmin(ImportExportModelAdmin):
    resource_class = OfertaResource
    """
    Admin para o model Oferta.
    """
    list_display = ['nome_exibicao', 'slug', 'valor_centavos_display', 
                    'ativo', 'criado_em']
    list_filter = ['ativo', 'slug']
    search_fields = ['nome_exibicao', 'slug']
    readonly_fields = ['criado_em', 'atualizado_em']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('slug', 'nome_exibicao', 'descricao', 'periodicidade', 'ativo')
        }),
        ('Preço e Leads', {
            'fields': ('valor_centavos', 'moeda', 'leads_mensais')
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
class CompraAdmin(ImportExportModelAdmin):
    resource_class = CompraResource
    """
    Admin para o model Compra.
    """
    list_display = ['id', 'usuario', 'oferta', 'status', 'criado_em']
    list_filter = ['status', 'criado_em', 'oferta']
    search_fields = ['usuario__username', 'usuario__email', 
                    'mercadopago_preference_id', 'mercadopago_payment_id']
    readonly_fields = ['criado_em', 'atualizado_em']
    raw_id_fields = ['usuario', 'oferta']
    
    fieldsets = (
        ('Compra', {
            'fields': ('usuario', 'oferta', 'status')
        }),
        ('Mercado Pago', {
            'fields': ('mercadopago_preference_id', 'mercadopago_preapproval_id', 'mercadopago_payment_id')
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


@admin.register(Assinatura)
class AssinaturaAdmin(ImportExportModelAdmin):
    resource_class = AssinaturaResource
    list_display = ['id', 'usuario', 'oferta', 'status', 'criado_em']
    list_filter = ['status', 'oferta', 'criado_em']
    search_fields = ['usuario__username', 'usuario__email', 'mercadopago_preapproval_id']
    readonly_fields = ['criado_em', 'atualizado_em']
    raw_id_fields = ['usuario', 'oferta']
    fieldsets = (
        ('Assinatura', {'fields': ('usuario', 'oferta', 'status')}),
        ('Mercado Pago', {'fields': ('mercadopago_preapproval_id',)}),
        ('Datas', {'fields': ('criado_em', 'atualizado_em')}),
    )


@admin.register(AcessoUsuario)
class AcessoUsuarioAdmin(ImportExportModelAdmin):
    resource_class = AcessoUsuarioResource
    """
    Admin para o model AcessoUsuario.
    """
    list_display = ['usuario', 'nivel', 'status', 'leads_limite_mensal', 'leads_consumidos_mes', 'concedido_em']
    list_filter = ['nivel', 'status', 'concedido_em']
    search_fields = ['usuario__username', 'usuario__email']
    readonly_fields = ['concedido_em', 'atualizado_em']
    raw_id_fields = ['usuario', 'ultima_compra', 'ultima_assinatura']
    
    fieldsets = (
        ('Usuário', {'fields': ('usuario',)}),
        ('Acesso', {'fields': ('nivel', 'status', 'ultima_compra', 'ultima_assinatura')}),
        ('Leads', {'fields': ('leads_limite_mensal', 'leads_consumidos_mes', 'mes_referencia')}),
        ('Datas', {'fields': ('concedido_em', 'atualizado_em')}),
    )


@admin.register(EventoMercadoPago)
class EventoMercadoPagoAdmin(ImportExportModelAdmin):
    resource_class = EventoMercadoPagoResource
    """
    Admin para o model EventoMercadoPago (apenas leitura).
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
