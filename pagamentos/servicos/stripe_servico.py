"""
Serviço responsável por toda a integração com a API Stripe.
Isola a lógica de negócio relacionada ao Stripe das views.
"""
import stripe
import logging
from django.conf import settings
from django.urls import reverse
from pagamentos.models import Oferta, Compra

logger = logging.getLogger(__name__)

# Configurar a chave da API Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeServico:
    """
    Classe que encapsula todas as operações com Stripe.
    """
    
    @staticmethod
    def criar_produto(nome, descricao, metadata=None):
        """
        Cria um produto no Stripe.
        
        Args:
            nome: Nome do produto
            descricao: Descrição do produto
            metadata: Dicionário com metadados personalizados
            
        Returns:
            Objeto Product do Stripe
        """
        try:
            produto = stripe.Product.create(
                name=nome,
                description=descricao,
                metadata=metadata or {},
            )
            logger.info(f"Produto criado no Stripe: {produto.id} - {nome}")
            return produto
        except stripe.error.StripeError as e:
            logger.error(f"Erro ao criar produto no Stripe: {str(e)}")
            raise
    
    @staticmethod
    def criar_preco(product_id, valor_centavos, moeda, lookup_key, metadata=None):
        """
        Cria um preço no Stripe associado a um produto.
        
        Args:
            product_id: ID do produto Stripe
            valor_centavos: Valor em centavos
            moeda: Código da moeda (ex: 'brl')
            lookup_key: Chave única para lookup
            metadata: Dicionário com metadados personalizados
            
        Returns:
            Objeto Price do Stripe
        """
        try:
            preco = stripe.Price.create(
                product=product_id,
                unit_amount=valor_centavos,
                currency=moeda,
                lookup_key=lookup_key,
                metadata=metadata or {},
            )
            logger.info(f"Preço criado no Stripe: {preco.id} - {lookup_key}")
            return preco
        except stripe.error.StripeError as e:
            logger.error(f"Erro ao criar preço no Stripe: {str(e)}")
            raise
    
    @staticmethod
    def recuperar_preco_por_lookup_key(lookup_key):
        """
        Busca um preço ativo no Stripe usando a lookup_key.
        """
        try:
            precos = stripe.Price.list(lookup_keys=[lookup_key], active=True, limit=1)
            if precos.data:
                return precos.data[0]
            return None
        except stripe.error.StripeError as e:
            logger.error(f"Erro ao recuperar preço por lookup_key: {str(e)}")
            raise

    @staticmethod
    def criar_checkout_session(compra, oferta, dominio_base):
        """
        Cria uma sessão de checkout do Stripe.
        
        Args:
            compra: Instância do model Compra
            oferta: Instância do model Oferta
            dominio_base: URL base do domínio (ex: http://localhost:8000)
            
        Returns:
            Objeto CheckoutSession do Stripe
        """
        try:
            # URLs de sucesso e cancelamento
            url_sucesso = f"{dominio_base}{reverse('pagamento_sucesso')}"
            url_cancelamento = f"{dominio_base}{reverse('pagamento_cancelado')}"
            
            # Criar sessão de checkout
            session = stripe.checkout.Session.create(
                mode='payment',
                line_items=[
                    {
                        'price': oferta.stripe_price_id,
                        'quantity': 1,
                    }
                ],
                success_url=url_sucesso + '?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=url_cancelamento,
                client_reference_id=str(compra.id),
                metadata={
                    'id_usuario': str(compra.usuario.id),
                    'id_oferta': str(oferta.id),
                    'plano': oferta.slug,
                },
                customer_email=compra.usuario.email if compra.usuario.email else None,
            )
            
            logger.info(f"Checkout Session criada: {session.id} para compra {compra.id}")
            return session
            
        except stripe.error.StripeError as e:
            logger.error(f"Erro ao criar checkout session: {str(e)}")
            raise
    
    @staticmethod
    def recuperar_session(session_id):
        """
        Recupera uma sessão de checkout do Stripe.
        
        Args:
            session_id: ID da sessão
            
        Returns:
            Objeto CheckoutSession do Stripe
        """
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            return session
        except stripe.error.StripeError as e:
            logger.error(f"Erro ao recuperar session {session_id}: {str(e)}")
            raise
    
    @staticmethod
    def listar_produtos():
        """
        Lista todos os produtos no Stripe.
        
        Returns:
            Lista de produtos
        """
        try:
            produtos = stripe.Product.list(limit=100)
            return produtos.data
        except stripe.error.StripeError as e:
            logger.error(f"Erro ao listar produtos: {str(e)}")
            raise
    
    @staticmethod
    def listar_precos(product_id=None):
        """
        Lista preços no Stripe, opcionalmente filtrados por produto.
        
        Args:
            product_id: ID do produto (opcional)
            
        Returns:
            Lista de preços
        """
        try:
            params = {'limit': 100}
            if product_id:
                params['product'] = product_id
            
            precos = stripe.Price.list(**params)
            return precos.data
        except stripe.error.StripeError as e:
            logger.error(f"Erro ao listar preços: {str(e)}")
            raise
    
    @staticmethod
    def verificar_assinatura_webhook(payload, sig_header, webhook_secret):
        """
        Verifica a assinatura de um webhook do Stripe.
        
        Args:
            payload: Corpo da requisição (bytes)
            sig_header: Header Stripe-Signature
            webhook_secret: Segredo do webhook
            
        Returns:
            Objeto Event do Stripe se válido
            
        Raises:
            ValueError: Se a assinatura for inválida
        """
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
            return event
        except ValueError as e:
            logger.error(f"Payload inválido: {str(e)}")
            raise
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Assinatura inválida: {str(e)}")
            raise ValueError("Assinatura inválida")
