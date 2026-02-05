# management/commands/popular_questionarios.py
# Rode: python manage.py popular_questionarios
#
# Ajuste o import do app conforme o seu projeto (ex.: from seu_app.models import ...)
# Este comando cria:
# - 5 Pilares (PilarQuestionario)
# - 50 Perguntas (PerguntaQuestionario), com alternativas A-E

from django.core.management.base import BaseCommand
from django.db import transaction

from questionarios.models import PilarQuestionario, PerguntaQuestionario


QUESTIONARIOS = [
    {
        "pilar": PilarQuestionario.Pilar.TECNOLOGIA_SOFTWARE,
        "ordem_pilar": 1,
        "descricao": "Avalia uso, integração, governança e resiliência dos softwares e sistemas.",
        "prefixo_codigo": "TEC",
        "perguntas": [
            {
                "ordem": 1,
                "enunciado": "Qual é o nível de adoção de softwares de gestão (como ERP ou CRM) na sua empresa?",
                "a": "Não utilizamos nenhum software de gestão; tudo é manual.",
                "b": "Usamos planilhas ou ferramentas básicas gratuitas para tarefas simples.",
                "c": "Temos um software básico integrado para funções essenciais, como finanças.",
                "d": "Utilizamos softwares avançados e integrados em múltiplas áreas do negócio.",
                "e": "Temos um ecossistema de softwares otimizado, com atualizações automáticas e integração total.",
            },
            {
                "ordem": 2,
                "enunciado": "Como sua empresa gerencia atualizações e manutenção de softwares?",
                "a": "Não há processo definido; atualizações são ignoradas.",
                "b": "Atualizamos manualmente quando problemas surgem.",
                "c": "Temos um cronograma básico para verificações periódicas.",
                "d": "Usamos ferramentas de gerenciamento para atualizações automáticas.",
                "e": "Implementamos DevOps ou automações para manutenção contínua e proativa.",
            },
            {
                "ordem": 3,
                "enunciado": "Qual é o grau de uso de ferramentas colaborativas (como Google Workspace ou Microsoft Teams)?",
                "a": "Não usamos; comunicação é por e-mail ou telefone.",
                "b": "Usamos ferramentas gratuitas para comunicação básica.",
                "c": "Integramos ferramentas colaborativas em rotinas diárias.",
                "d": "Temos suítes completas com integração a outros sistemas.",
                "e": "Otimizamos com IA para colaboração em tempo real e produtividade.",
            },
            {
                "ordem": 4,
                "enunciado": "Como é a infraestrutura de TI da sua empresa (servidores, nuvem)?",
                "a": "Tudo local e sem backup; dependemos de computadores individuais.",
                "b": "Usamos armazenamento local com backups manuais ocasionais.",
                "c": "Migrados para nuvem básica para armazenamento e e-mail.",
                "d": "Infraestrutura híbrida com segurança e escalabilidade.",
                "e": "Totalmente em nuvem com IA para monitoramento e otimização automática.",
            },
            {
                "ordem": 5,
                "enunciado": "Qual é o nível de treinamento da equipe em tecnologias e softwares?",
                "a": "Nenhum treinamento formal; aprendizado informal.",
                "b": "Treinamentos básicos quando um novo software é adotado.",
                "c": "Programas regulares para atualização de habilidades.",
                "d": "Certificações e treinamentos avançados integrados ao plano de carreira.",
                "e": "Uso de plataformas de e-learning com IA para personalização contínua.",
            },
            {
                "ordem": 6,
                "enunciado": "Como sua empresa lida com segurança de softwares e ciberameaças?",
                "a": "Sem medidas específicas; dependemos de antivírus gratuitos.",
                "b": "Antivírus básico e senhas simples.",
                "c": "Firewall e políticas de senha implementadas.",
                "d": "Auditorias regulares e ferramentas de detecção avançada.",
                "e": "Sistema de segurança com IA para detecção proativa e resposta automática.",
            },
            {
                "ordem": 7,
                "enunciado": "Qual é a integração entre diferentes softwares usados na empresa?",
                "a": "Nenhum; dados são copiados manualmente entre ferramentas.",
                "b": "Integrações básicas via export/import de arquivos.",
                "c": "Algumas integrações via APIs para fluxos essenciais.",
                "d": "Integrações completas em múltiplos sistemas.",
                "e": "Ecossistema integrado com IA para automação de fluxos end-to-end.",
            },
            {
                "ordem": 8,
                "enunciado": "Como é o uso de softwares para mobilidade (apps móveis)?",
                "a": "Não há suporte móvel; tudo é desktop.",
                "b": "Acesso básico via navegador móvel.",
                "c": "Apps dedicados para funções simples.",
                "d": "Soluções móveis integradas ao core business.",
                "e": "Apps otimizados com IA para acesso em tempo real e decisões móveis.",
            },
            {
                "ordem": 9,
                "enunciado": "Qual é o orçamento dedicado a tecnologia e software anualmente?",
                "a": "Nenhum orçamento específico; gastos reativos.",
                "b": "Baixo, apenas para manutenção essencial.",
                "c": "Moderado, com planejamento para upgrades anuais.",
                "d": "Alto, com foco em inovação e ROI mensurável.",
                "e": "Otimizado com IA para alocação inteligente baseada em dados.",
            },
            {
                "ordem": 10,
                "enunciado": "Como sua empresa avalia o ROI de investimentos em tecnologia?",
                "a": "Não avaliamos; decisões baseadas em intuição.",
                "b": "Avaliações básicas pós-implementação.",
                "c": "Métricas simples como custo vs. benefício.",
                "d": "Análises detalhadas com relatórios periódicos.",
                "e": "Uso de ferramentas de IA para previsão e otimização contínua de ROI.",
            },
        ],
    },
    {
        "pilar": PilarQuestionario.Pilar.DADOS,
        "ordem_pilar": 2,
        "descricao": "Avalia organização, qualidade, governança e uso dos dados no negócio.",
        "prefixo_codigo": "DAD",
        "perguntas": [
            {
                "ordem": 1,
                "enunciado": "Como sua empresa coleta dados de clientes e operações?",
                "a": "Não coletamos dados sistematicamente; anotações manuais.",
                "b": "Coleta básica via planilhas ou formulários simples.",
                "c": "Sistemas automatizados para coleta em pontos chave.",
                "d": "Coleta integrada em múltiplas fontes com qualidade controlada.",
                "e": "Coleta em tempo real com IA para validação e enriquecimento automático.",
            },
            {
                "ordem": 2,
                "enunciado": "Qual é o nível de armazenamento e organização de dados?",
                "a": "Dados dispersos em arquivos locais sem organização.",
                "b": "Armazenados em planilhas ou bancos de dados básicos.",
                "c": "Banco de dados centralizado com backups regulares.",
                "d": "Data warehouse com governança e metadados.",
                "e": "Data lake otimizado com IA para gerenciamento automático.",
            },
            {
                "ordem": 3,
                "enunciado": "Como é a qualidade e limpeza dos dados na sua empresa?",
                "a": "Dados cheios de erros; sem processos de limpeza.",
                "b": "Limpeza manual ocasional quando necessário.",
                "c": "Ferramentas básicas para detecção de duplicatas.",
                "d": "Processos automatizados de ETL para qualidade.",
                "e": "IA para limpeza proativa e detecção de anomalias em tempo real.",
            },
            {
                "ordem": 4,
                "enunciado": "Qual é o grau de conformidade com regulamentações como LGPD?",
                "a": "Não conhecemos ou não aplicamos regulamentações.",
                "b": "Conformidade básica com políticas internas.",
                "c": "Auditorias periódicas e consentimentos coletados.",
                "d": "Sistema completo de governança de dados.",
                "e": "IA integrada para monitoramento contínuo de conformidade.",
            },
            {
                "ordem": 5,
                "enunciado": "Como sua empresa compartilha dados internamente?",
                "a": "Não há compartilhamento; cada departamento gerencia os seus.",
                "b": "Compartilhamento via e-mails ou arquivos compartilhados.",
                "c": "Plataformas colaborativas para acesso controlado.",
                "d": "Dashboards centralizados com permissões granulares.",
                "e": "Acesso em tempo real com IA para recomendações personalizadas.",
            },
            {
                "ordem": 6,
                "enunciado": "Qual é o uso de dados para tomada de decisões?",
                "a": "Decisões baseadas em intuição, sem dados.",
                "b": "Uso ocasional de relatórios simples.",
                "c": "Dados consultados regularmente para decisões operacionais.",
                "d": "Dados integrados em estratégias de negócio.",
                "e": "Decisões impulsionadas por IA com previsões baseadas em dados.",
            },
            {
                "ordem": 7,
                "enunciado": "Como é o backup e recuperação de dados?",
                "a": "Sem backups; risco total de perda.",
                "b": "Backups manuais em drives externos.",
                "c": "Backups automáticos semanais em nuvem.",
                "d": "Estratégia de recuperação com testes regulares.",
                "e": "Sistema resiliente com IA para detecção e recuperação automática.",
            },
            {
                "ordem": 8,
                "enunciado": "Qual é o volume de dados gerenciados pela empresa?",
                "a": "Muito baixo; poucos registros manuais.",
                "b": "Moderado, gerenciável em planilhas.",
                "c": "Alto, exigindo bancos de dados dedicados.",
                "d": "Escala enterprise com ferramentas avançadas.",
                "e": "Big data otimizado com IA para processamento eficiente.",
            },
            {
                "ordem": 9,
                "enunciado": "Como sua empresa lida com dados sensíveis?",
                "a": "Sem proteção específica; expostos.",
                "b": "Senhas básicas para acesso.",
                "c": "Encriptação em repouso e transmissão.",
                "d": "Policies de anonimização e auditoria.",
                "e": "IA para detecção de riscos e proteção proativa.",
            },
            {
                "ordem": 10,
                "enunciado": "Qual é o investimento em ferramentas de dados?",
                "a": "Nenhum; dependemos de gratuitas.",
                "b": "Baixo, para ferramentas básicas.",
                "c": "Moderado, com foco em eficiência.",
                "d": "Alto, com ROI calculado.",
                "e": "Otimizado com IA para alocação baseada em necessidades.",
            },
        ],
    },
    {
        "pilar": PilarQuestionario.Pilar.ANALYTICS,
        "ordem_pilar": 3,
        "descricao": "Avalia relatórios, KPIs, uso de dashboards e capacidade de gerar ação.",
        "prefixo_codigo": "ANA",
        "perguntas": [
            {
                "ordem": 1,
                "enunciado": "Como sua empresa analisa dados de desempenho?",
                "a": "Não analisamos; relatórios manuais raros.",
                "b": "Análises básicas em planilhas.",
                "c": "Ferramentas como Google Analytics para métricas simples.",
                "d": "Dashboards interativos para análises profundas.",
                "e": "Analytics preditivo com IA para insights proativos.",
            },
            {
                "ordem": 2,
                "enunciado": "Qual é o frequência de geração de relatórios analíticos?",
                "a": "Nunca ou raramente.",
                "b": "Mensal, manualmente.",
                "c": "Semanal, com automação básica.",
                "d": "Diário, com integração de dados.",
                "e": "Em tempo real, impulsionado por IA.",
            },
            {
                "ordem": 3,
                "enunciado": "Como é o uso de métricas chave (KPIs)?",
                "a": "Sem KPIs definidos.",
                "b": "KPIs básicos monitorados manualmente.",
                "c": "KPIs rastreados em ferramentas dedicadas.",
                "d": "KPIs integrados a estratégias com alertas.",
                "e": "KPIs otimizados por IA com previsões.",
            },
            {
                "ordem": 4,
                "enunciado": "Qual é o nível de visualização de dados?",
                "a": "Sem visualizações; apenas textos.",
                "b": "Gráficos simples em planilhas.",
                "c": "Dashboards com gráficos interativos.",
                "d": "Visualizações avançadas com storytelling.",
                "e": "Visualizações com IA para insights automáticos.",
            },
            {
                "ordem": 5,
                "enunciado": "Como sua empresa lida com análise de tendências?",
                "a": "Não analisamos tendências.",
                "b": "Observações manuais passadas.",
                "c": "Ferramentas básicas para padrões históricos.",
                "d": "Análises estatísticas avançadas.",
                "e": "Modelos de IA para previsão de tendências.",
            },
            {
                "ordem": 6,
                "enunciado": "Qual é a integração de analytics com outros sistemas?",
                "a": "Isolado; sem integração.",
                "b": "Export manual para análise.",
                "c": "Integração básica via APIs.",
                "d": "Fluxos automatizados end-to-end.",
                "e": "Integração com IA para analytics em tempo real.",
            },
            {
                "ordem": 7,
                "enunciado": "Como é o treinamento em analytics para a equipe?",
                "a": "Nenhum; autoaprendizado.",
                "b": "Treinamentos básicos ocasionais.",
                "c": "Cursos regulares em ferramentas.",
                "d": "Certificações em análise de dados.",
                "e": "Programas com IA para aprendizado personalizado.",
            },
            {
                "ordem": 8,
                "enunciado": "Qual é o uso de analytics para otimização de processos?",
                "a": "Não usado para otimização.",
                "b": "Análises reativas para problemas.",
                "c": "Otimização baseada em dados históricos.",
                "d": "Análises prescritivas para melhorias.",
                "e": "Otimização preditiva com IA.",
            },
            {
                "ordem": 9,
                "enunciado": "Como sua empresa mede o impacto de analytics?",
                "a": "Não medimos.",
                "b": "Avaliações qualitativas.",
                "c": "Métricas simples de uso.",
                "d": "ROI calculado em projetos.",
                "e": "Análise contínua com IA.",
            },
            {
                "ordem": 10,
                "enunciado": "Qual é o escopo de analytics na empresa?",
                "a": "Limitado a uma área.",
                "b": "Em poucas áreas operacionais.",
                "c": "Em múltiplas áreas.",
                "d": "Empresa-wide com governança.",
                "e": "Holístico com IA para insights cross-funcionais.",
            },
        ],
    },
    {
        "pilar": PilarQuestionario.Pilar.AUTOMACOES,
        "ordem_pilar": 4,
        "descricao": "Avalia automações de processos, integrações, monitoramento e governança.",
        "prefixo_codigo": "AUT",
        "perguntas": [
            {
                "ordem": 1,
                "enunciado": "Qual é o nível de automação em processos repetitivos?",
                "a": "Tudo manual; sem automações.",
                "b": "Automações básicas como e-mails programados.",
                "c": "Ferramentas como Zapier para fluxos simples.",
                "d": "Automações integradas em sistemas core.",
                "e": "Automações inteligentes com IA para adaptação.",
            },
            {
                "ordem": 2,
                "enunciado": "Como é a automação de fluxos de trabalho?",
                "a": "Não há fluxos automatizados.",
                "b": "Automação manual em tarefas isoladas.",
                "c": "Workflows básicos em ferramentas.",
                "d": "Cadeias complexas de automação.",
                "e": "Workflows otimizados por IA.",
            },
            {
                "ordem": 3,
                "enunciado": "Qual é o uso de bots ou scripts para tarefas?",
                "a": "Nenhum uso.",
                "b": "Scripts simples criados manualmente.",
                "c": "Bots para atendimento básico.",
                "d": "Bots avançados integrados.",
                "e": "Bots com IA para interações dinâmicas.",
            },
            {
                "ordem": 4,
                "enunciado": "Como sua empresa monitora automações?",
                "a": "Sem monitoramento.",
                "b": "Verificações manuais.",
                "c": "Alertas básicos para falhas.",
                "d": "Dashboards para desempenho.",
                "e": "Monitoramento com IA para otimização.",
            },
            {
                "ordem": 5,
                "enunciado": "Qual é a integração de automações com dados?",
                "a": "Isoladas; sem dados.",
                "b": "Automações baseadas em inputs manuais.",
                "c": "Integração básica com bancos de dados.",
                "d": "Fluxos data-driven.",
                "e": "Automações preditivas com IA.",
            },
            {
                "ordem": 6,
                "enunciado": "Como é a escalabilidade das automações?",
                "a": "Não escaláveis.",
                "b": "Limitadas a pequenas tarefas.",
                "c": "Escaláveis para equipes médias.",
                "d": "Projetadas para crescimento.",
                "e": "Autoescaláveis com IA.",
            },
            {
                "ordem": 7,
                "enunciado": "Qual é o treinamento para criação de automações?",
                "a": "Nenhum.",
                "b": "Aprendizado informal.",
                "c": "Treinamentos básicos.",
                "d": "Programas avançados.",
                "e": "Ferramentas de low-code com IA.",
            },
            {
                "ordem": 8,
                "enunciado": "Como automações impactam a eficiência?",
                "a": "Sem impacto.",
                "b": "Redução mínima de tempo.",
                "c": "Economia moderada.",
                "d": "Otimização significativa.",
                "e": "Transformação com IA.",
            },
            {
                "ordem": 9,
                "enunciado": "Qual é a segurança em automações?",
                "a": "Sem segurança.",
                "b": "Controles básicos.",
                "c": "Autenticação integrada.",
                "d": "Auditorias regulares.",
                "e": "Segurança com IA para detecção.",
            },
            {
                "ordem": 10,
                "enunciado": "Qual é o escopo de automações na empresa?",
                "a": "Nenhuma área.",
                "b": "Uma ou duas áreas.",
                "c": "Múltiplas áreas.",
                "d": "Todo o negócio.",
                "e": "Ecossistema com IA.",
            },
        ],
    },
    {
        "pilar": PilarQuestionario.Pilar.INTELIGENCIA_ARTIFICIAL,
        "ordem_pilar": 5,
        "descricao": "Avalia aplicação, governança e integração de IA no negócio.",
        "prefixo_codigo": "IA",
        "perguntas": [
            {
                "ordem": 1,
                "enunciado": "Qual é o uso de IA em operações diárias?",
                "a": "Nenhum uso de IA.",
                "b": "Ferramentas básicas como chatbots gratuitos.",
                "c": "IA para tarefas específicas, como recomendações.",
                "d": "Integração de IA em processos core.",
                "e": "IA estratégica para inovação contínua.",
            },
            {
                "ordem": 2,
                "enunciado": "Como sua empresa adota modelos de machine learning?",
                "a": "Não adotamos.",
                "b": "Experimentos isolados.",
                "c": "Modelos pré-treinados para análise.",
                "d": "Modelos customizados.",
                "e": "Modelos autoaprendentes.",
            },
            {
                "ordem": 3,
                "enunciado": "Qual é o nível de IA em análise preditiva?",
                "a": "Sem predições.",
                "b": "Predições manuais baseadas em histórico.",
                "c": "Ferramentas básicas de forecasting.",
                "d": "Modelos avançados de ML.",
                "e": "IA generativa para cenários.",
            },
            {
                "ordem": 4,
                "enunciado": "Como é a ética e viés em IA?",
                "a": "Não considerado.",
                "b": "Políticas básicas.",
                "c": "Auditorias ocasionais.",
                "d": "Governança ética integrada.",
                "e": "IA para detecção de viés.",
            },
            {
                "ordem": 5,
                "enunciado": "Qual é o investimento em IA?",
                "a": "Nenhum.",
                "b": "Baixo, para testes.",
                "c": "Moderado, com projetos.",
                "d": "Alto, com ROI.",
                "e": "Estratégico com parcerias.",
            },
            {
                "ordem": 6,
                "enunciado": "Como a equipe é treinada em IA?",
                "a": "Sem treinamento.",
                "b": "Cursos online básicos.",
                "c": "Workshops regulares.",
                "d": "Certificações avançadas.",
                "e": "Programas personalizados por IA.",
            },
            {
                "ordem": 7,
                "enunciado": "Qual é a integração de IA com outros sistemas?",
                "a": "Isolada.",
                "b": "Integrações manuais.",
                "c": "APIs básicas.",
                "d": "Ecossistema integrado.",
                "e": "Hiperautomação com IA.",
            },
            {
                "ordem": 8,
                "enunciado": "Como IA impacta a inovação?",
                "a": "Sem impacto.",
                "b": "Ideias ocasionais.",
                "c": "Projetos pilotos.",
                "d": "Inovação contínua.",
                "e": "Cultura de IA-driven.",
            },
            {
                "ordem": 9,
                "enunciado": "Qual é o uso de IA generativa (como ChatGPT)?",
                "a": "Nenhum.",
                "b": "Uso pessoal ocasional.",
                "c": "Integrada para conteúdo.",
                "d": "Customizada para negócios.",
                "e": "Avançada para automação criativa.",
            },
            {
                "ordem": 10,
                "enunciado": "Qual é a visão futura para IA na empresa?",
                "a": "Sem planos.",
                "b": "Exploração inicial.",
                "c": "Adoção gradual.",
                "d": "Estratégia definida.",
                "e": "Liderança em IA.",
            },
        ],
    },
]


def _codigo(prefixo: str, ordem: int) -> str:
    # Ex.: TEC_01, DAD_10, IA_03
    return f"{prefixo}_{ordem:02d}"


class Command(BaseCommand):
    help = "Popula pilares e perguntas (A-E) dos questionários de maturidade."

    @transaction.atomic
    def handle(self, *args, **options):
        criados_pilares = 0
        criadas_perguntas = 0
        atualizadas_perguntas = 0

        for q in QUESTIONARIOS:
            pilar_obj, pilar_criado = PilarQuestionario.objects.update_or_create(
                pilar=q["pilar"],
                defaults={
                    "descricao": q.get("descricao", ""),
                    "ordem": q.get("ordem_pilar", 1),
                    "ativo": True,
                },
            )
            if pilar_criado:
                criados_pilares += 1

            prefixo = q["prefixo_codigo"]
            for p in q["perguntas"]:
                codigo = _codigo(prefixo, p["ordem"])

                pergunta_obj, pergunta_criada = PerguntaQuestionario.objects.update_or_create(
                    codigo=codigo,
                    defaults={
                        "pilar": pilar_obj,
                        "ordem": p["ordem"],
                        "enunciado": p["enunciado"],
                        "alternativa_a": p["a"],
                        "alternativa_b": p["b"],
                        "alternativa_c": p["c"],
                        "alternativa_d": p["d"],
                        "alternativa_e": p["e"],
                        "ativo": True,
                    },
                )

                if pergunta_criada:
                    criadas_perguntas += 1
                else:
                    atualizadas_perguntas += 1

        self.stdout.write(self.style.SUCCESS(
            f"Concluído. Pilares criados: {criados_pilares}. "
            f"Perguntas criadas: {criadas_perguntas}. Perguntas atualizadas: {atualizadas_perguntas}."
        ))
