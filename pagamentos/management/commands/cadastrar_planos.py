"""
Management command para provisionar o catálogo de planos de assinatura.
Cria 6 ofertas: 3 planos x 2 periodicidades (mensal e anual).
"""
from django.core.management.base import BaseCommand
from pagamentos.models import Oferta


class Command(BaseCommand):
    help = 'Provisiona ou sincroniza o catálogo de planos localmente'
    
    def handle(self, *args, **options):
        """
        Cria as ofertas no banco de dados local.
        Planos: Básico (300 leads), Profissional (1000 leads), Enterprise (5000 leads)
        Periodicidade: Mensal e Anual (20% desconto no anual)
        """
        self.stdout.write(self.style.WARNING('Provisionando catálogo de planos...'))
        
        ofertas_config = [
            # Básico - 300 leads/mês
            {
                'slug': 'basico_mensal',
                'nome_exibicao': 'Básico - Mensal',
                'descricao': '300 leads por mês - Assinatura mensal',
                'valor_centavos': 11900,
                'leads_mensais': 300,
                'periodicidade': 'mensal',
            },
            {
                'slug': 'basico_anual',
                'nome_exibicao': 'Básico - Anual',
                'descricao': '300 leads por mês - Assinatura anual (20% off)',
                'valor_centavos': 114200,
                'leads_mensais': 300,
                'periodicidade': 'anual',
            },
            # Profissional - 1000 leads/mês
            {
                'slug': 'profissional_mensal',
                'nome_exibicao': 'Profissional - Mensal',
                'descricao': '1.000 leads por mês - Assinatura mensal',
                'valor_centavos': 24900,
                'leads_mensais': 1000,
                'periodicidade': 'mensal',
            },
            {
                'slug': 'profissional_anual',
                'nome_exibicao': 'Profissional - Anual',
                'descricao': '1.000 leads por mês - Assinatura anual (20% off)',
                'valor_centavos': 239000,
                'leads_mensais': 1000,
                'periodicidade': 'anual',
            },
            # Enterprise - 5000 leads/mês
            {
                'slug': 'enterprise_mensal',
                'nome_exibicao': 'Enterprise - Mensal',
                'descricao': '5.000 leads por mês - Assinatura mensal',
                'valor_centavos': 49900,
                'leads_mensais': 5000,
                'periodicidade': 'mensal',
            },
            {
                'slug': 'enterprise_anual',
                'nome_exibicao': 'Enterprise - Anual',
                'descricao': '5.000 leads por mês - Assinatura anual (20% off)',
                'valor_centavos': 479000,
                'leads_mensais': 5000,
                'periodicidade': 'anual',
            },
        ]
        
        slugs_mantidos = [c['slug'] for c in ofertas_config]
        
        for config in ofertas_config:
            self.processar_oferta(config)
            
        # Desativar planos que não estão na configuração atual (ex: ouro legado)
        desativados = Oferta.objects.exclude(slug__in=slugs_mantidos).update(ativo=False)
        if desativados:
            self.stdout.write(self.style.WARNING(f'\n-> {desativados} planos antigos foram desativados.'))
        
        self.stdout.write(self.style.SUCCESS('\n[OK] Provisionamento concluido!'))
    
    def processar_oferta(self, config):
        """
        Processa uma oferta individual: cria ou atualiza no banco.
        """
        slug = config['slug']
        self.stdout.write(f'\n--- Processando {slug.upper()} ---')
        
        oferta, criada = Oferta.objects.get_or_create(
            slug=slug,
            defaults={
                'nome_exibicao': config['nome_exibicao'],
                'descricao': config['descricao'],
                'valor_centavos': config['valor_centavos'],
                'moeda': 'brl',
                'leads_mensais': config.get('leads_mensais', 0),
                'periodicidade': config.get('periodicidade', 'mensal'),
                'ativo': True,
            }
        )
        
        if criada:
            self.stdout.write('  [OK] Oferta criada no banco de dados')
        else:
            oferta.nome_exibicao = config['nome_exibicao']
            oferta.descricao = config['descricao']
            oferta.valor_centavos = config['valor_centavos']
            oferta.leads_mensais = config.get('leads_mensais', 0)
            oferta.periodicidade = config.get('periodicidade', 'mensal')
            oferta.save()
            self.stdout.write('  [OK] Oferta atualizada no banco de dados')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'  [OK] {slug}: R$ {oferta.valor_reais()} - {oferta.leads_mensais} leads/mes'
            )
        )
