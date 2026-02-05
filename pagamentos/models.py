"""
Models do aplicativo de pagamentos.
Todos os nomes foram mantidos em português conforme requisito.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Oferta(models.Model):
    """
    Representa um plano de assinatura (Bronze, Prata ou Ouro).
    Armazena as informações do produto e preço no Stripe.
    """
    SLUG_CHOICES = [
        ('bronze', 'Bronze'),
        ('prata', 'Prata'),
        ('ouro', 'Ouro'),
    ]
    
    slug = models.SlugField(unique=True, max_length=50, choices=SLUG_CHOICES, 
                           verbose_name='Identificador')
    nome_exibicao = models.CharField(max_length=100, verbose_name='Nome de Exibição')
    descricao = models.TextField(blank=True, verbose_name='Descrição')
    valor_centavos = models.PositiveIntegerField(verbose_name='Valor em Centavos')
    moeda = models.CharField(max_length=3, default='brl', verbose_name='Moeda')
    
    # IDs do Stripe
    stripe_product_id = models.CharField(max_length=100, blank=True, 
                                        verbose_name='ID do Produto Stripe')
    stripe_price_id = models.CharField(max_length=100, blank=True, 
                                      verbose_name='ID do Preço Stripe')
    lookup_key = models.CharField(max_length=100, unique=True, 
                                 verbose_name='Lookup Key')
    
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
    
    @staticmethod
    def obter_nivel_numerico(slug):
        """
        Converte o slug do plano em um valor numérico para comparação.
        Bronze = 1, Prata = 2, Ouro = 3
        """
        niveis = {'bronze': 1, 'prata': 2, 'ouro': 3}
        return niveis.get(slug, 0)


class Compra(models.Model):
    """
    Representa uma compra/transação de um plano.
    Rastreia o status do pagamento e IDs do Stripe.
    """
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('paga', 'Paga'),
        ('cancelada', 'Cancelada'),
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, 
                               related_name='compras', verbose_name='Usuário')
    oferta = models.ForeignKey(Oferta, on_delete=models.PROTECT, 
                              related_name='compras', verbose_name='Oferta')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, 
                            default='pendente', verbose_name='Status')
    
    # IDs do Stripe
    stripe_session_id = models.CharField(max_length=200, blank=True, 
                                        verbose_name='ID da Session Stripe')
    stripe_payment_intent_id = models.CharField(max_length=200, blank=True, 
                                               verbose_name='ID do Payment Intent')
    
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')
    
    class Meta:
        verbose_name = 'Compra'
        verbose_name_plural = 'Compras'
        ordering = ['-criado_em']
    
    def __str__(self):
        return f"Compra #{self.id} - {self.usuario.username} - {self.oferta.nome_exibicao} ({self.status})"


class AcessoUsuario(models.Model):
    """
    Controla o acesso de cada usuário ao plano adquirido.
    Um usuário pode ter apenas um acesso ativo por vez.
    """
    NIVEL_CHOICES = [
        ('bronze', 'Bronze'),
        ('prata', 'Prata'),
        ('ouro', 'Ouro'),
    ]
    
    STATUS_CHOICES = [
        ('ativo', 'Ativo'),
        ('suspenso', 'Suspenso'),
        ('revogado', 'Revogado'),
    ]
    
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, 
                                  related_name='acesso', verbose_name='Usuário')
    nivel = models.CharField(max_length=20, choices=NIVEL_CHOICES, 
                           verbose_name='Nível de Acesso')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, 
                            default='ativo', verbose_name='Status')
    
    concedido_em = models.DateTimeField(auto_now_add=True, verbose_name='Concedido em')
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')
    
    ultima_compra = models.ForeignKey(Compra, on_delete=models.SET_NULL, 
                                     null=True, blank=True,
                                     related_name='acessos_concedidos',
                                     verbose_name='Última Compra')
    
    class Meta:
        verbose_name = 'Acesso de Usuário'
        verbose_name_plural = 'Acessos de Usuários'
    
    def __str__(self):
        return f"{self.usuario.username} - {self.nivel} ({self.status})"
    
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


class EventoStripe(models.Model):
    """
    Registra eventos do webhook Stripe para implementar idempotência.
    Previne processamento duplicado de eventos.
    """
    event_id = models.CharField(max_length=100, unique=True, 
                               verbose_name='ID do Evento')
    tipo = models.CharField(max_length=100, verbose_name='Tipo de Evento')
    processado_em = models.DateTimeField(auto_now_add=True, 
                                        verbose_name='Processado em')
    dados_json = models.TextField(blank=True, verbose_name='Dados JSON')
    
    class Meta:
        verbose_name = 'Evento Stripe'
        verbose_name_plural = 'Eventos Stripe'
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
