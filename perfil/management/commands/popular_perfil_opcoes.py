from django.core.management.base import BaseCommand
from perfil.models import CanalAquisicaoCliente, SistemaUtilizado, ObjetivoProximo12Meses, RestricaoCritica

class Command(BaseCommand):
    help = 'Popula as opções de múltipla escolha do perfil da empresa'

    def handle(self, *args, **options):
        canais = [
            "LinkedIn", "Instagram", "Facebook", "Google Ads", 
            "YouTube", "TikTok", "Indicação / Boca-a-boca", 
            "Eventos / Feiras", "Prospecção Ativa (Outbound)", 
            "SEO / Blog", "E-mail Marketing", "Parcerias / Afiliados", "Outros"
        ]
        sistemas = [
            "ERP (Gestão Integrada)", "CRM (Gestão de Clientes)", 
            "Mensageiros (WhatsApp / Telegram)", "Planilhas (Excel / Sheets)", 
            "E-mail Corporativo", "Ferramenta de E-mail Marketing", 
            "Plataforma de E-commerce", "Sistema de PDV", 
            "Software de Gestão Financeira", "Software de Gestão de Projetos",
            "Software de BI / Analytics", "Ferramentas de IA (ChatGPT etc.)", 
            "Sistemas Legados / Próprios", "Outros"
        ]
        objetivos = [
            "Aumentar faturamento / vendas", "Reduzir custos operacionais", 
            "Melhorar a experiência do cliente", "Automatizar processos manuais", 
            "Melhorar a qualidade dos dados", "Escalar a operação", 
            "Expansão geográfica / novas unidades", "Lançar novos produtos/serviços",
            "Melhorar a governança / conformidade"
        ]
        restricoes = [
            "Orçamento limitado", "Falta de pessoal qualificado", 
            "Resistência cultural à mudança", "Sistemas atuais limitados/antigos", 
            "Falta de tempo da diretoria", "Dificuldade em integrar dados",
            "Insegurança com novas tecnologias", "Ausência de processos definidos"
        ]

        def populate(model, items):
            count = 0
            for item in items:
                obj, created = model.objects.get_or_create(nome=item)
                if created:
                    count += 1
            return count

        c_canais = populate(CanalAquisicaoCliente, canais)
        c_sistemas = populate(SistemaUtilizado, sistemas)
        c_objetivos = populate(ObjetivoProximo12Meses, objetivos)
        c_restricoes = populate(RestricaoCritica, restricoes)

        self.stdout.write(self.style.SUCCESS(
            f'Sucesso: {c_canais} canais, {c_sistemas} sistemas, '
            f'{c_objetivos} objetivos e {c_restricoes} restrições criados.'
        ))
