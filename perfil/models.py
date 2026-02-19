from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class PerfilEmpresa(models.Model):
    """
    Modelo para armazenar o PERFIL (contexto estável) da empresa.
    Nomes de tabela e atributos em português, com escolhas (choices) padronizadas.
    """

    # -------------------------
    # Choices / enums
    # -------------------------
    class Setor(models.TextChoices):
        AGRO = "AGRO", "Agronegócio / Pecuária / Rural"
        ALIMENTOS = "ALIMENTOS", "Alimentos / Bebidas"
        PET = "PET", "Animais de Estimação / Mundo Pet"
        ARQUITETURA = "ARQUITETURA", "Arquitetura / Design de Interiores"
        ARTISTICO = "ARTISTICO", "Artístico / Musical / Produtora"
        AUTOMOBILISTICO = "AUTOMOBILISTICO", "Automobilístico"
        COMBUSTIVEIS = "COMBUSTIVEIS", "Combustíveis / Energia"
        CONSTRUCAO = "CONSTRUCAO", "Construção Civil / Incorporadora"
        CONTABILIDADE = "CONTABILIDADE", "Contabilidade"
        BELEZA = "BELEZA", "Cosméticos / Beleza / Estética"
        DIVERSOS = "DIVERSOS", "Diversos"
        ECOMMERCE = "ECOMMERCE", "E-commerce / Marketplace"
        EDUCACAO = "EDUCACAO", "Educação"
        ENERGIA_SOLAR = "ENERGIA_SOLAR", "Energia Solar"
        ENGENHARIA = "ENGENHARIA", "Engenharia / Infraestrutura"
        ELETRO = "ELETRO", "Equipamentos Eletrodomésticos / Eletrônicos"
        ESPORTE = "ESPORTE", "Esporte / Lazer / Jogos / Bem-estar"
        EVENTOS = "EVENTOS", "Eventos"
        FARMACEUTICA = "FARMACEUTICA", "Farmacêutica / Drogarias"
        GESTAO = "GESTAO", "Gestão / Administração / Consultorias"
        IMOBILIARIA = "IMOBILIARIA", "Imobiliária"
        IMPORT_EXPORT = "IMPORT_EXPORT", "Importação e Exportação"
        INVESTIMENTO = "INVESTIMENTO", "Investimento / Financeiro"
        JURIDICO = "JURIDICO", "Jurídico"
        LOGISTICA = "LOGISTICA", "Logística / Distribuidora / Transporte de carga"
        MARKETING = "MARKETING", "Marketing"
        MEDICINA_DIAG = "MEDICINA_DIAG", "Medicina Diagnóstica / Laboratórios"
        METALURGIA = "METALURGIA", "Metalúrgica / Mineração"
        MAQUINAS = "MAQUINAS", "Máquinas e Equipamentos"
        MEDICOS = "MEDICOS", "Médicos / Dentistas / Clínicas / Institutos Médicos"
        MOVEIS = "MOVEIS", "Móveis e Decoração"
        PAPEL = "PAPEL", "Papel / Celulose / Plástico"
        HOSPITALAR = "HOSPITALAR", "Produtos e equipamentos para hospitais e clínicas"
        PUBLICIDADE = "PUBLICIDADE", "Publicidade / Propaganda"
        PUBLICO = "PUBLICO", "Público / Governamental"
        QUIMICA = "QUIMICA", "Química"
        RECICLAGEM = "RECICLAGEM", "Reciclagem e Sustentabilidade"
        ATACADO_VAREJO = "ATACADO_VAREJO", "Redes de Atacado ou Varejo"
        TELECOM = "TELECOM", "Redes e Telecomunicações"
        RH = "RH", "RH / Recrutamento e Seleção"
        TI = "TI", "SaaS / Plataformas / Softwarehouse / TI"
        SEGUROS = "SEGUROS", "Seguros"
        SEGURANCA_LIMPEZA = "SEGURANCA_LIMPEZA", "Serviços de Segurança / Limpeza"
        TRANSPORTE = "TRANSPORTE", "Transporte e Mobilidade"
        TURISMO = "TURISMO", "Turismo / Hotelaria"
        MODA = "MODA", "Vestuário & Moda"
        COMUNICACAO = "COMUNICACAO", "Veículos de comunicação"
        OUTRO = "OUTRO", "Outro (descreva)"

    class Cargo(models.TextChoices):
        SOCIO = "SOCIO", "Sócio ou Fundador"
        PRESIDENTE = "PRESIDENTE", "Presidente ou CEO"
        VP = "VP", "Vice-presidente ou C-Level"
        DIRETOR = "DIRETOR", "Diretor"
        GERENTE = "GERENTE", "Gerente"
        COORDENADOR = "COORDENADOR", "Coordenador"
        SUPERVISOR = "SUPERVISOR", "Supervisor"
        ANALISTA = "ANALISTA", "Analista"
        OUTRO = "OUTRO", "Outro (descreva)"

    class FaseNegocio(models.TextChoices):
        IDEACAO = "IDEACAO", "Ideação (pré-operação)"
        OPERACAO_INICIAL = "OPERACAO_INICIAL", "Operação inicial"
        CRESCIMENTO = "CRESCIMENTO", "Em crescimento"
        ESTAVEL = "ESTAVEL", "Estável"
        DIFICULDADE = "DIFICULDADE", "Em dificuldade"

    class FaixaAnoFundacao(models.TextChoices):
        ANTES_2010 = "ANTES_2010", "Antes de 2010"
        A2010_2015 = "2010_2015", "2010–2015"
        A2016_2020 = "2016_2020", "2016–2020"
        A2021_2025 = "2021_2025", "2021–2025"
        A2026_MAIS = "2026_MAIS", "2026 ou posterior"

    class FaixaFuncionarios(models.TextChoices):
        UM = "UM", "1 (apenas o(a) fundador(a))"
        DOIS_A_NOVE = "2_9", "2–9"
        DEZ_A_VINTE_CINCO = "10_25", "10–25"
        VINTE_SEIS_A_CEM = "26_100", "26–100"
        CEM_MAIS = "100_MAIS", "100+"

    class TomadorDecisao(models.TextChoices):
        DONO = "DONO", "Dono(a)"
        SOCIOS = "SOCIOS", "Sócios"
        GESTORES = "GESTORES", "Gestor(es)"
        TIME_EXECUTIVO = "TIME_EXECUTIVO", "Time executivo"

    class ResponsavelTecnologia(models.TextChoices):
        NINGUEM = "NINGUEM", "Não há responsável definido"
        DONO = "DONO", "Dono(a)"
        ADMINISTRATIVO = "ADMINISTRATIVO", "Pessoa administrativa"
        TI_INTERNO = "TI_INTERNO", "TI interno"
        FORNECEDOR = "FORNECEDOR", "Fornecedor/parceiro externo"

    class RegimeTributario(models.TextChoices):
        MEI = "MEI", "MEI"
        SIMPLES = "SIMPLES", "Simples Nacional"
        LUCRO_PRESUMIDO = "LUCRO_PRESUMIDO", "Lucro Presumido"
        LUCRO_REAL = "LUCRO_REAL", "Lucro Real"

    class FaixaFaturamentoAnual(models.TextChoices):
        NAO_FATURAMOS = "NAO_FATURAMOS", "Ainda não faturamos"
        ATE_100K = "ATE_100K", "Até R$ 100 mil"
        R100K_1M = "100K_1M", "R$ 100 mil – R$ 1 milhão"
        R1M_5M = "1M_5M", "R$ 1 milhão – R$ 5 milhões"
        R5M_25M = "5M_25M", "R$ 5 milhões – R$ 25 milhões"
        R25M_100M = "25M_100M", "R$ 25 milhões – R$ 100 milhões"
        ACIMA_100M = "ACIMA_100M", "Acima de R$ 100 milhões"

    class OrcamentoAnualTI(models.TextChoices):
        NAO_DEFINIDO = "NAO_DEFINIDO", "Não possuo / não definido"
        ATE_10K = "ATE_10K", "Até R$ 10 mil"
        R10K_50K = "10K_50K", "R$ 10 mil – R$ 50 mil"
        R50K_100K = "50K_100K", "R$ 50 mil – R$ 100 mil"
        R100K_250K = "100K_250K", "R$ 100 mil – R$ 250 mil"
        R250K_1M = "250K_1M", "R$ 250 mil – R$ 1 milhão"
        ACIMA_1M = "ACIMA_1M", "Acima de R$ 1 milhão"

    class ModeloNegocio(models.TextChoices):
        B2B = "B2B", "B2B (vende para empresas)"
        B2C = "B2C", "B2C (vende para consumidor final)"
        B2B2C = "B2B2C", "B2B2C"
        B2G = "B2G", "B2G"
        D2C = "D2C", "D2C"
        MARKETPLACE = "MARKETPLACE", "Marketplace"
        HIBRIDO = "HIBRIDO", "Híbrido"

    class TipoReceitaPredominante(models.TextChoices):
        VENDA_UNICA = "VENDA_UNICA", "Venda única (transacional)"
        RECORRENCIA = "RECORRENCIA", "Recorrência / assinatura"
        SERVICOS = "SERVICOS", "Serviços por hora ou projeto"
        COMISSOES = "COMISSOES", "Comissões"
        MIX = "MIX", "Mix de modelos"

    class TicketMedio(models.TextChoices):
        ATE_100 = "ATE_100", "Até R$ 100"
        R101_500 = "101_500", "R$ 101 – R$ 500"
        R501_2000 = "501_2000", "R$ 501 – R$ 2.000"
        R2000_10K = "2000_10K", "R$ 2.000 – R$ 10.000"
        ACIMA_10K = "ACIMA_10K", "Acima de R$ 10.000"

    class CanalVendas(models.TextChoices):
        LOJA_FISICA = "LOJA_FISICA", "Loja física"
        ECOMMERCE = "ECOMMERCE", "E-commerce / site próprio"
        WHATSAPP = "WHATSAPP", "WhatsApp"
        REDES_SOCIAIS = "REDES_SOCIAIS", "Redes sociais"
        VENDEDORES_EXTERNOS = "VENDEDORES_EXTERNOS", "Vendedores externos / representantes"
        MARKETPLACES = "MARKETPLACES", "Marketplaces"

    class EstruturaOperacional(models.TextChoices):
        PRESENCIAL = "PRESENCIAL", "100% presencial"
        ONLINE = "ONLINE", "100% online"
        HIBRIDA = "HIBRIDA", "Híbrida"
        MULTILOJA = "MULTILOJA", "Multiloja / múltiplas unidades"

    class QuantidadeUnidades(models.TextChoices):
        UMA = "UMA", "1"
        DUAS_A_CINCO = "2_5", "2–5"
        SEIS_A_VINTE = "6_20", "6–20"
        VINTE_MAIS = "20_MAIS", "20+"

    class AbrangenciaGeografica(models.TextChoices):
        LOCAL = "LOCAL", "Local / bairro"
        CIDADE = "CIDADE", "Cidade"
        REGIONAL = "REGIONAL", "Regional"
        NACIONAL = "NACIONAL", "Nacional"
        INTERNACIONAL = "INTERNACIONAL", "Internacional"

    class Sazonalidade(models.TextChoices):
        BAIXA = "BAIXA", "Baixa"
        MODERADA = "MODERADA", "Moderada"
        ALTA = "ALTA", "Alta"

    class EquipeTI(models.TextChoices):
        NAO = "NAO", "Não"
        UMA_PESSOA = "UMA_PESSOA", "Sim, 1 pessoa"
        EQUIPE_DEDICADA = "EQUIPE_DEDICADA", "Sim, equipe dedicada"

    class AlfabetizacaoDigital(models.TextChoices):
        BAIXA = "BAIXA", "Baixo – dificuldade com novas ferramentas"
        MEDIA = "MEDIA", "Médio – utilizam o básico bem"
        ALTA = "ALTA", "Alto – aprendem rápido e buscam inovação"

    class FerramentasGestao(models.TextChoices):
        NENHUMA = "NENHUMA", "Nenhuma"
        PAPEL = "PAPEL", "Papel / controles manuais"
        PLANILHAS = "PLANILHAS", "Planilhas (Excel / Google Sheets)"
        SOFTWARE_GENERALISTA = "SOFTWARE_GENERALISTA", "Software generalista (ERP, financeiro etc.)"
        SOFTWARE_SETOR = "SOFTWARE_SETOR", "Software específico do setor"
        LEGADO = "LEGADO", "Sistema próprio / legado"

    class ResidenciaDados(models.TextChoices):
        NAO_ARMAZENAMOS = "NAO_ARMAZENAMOS", "Não armazenamos dados"
        PAPEL = "PAPEL", "Papel / caderno"
        PLANILHAS = "PLANILHAS", "Planilhas (Excel / Google)"
        BANCO_DADOS = "BANCO_DADOS", "Banco de dados estruturado"
        DISPERSOS = "DISPERSOS", "Dispersos em várias ferramentas"

    class PrioridadeEstrategica(models.TextChoices):
        CUSTOS = "CUSTOS", "Reduzir custos operacionais"
        VENDAS = "VENDAS", "Aumentar volume de vendas"
        EXPERIENCIA_CLIENTE = "EXPERIENCIA_CLIENTE", "Melhorar a experiência do cliente"
        ORGANIZACAO = "ORGANIZACAO", "Organizar processos e gestão"
        EFICIENCIA = "EFICIENCIA", "Aumentar eficiência operacional"

    class ConformidadeLGPD(models.TextChoices):
        NAO_IMPLEMENTADO = "NAO_IMPLEMENTADO", "Não implementado"
        EM_PROCESSO = "EM_PROCESSO", "Em processo de adequação"
        CONFORME = "CONFORME", "Totalmente conforme"
        NAO_SEI = "NAO_SEI", "Não sei informar"

    class PreferenciaRecomendacoes(models.TextChoices):
        DIRETO = "DIRETO", "Mais direto e objetivo"
        DETALHADO = "DETALHADO", "Mais detalhado e explicativo"
        EXECUTIVO = "EXECUTIVO", "Visão executiva (decisão)"
        OPERACIONAL = "OPERACIONAL", "Visão operacional (execução)"

    # -------------------------
    # Campos (perfil)
    # -------------------------
    # Identificação
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="perfil_empresa",
        verbose_name="Usuário",
    )
    nome_empresa = models.CharField("Nome da empresa", max_length=200, blank=True)
    setor_atuacao = models.CharField(
        "Setor de atuação",
        max_length=50,
        choices=Setor.choices,
    )
    cargo = models.CharField(
        "Cargo",
        max_length=50,
        choices=Cargo.choices,
        blank=True,
    )
    segmento_especifico = models.CharField(
        "Segmento específico",
        max_length=160,
        help_text="Lista dinâmica com base no setor selecionado.",
    )

    # Estrutura e estágio
    fase_negocio = models.CharField("Fase do negócio", max_length=24, choices=FaseNegocio.choices, blank=True)
    faixa_ano_fundacao = models.CharField(
        "Ano de fundação (faixa)",
        max_length=16,
        choices=FaixaAnoFundacao.choices,
        blank=True,
    )
    faixa_funcionarios = models.CharField("Número de funcionários", max_length=16, choices=FaixaFuncionarios.choices, blank=True)

    # Estrutura societária e decisão
    decisao_estrategica = models.CharField(
        "Quem toma as decisões estratégicas?",
        max_length=20,
        choices=TomadorDecisao.choices,
        blank=True,
    )
    responsavel_tecnologia_processos = models.CharField(
        "Responsável por tecnologia e processos",
        max_length=24,
        choices=ResponsavelTecnologia.choices,
        blank=True,
    )

    # Financeiro
    regime_tributario = models.CharField("Regime tributário", max_length=20, choices=RegimeTributario.choices, blank=True)
    faturamento_anual_aproximado = models.CharField(
        "Faturamento anual aproximado",
        max_length=20,
        choices=FaixaFaturamentoAnual.choices,
        blank=True,
    )
    orcamento_anual_ti = models.CharField(
        "Orçamento anual disponível para TI / tecnologia",
        max_length=20,
        choices=OrcamentoAnualTI.choices,
        blank=True,
    )

    # Modelo de negócio e vendas
    modelo_negocio = models.CharField("Modelo de negócio", max_length=16, choices=ModeloNegocio.choices, blank=True)
    tipo_receita_predominante = models.CharField(
        "Tipo de receita predominante",
        max_length=20,
        choices=TipoReceitaPredominante.choices,
        blank=True,
    )
    ticket_medio_venda = models.CharField("Ticket médio de venda", max_length=16, choices=TicketMedio.choices, blank=True)
    principal_canal_vendas = models.CharField(
        "Principal canal de vendas",
        max_length=24,
        choices=CanalVendas.choices,
        blank=True,
    )

    # Escala e operação
    estrutura_operacional = models.CharField(
        "Estrutura operacional",
        max_length=16,
        choices=EstruturaOperacional.choices,
        blank=True,
    )
    quantidade_unidades = models.CharField(
        "Quantidade de unidades / filiais",
        max_length=16,
        choices=QuantidadeUnidades.choices,
        blank=True,
    )
    abrangencia_geografica = models.CharField(
        "Abrangência geográfica",
        max_length=16,
        choices=AbrangenciaGeografica.choices,
        blank=True,
    )
    sazonalidade_negocio = models.CharField(
        "Sazonalidade do negócio",
        max_length=12,
        choices=Sazonalidade.choices,
        blank=True,
    )
    meses_pico = models.CharField(
        "Meses de pico (opcional)",
        max_length=80,
        blank=True,
        help_text="Ex.: mar, abr, nov. Preencher apenas se sazonalidade for moderada/alta.",
    )

    # Localização
    pais = models.CharField("País", max_length=60, blank=True)
    estado = models.CharField("Estado", max_length=60, blank=True)
    cidade = models.CharField("Cidade", max_length=80, blank=True)

    # Tecnologia e dados (percepção / contexto)
    possui_equipe_ti_dados = models.CharField(
        "Possui equipe de TI / dados?",
        max_length=16,
        choices=EquipeTI.choices,
        blank=True,
    )
    alfabetizacao_digital_equipe = models.CharField(
        "Nível de alfabetização digital da equipe",
        max_length=12,
        choices=AlfabetizacaoDigital.choices,
        blank=True,
    )
    ferramentas_gestao = models.CharField(
        "Ferramentas de gestão utilizadas atualmente",
        max_length=24,
        choices=FerramentasGestao.choices,
        blank=True,
    )
    residencia_dados = models.CharField(
        "Onde os dados da empresa residem hoje?",
        max_length=20,
        choices=ResidenciaDados.choices,
        blank=True,
    )

    # Estratégia e conformidade
    prioridade_estrategica_ano = models.CharField(
        "Prioridade estratégica para este ano",
        max_length=24,
        choices=PrioridadeEstrategica.choices,
        blank=True,
    )
    conformidade_lgpd = models.CharField(
        "Nível de conformidade com LGPD",
        max_length=20,
        choices=ConformidadeLGPD.choices,
        blank=True,
    )

    # Preferências
    preferencia_entrega_recomendacoes = models.CharField(
        "Como prefere receber as recomendações?",
        max_length=16,
        choices=PreferenciaRecomendacoes.choices,
        blank=True,
    )

    # Metadados
    criado_em = models.DateTimeField("Criado em", auto_now_add=True)
    atualizado_em = models.DateTimeField("Atualizado em", auto_now=True)

    def __str__(self) -> str:
        return self.nome_empresa

    class Meta:
        verbose_name = "Perfil da Empresa"
        verbose_name_plural = "Perfis das Empresas"
        db_table = "perfil_empresa"


class CanalAquisicaoCliente(models.Model):
    """
    Tabela de apoio para múltipla escolha de canais de aquisição.
    (Permite evoluir opções sem migrations de choices.)
    """

    nome = models.CharField("Nome", max_length=80, unique=True)

    def __str__(self) -> str:
        return self.nome

    class Meta:
        verbose_name = "Canal de Aquisição"
        verbose_name_plural = "Canais de Aquisição"
        db_table = "canal_aquisicao_cliente"


class SistemaUtilizado(models.Model):
    """
    Tabela de apoio para múltipla escolha de sistemas utilizados.
    (Permite evoluir opções sem migrations de choices.)
    """

    nome = models.CharField("Nome", max_length=80, unique=True)

    def __str__(self) -> str:
        return self.nome

    class Meta:
        verbose_name = "Sistema Utilizado"
        verbose_name_plural = "Sistemas Utilizados"
        db_table = "sistema_utilizado"


class PerfilEmpresaCanaisAquisicao(models.Model):
    """
    Relação N:N explícita (com tabela em português) entre PerfilEmpresa e CanalAquisicaoCliente.
    """

    perfil_empresa = models.ForeignKey(
        PerfilEmpresa,
        on_delete=models.CASCADE,
        related_name="canais_aquisicao",
        verbose_name="Perfil da empresa",
    )
    canal_aquisicao = models.ForeignKey(
        CanalAquisicaoCliente,
        on_delete=models.PROTECT,
        related_name="perfis_empresas",
        verbose_name="Canal de aquisição",
    )

    class Meta:
        verbose_name = "Canal de aquisição do perfil"
        verbose_name_plural = "Canais de aquisição dos perfis"
        db_table = "perfil_empresa_canais_aquisicao"
        unique_together = ("perfil_empresa", "canal_aquisicao")


class PerfilEmpresaSistemasUtilizados(models.Model):
    """
    Relação N:N explícita (com tabela em português) entre PerfilEmpresa e SistemaUtilizado.
    Inclui o campo "outros" em texto livre no próprio PerfilEmpresa (abaixo),
    mas aqui você mantém o catálogo de sistemas e seleção múltipla.
    """

    perfil_empresa = models.ForeignKey(
        PerfilEmpresa,
        on_delete=models.CASCADE,
        related_name="sistemas_utilizados",
        verbose_name="Perfil da empresa",
    )
    sistema_utilizado = models.ForeignKey(
        SistemaUtilizado,
        on_delete=models.PROTECT,
        related_name="perfis_empresas",
        verbose_name="Sistema utilizado",
    )

    class Meta:
        verbose_name = "Sistema do perfil"
        verbose_name_plural = "Sistemas dos perfis"
        db_table = "perfil_empresa_sistemas_utilizados"
        unique_together = ("perfil_empresa", "sistema_utilizado")


# Campo "Outros (especifique)" para setores, cargos e sistemas.
PerfilEmpresa.add_to_class(
    "setor_outro",
    models.CharField(
        "Outro setor (especifique)",
        max_length=100,
        blank=True,
    ),
)
PerfilEmpresa.add_to_class(
    "cargo_outro",
    models.CharField(
        "Outro cargo (especifique)",
        max_length=100,
        blank=True,
    ),
)
PerfilEmpresa.add_to_class(
    "segmento_outro",
    models.CharField(
        "Outro segmento (especifique)",
        max_length=100,
        blank=True,
    ),
)
PerfilEmpresa.add_to_class(
    "sistemas_outros",
    models.CharField(
        "Outros sistemas (especifique)",
        max_length=160,
        blank=True,
        help_text="Preencha se marcou 'Outros' no questionário de sistemas.",
    ),
)

# Volume mensal aproximado: como o tipo muda por setor, guarde como descrição + faixa (flexível).
PerfilEmpresa.add_to_class(
    "tipo_volume_mensal",
    models.CharField(
        "Tipo de volume mensal (ex.: pedidos, atendimentos, propostas, NFs)",
        max_length=60,
        blank=True,
    ),
)
PerfilEmpresa.add_to_class(
    "faixa_volume_mensal",
    models.CharField(
        "Faixa de volume mensal",
        max_length=40,
        blank=True,
        help_text="Faixa numérica definida conforme o setor. Ex.: 0–100 / 101–500 / 501–2.000 / 2.000+",
    ),
)

# Objetivos principais (múltipla escolha/ranking): use um catálogo + relação N:N para não travar em choices.
class ObjetivoProximo12Meses(models.Model):
    nome = models.CharField("Nome", max_length=80, unique=True)

    def __str__(self) -> str:
        return self.nome

    class Meta:
        verbose_name = "Objetivo (12 meses)"
        verbose_name_plural = "Objetivos (12 meses)"
        db_table = "objetivo_proximo_12_meses"


class PerfilEmpresaObjetivos(models.Model):
    perfil_empresa = models.ForeignKey(
        PerfilEmpresa,
        on_delete=models.CASCADE,
        related_name="objetivos_12_meses",
        verbose_name="Perfil da empresa",
    )
    objetivo = models.ForeignKey(
        ObjetivoProximo12Meses,
        on_delete=models.PROTECT,
        related_name="perfis_empresas",
        verbose_name="Objetivo",
    )
    # Se você quiser "ranking", use prioridade 1..N (opcional)
    prioridade = models.PositiveSmallIntegerField(
        "Prioridade (opcional)",
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Use se o usuário ordenar objetivos. 1 = mais importante.",
    )

    class Meta:
        verbose_name = "Objetivo do perfil"
        verbose_name_plural = "Objetivos dos perfis"
        db_table = "perfil_empresa_objetivos"
        unique_together = ("perfil_empresa", "objetivo")
        ordering = ["prioridade", "id"]


# Restrições críticas (múltipla escolha): também como catálogo + relação N:N
class RestricaoCritica(models.Model):
    nome = models.CharField("Nome", max_length=80, unique=True)

    def __str__(self) -> str:
        return self.nome

    class Meta:
        verbose_name = "Restrição Crítica"
        verbose_name_plural = "Restrições Críticas"
        db_table = "restricao_critica"


class PerfilEmpresaRestricoes(models.Model):
    perfil_empresa = models.ForeignKey(
        PerfilEmpresa,
        on_delete=models.CASCADE,
        related_name="restricoes_criticas",
        verbose_name="Perfil da empresa",
    )
    restricao = models.ForeignKey(
        RestricaoCritica,
        on_delete=models.PROTECT,
        related_name="perfis_empresas",
        verbose_name="Restrição",
    )

    class Meta:
        verbose_name = "Restrição do perfil"
        verbose_name_plural = "Restrições dos perfis"
        db_table = "perfil_empresa_restricoes"
        unique_together = ("perfil_empresa", "restricao")
