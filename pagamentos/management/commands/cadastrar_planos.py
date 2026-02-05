"""
Management command para provisionar o catálogo de produtos e preços no Stripe.
Pode ser executado em modo teste ou produção.
"""
import uuid
from django.core.management.base import BaseCommand
from django.conf import settings
from pagamentos.models import Oferta
from pagamentos.servicos.stripe_servico import StripeServico


class Command(BaseCommand):
    help = 'Provisiona ou sincroniza o catálogo de produtos e preços no Stripe'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Força a criação de novos produtos mesmo se já existirem',
        )
    
    def handle(self, *args, **options):
        """
        Cria produtos e preços no Stripe baseado nas ofertas no banco de dados.
        """
        self.stdout.write(self.style.WARNING('Provisionando catálogo Stripe...'))
        
        # Verificar se as chaves Stripe estão configuradas
        if not settings.STRIPE_SECRET_KEY or not settings.STRIPE_PUBLISHABLE_KEY:
            self.stdout.write(
                self.style.ERROR('Chaves Stripe não configuradas. Verifique o .env')
            )
            return
        
        # Determinar modo (teste ou produção)
        modo = 'TESTE' if settings.STRIPE_SECRET_KEY.startswith('sk_test_') else 'PRODUÇÃO'
        self.stdout.write(self.style.WARNING(f'Modo: {modo}'))
        
        # Buscar ou criar ofertas no banco de dados
        ofertas_config = [
            {
                'slug': 'bronze',
                'nome_exibicao': 'Plano Bronze',
                'descricao': 'Acesso vitalício ao conteúdo Bronze',
                'valor_centavos': 9900,  # R$ 99,00
                'lookup_key': 'bronze_v1',
            },
            {
                'slug': 'prata',
                'nome_exibicao': 'Plano Prata',
                'descricao': 'Acesso vitalício ao conteúdo Bronze e Prata',
                'valor_centavos': 19900,  # R$ 199,00
                'lookup_key': 'prata_v1',
            },
            {
                'slug': 'ouro',
                'nome_exibicao': 'Plano Ouro',
                'descricao': 'Acesso vitalício completo (Bronze, Prata e Ouro)',
                'valor_centavos': 39900,  # R$ 399,00
                'lookup_key': 'ouro_v1',
            },
        ]
        
        for oferta_config in ofertas_config:
            self.processar_oferta(oferta_config, options['force'])
        
        self.stdout.write(self.style.SUCCESS('\n✓ Provisionamento concluído!'))
    
    def processar_oferta(self, config, force=False):
        """
        Processa uma oferta individual: cria ou atualiza no banco e no Stripe.
        """
        slug = config['slug']
        self.stdout.write(f'\n--- Processando {slug.upper()} ---')
        
        # Buscar ou criar oferta no banco
        oferta, criada = Oferta.objects.get_or_create(
            slug=slug,
            defaults={
                'nome_exibicao': config['nome_exibicao'],
                'descricao': config['descricao'],
                'valor_centavos': config['valor_centavos'],
                'moeda': 'brl',
                'lookup_key': config['lookup_key'],
                'ativo': True,
            }
        )
        
        if criada:
            self.stdout.write(f'  ✓ Oferta criada no banco de dados')
        else:
            self.stdout.write(f'  → Oferta já existe no banco de dados')
        
        # Verificar se já tem IDs Stripe e se deve forçar recriação
        if oferta.stripe_product_id and oferta.stripe_price_id and not force:
            self.stdout.write(
                f'  → Produto e preço já existem no Stripe '
                f'(Product: {oferta.stripe_product_id}, Price: {oferta.stripe_price_id})'
            )
            self.stdout.write(f'  → Use --force para recriar')
            return
        
        # Tentar recuperar preço existente pela lookup_key
        preco_existente = None
        try:
            preco_existente = StripeServico.recuperar_preco_por_lookup_key(config['lookup_key'])
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ⚠ Erro ao verificar existência: {str(e)}'))

        if preco_existente:
            self.stdout.write(f'  ✓ Preço já existente no Stripe encontrado: {preco_existente.id}')
            oferta.stripe_price_id = preco_existente.id
            oferta.stripe_product_id = preco_existente.product if isinstance(preco_existente.product, str) else preco_existente.product.id
            oferta.save()
            self.stdout.write(f'  ✓ IDs atualizados no banco de dados (Produto reutilizado)')
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'  ✓ {slug.upper()} sincronizado: R$ {oferta.valor_reais()}'
                )
            )
            return

        # Se não existe, prosseguir com a criação
        # Criar produto no Stripe
        try:
            # Usar idempotency key baseado no slug para evitar duplicatas
            idempotency_key_product = f'product-{slug}-{uuid.uuid4().hex[:8]}'
            
            produto = StripeServico.criar_produto(
                nome=config['nome_exibicao'],
                descricao=config['descricao'],
                metadata={
                    'slug': slug,
                    'lookup_key': config['lookup_key'],
                }
            )
            
            oferta.stripe_product_id = produto.id
            self.stdout.write(f'  ✓ Produto criado no Stripe: {produto.id}')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'  ✗ Erro ao criar produto: {str(e)}')
            )
            return
        
        # Criar preço no Stripe
        try:
            preco = StripeServico.criar_preco(
                product_id=produto.id,
                valor_centavos=config['valor_centavos'],
                moeda='brl',
                lookup_key=config['lookup_key'],
                metadata={
                    'slug': slug,
                }
            )
            
            oferta.stripe_price_id = preco.id
            self.stdout.write(f'  ✓ Preço criado no Stripe: {preco.id}')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'  ✗ Erro ao criar preço: {str(e)}')
            )
            return
        
        # Salvar IDs no banco
        oferta.save()
        self.stdout.write(f'  ✓ IDs salvos no banco de dados')
        
        # Resumo
        self.stdout.write(
            self.style.SUCCESS(
                f'  ✓ {slug.upper()} provisionado: R$ {oferta.valor_reais()}'
            )
        )
