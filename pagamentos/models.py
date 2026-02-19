"""
Models do aplicativo de pagamentos.
Todos os nomes foram mantidos em português conforme requisito.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Oferta(models.Model):
    """
    Representa o plano de assinatura.
    Armazena as informações do produto, preço e periodicidade (mensal/anual).
    """
    PERIODICIDADE_CHOICES = [
        ('mensal', 'Mensal'),
        ('anual', 'Anual'),
    ]
    
    SLUG_CHOICES = [
        ('basico_mensal', 'Básico Mensal'),
        ('basico_anual', 'Básico Anual'),
        ('profissional_mensal', 'Profissional Mensal'),
        ('profissional_anual', 'Profissional Anual'),
        ('enterprise_mensal', 'Enterprise Mensal'),
        ('enterprise_anual', 'Enterprise Anual'),
        ('ouro', 'Ouro'),  # Legado
    ]
    
    slug = models.SlugField(unique=True, max_length=50, verbose_name='Identificador')
    nome_exibicao = models.CharField(max_length=100, verbose_name='Nome de Exibição')
    descricao = models.TextField(blank=True, verbose_name='Descrição')
    valor_centavos = models.PositiveIntegerField(verbose_name='Valor em Centavos')
    moeda = models.CharField(max_length=3, default='brl', verbose_name='Moeda')
    leads_mensais = models.PositiveIntegerField(default=0, verbose_name='Leads por mês')
    periodicidade = models.CharField(max_length=20, choices=PERIODICIDADE_CHOICES,
                                     default='mensal', verbose_name='Periodicidade')
    
    ativo = models.BooleanField(default=True, verbose_name='Ativo')
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')
    
    class Meta:
        verbose_name = 'Oferta'
        verbose_name_plural = 'Ofertas'
        ordering = ['valor_centavos']
    
    def __str__(self):
        return f"{self.nome_exibicao} - R$ {self.valor_reais()}"
    
    def valor_reais(self):
        """Retorna o valor em reais formatado."""
        return f"{self.valor_centavos / 100:.2f}"
    
    def slug_base(self):
        """Retorna o slug do plano sem a periodicidade (ex: basico_mensal -> basico)."""
        if '_mensal' in self.slug:
            return self.slug.replace('_mensal', '')
        if '_anual' in self.slug:
            return self.slug.replace('_anual', '')
        return self.slug
    
    @staticmethod
    def obter_nivel_numerico(slug):
        """
        Converte o slug do plano em um valor numérico para comparação.
        basico=1, profissional=2, enterprise=3, ouro=2 (legado -> profissional)
        """
        slug_base = slug
        if '_mensal' in slug:
            slug_base = slug.replace('_mensal', '')
        elif '_anual' in slug:
            slug_base = slug.replace('_anual', '')
        niveis = {'basico': 1, 'profissional': 2, 'enterprise': 3, 'ouro': 2}
        return niveis.get(slug_base, 0)


class Assinatura(models.Model):
    """
    Representa uma assinatura recorrente no Mercado Pago.
    Substitui Compra no fluxo de assinaturas.
    """
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('authorized', 'Autorizada'),
        ('pending', 'Pendente Pagamento'),
        ('paused', 'Pausada'),
        ('cancelled', 'Cancelada'),
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='assinaturas', verbose_name='Usuário')
    oferta = models.ForeignKey(Oferta, on_delete=models.PROTECT,
                               related_name='assinaturas', verbose_name='Oferta')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES,
                             default='pendente', verbose_name='Status')
    mercadopago_preapproval_id = models.CharField(max_length=200, blank=True,
                                                  verbose_name='ID da Assinatura MP')
    
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')
    
    class Meta:
        verbose_name = 'Assinatura'
        verbose_name_plural = 'Assinaturas'
        ordering = ['-criado_em']
    
    def __str__(self):
        return f"Assinatura #{self.id} - {self.usuario.username} - {self.oferta.nome_exibicao} ({self.status})"


class Compra(models.Model):
    """
    Representa uma compra/transação de um plano (histórico).
    Rastreia o status do pagamento e IDs do Mercado Pago.
    """
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('paga', 'Paga'),
        ('cancelada', 'Cancelada'),
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='compras', verbose_name='Usuário')
    oferta = models.ForeignKey(Oferta, on_delete=models.PROTECT, 
                              related_name='compras', verbose_name='Oferta')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, 
                            default='pendente', verbose_name='Status')
    
    # IDs do Mercado Pago
    mercadopago_preference_id = models.CharField(max_length=200, blank=True, 
                                        verbose_name='ID da Preferência MP')
    mercadopago_preapproval_id = models.CharField(max_length=200, blank=True,
                                                  verbose_name='ID da Assinatura MP')
    mercadopago_payment_id = models.CharField(max_length=200, blank=True, 
                                               verbose_name='ID do Pagamento MP')
    
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')
    
    class Meta:
        verbose_name = 'Compra'
        verbose_name_plural = 'Compras'
        ordering = ['-criado_em']
    
    def __str__(self):
        usuario_str = self.usuario.username if self.usuario else "Usuário Removido"
        return f"Compra #{self.id} - {usuario_str} - {self.oferta.nome_exibicao} ({self.status})"


class AcessoUsuario(models.Model):
    """
    Controla o acesso de cada usuário ao plano adquirido.
    Um usuário pode ter apenas um acesso ativo por vez.
    Inclui controle de leads mensais.
    """
    NIVEL_CHOICES = [
        ('basico', 'Básico'),
        ('profissional', 'Profissional'),
        ('enterprise', 'Enterprise'),
        ('ouro', 'Ouro'),  # Legado
    ]
    
    STATUS_CHOICES = [
        ('ativo', 'Ativo'),
        ('suspenso', 'Suspenso'),
        ('revogado', 'Revogado'),
    ]
    
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, 
                                  related_name='acesso', verbose_name='Usuário')
    nivel = models.CharField(max_length=30, verbose_name='Nível de Acesso')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, 
                            default='ativo', verbose_name='Status')
    
    leads_limite_mensal = models.PositiveIntegerField(default=0,
                                                      verbose_name='Leads por mês')
    leads_consumidos_mes = models.PositiveIntegerField(default=0,
                                                      verbose_name='Leads consumidos no mês')
    mes_referencia = models.CharField(max_length=7, blank=True,
                                     verbose_name='Mês referência (YYYY-MM)')
    
    concedido_em = models.DateTimeField(auto_now_add=True, verbose_name='Concedido em')
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')
    
    ultima_compra = models.ForeignKey(Compra, on_delete=models.SET_NULL, 
                                     null=True, blank=True,
                                     related_name='acessos_concedidos',
                                     verbose_name='Última Compra')
    ultima_assinatura = models.ForeignKey('Assinatura', on_delete=models.SET_NULL,
                                          null=True, blank=True,
                                          related_name='acessos_concedidos',
                                          verbose_name='Última Assinatura')
    
    class Meta:
        verbose_name = 'Acesso de Usuário'
        verbose_name_plural = 'Acessos de Usuários'
    
    def __str__(self):
        return f"{self.usuario.username} - {self.nivel} ({self.status})"
    
    def tem_leads_disponiveis(self):
        """Verifica se o usuário tem leads disponíveis no mês atual."""
        from django.utils import timezone
        ano_mes_atual = timezone.now().strftime('%Y-%m')
        if self.mes_referencia != ano_mes_atual:
            return True
        return self.leads_consumidos_mes < self.leads_limite_mensal
    
    def tem_acesso_minimo(self, nivel_requerido):
        """
        Verifica se o usuário tem o nível mínimo de acesso requerido.
        Retorna True se o usuário tiver acesso igual ou superior.
        """
        if self.status != 'ativo':
            return False
        
        nivel_atual = Oferta.obter_nivel_numerico(self.nivel)
        nivel_necessario = Oferta.obter_nivel_numerico(nivel_requerido)
        
        return nivel_atual >= nivel_necessario


class EventoMercadoPago(models.Model):
    """
    Registra eventos do webhook Mercado Pago para implementar idempotência.
    Previne processamento duplicado de eventos.
    """
    event_id = models.CharField(max_length=100, unique=True, 
                               verbose_name='ID do Evento')
    tipo = models.CharField(max_length=100, verbose_name='Tipo de Evento')
    processado_em = models.DateTimeField(auto_now_add=True, 
                                        verbose_name='Processado em')
    dados_json = models.TextField(blank=True, verbose_name='Dados JSON')
    
    class Meta:
        verbose_name = 'Evento Mercado Pago'
        verbose_name_plural = 'Eventos Mercado Pago'
        ordering = ['-processado_em']
    
    def __str__(self):
        return f"{self.event_id} - {self.tipo}"


class Perfil(models.Model):
    """
    Extensão do modelo de usuário para armazenar dados adicionais.
    """
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='pagamentos_perfil', verbose_name='Usuário')
    telefone = models.CharField(max_length=20, verbose_name='Celular/WhatsApp')
    
    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfis'
    
    def __str__(self):
        return f"Perfil de {self.usuario.username}"
