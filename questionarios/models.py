# models.py
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class AvaliacaoMaturidade(models.Model):
    """
    Uma avaliação completa (5 questionários/pilares).
    Normalmente vinculada a um PerfilEmpresa (se você já tiver esse model).
    """

    class Estagio(models.TextChoices):
        INICIAL = "INICIAL", "Inicial"
        EM_EVOLUCAO = "EM_EVOLUCAO", "Em evolução"
        ESTRUTURADO = "ESTRUTURADO", "Estruturado"
        AVANCADO = "AVANCADO", "Avançado"

    # Se você tiver o model PerfilEmpresa (do perfil), mantenha.
    # Se não tiver, troque para um identificador (email, uuid, etc).
    perfil_empresa = models.ForeignKey(
        "perfil.PerfilEmpresa",
        on_delete=models.CASCADE,
        related_name="avaliacoes_maturidade",
        verbose_name="Perfil da empresa",
        null=True,
        blank=True,
    )

    titulo = models.CharField("Título", max_length=120, default="Avaliação de Maturidade")
    pontuacao_geral = models.DecimalField(
        "Pontuação geral (0-100)",
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    estagio_geral = models.CharField(
        "Estágio geral",
        max_length=20,
        choices=Estagio.choices,
        default=Estagio.INICIAL,
    )

    criado_em = models.DateTimeField("Criado em", auto_now_add=True)
    atualizado_em = models.DateTimeField("Atualizado em", auto_now=True)

    def calcular_resultados(self):
        """
        Calcula a média dos pilares e aplica as regras de coerência/pilar limitante.
        """
        from .models import PilarQuestionario
        respostas = self.respostas_pilares.all()
        if not respostas:
            return

        total_pilares = PilarQuestionario.objects.filter(ativo=True).count() or 5
        soma = sum([r.pontuacao_pilar for r in respostas])
        media = soma / total_pilares
        
        # Regra de pilar limitante (Dados/Tecnologia <= 25 -> Final no máximo "Em evolução" (55))
        nota_dados = next((r.pontuacao_pilar for r in respostas if r.pilar.pilar == 'DADOS'), 0)
        nota_tec = next((r.pontuacao_pilar for r in respostas if r.pilar.pilar == 'TECNOLOGIA_SOFTWARE'), 0)
        
        if nota_dados <= 25 or nota_tec <= 25:
            if media > 55:
                media = 55
        
        # Se ambos forem muito baixos, trava no Inicial (25)
        if nota_dados <= 25 and nota_tec <= 25:
             if media > 25:
                 media = 25

        self.pontuacao_geral = media
        
        if media <= 25:
            self.estagio_geral = self.Estagio.INICIAL
        elif media <= 55:
            self.estagio_geral = self.Estagio.EM_EVOLUCAO
        elif media <= 80:
            self.estagio_geral = self.Estagio.ESTRUTURADO
        else:
            self.estagio_geral = self.Estagio.AVANCADO
            
        self.save()

    @property
    def get_score_color(self):
        if self.pontuacao_geral <= 25: return 'danger'
        if self.pontuacao_geral <= 55: return 'warning'
        if self.pontuacao_geral <= 80: return 'primary'
        return 'success'

    def __str__(self) -> str:
        return f"{self.titulo} - {self.id}"

    class Meta:
        verbose_name = "Avaliação de Maturidade"
        verbose_name_plural = "Avaliações de Maturidade"
        db_table = "avaliacao_maturidade"


class PilarQuestionario(models.Model):
    """
    Define os 5 pilares e seus questionários.
    """

    class Pilar(models.TextChoices):
        TECNOLOGIA_SOFTWARE = "TECNOLOGIA_SOFTWARE", "Tecnologia e Software"
        DADOS = "DADOS", "Dados"
        ANALYTICS = "ANALYTICS", "Analytics"
        AUTOMACOES = "AUTOMACOES", "Automações"
        INTELIGENCIA_ARTIFICIAL = "INTELIGENCIA_ARTIFICIAL", "Inteligência Artificial"

    pilar = models.CharField("Pilar", max_length=40, choices=Pilar.choices, unique=True)
    descricao = models.CharField("Descrição", max_length=180, blank=True)
    ordem = models.PositiveSmallIntegerField("Ordem", default=1, validators=[MinValueValidator(1), MaxValueValidator(50)])
    ativo = models.BooleanField("Ativo", default=True)

    def __str__(self) -> str:
        return self.get_pilar_display()

    class Meta:
        verbose_name = "Pilar do Questionário"
        verbose_name_plural = "Pilares dos Questionários"
        db_table = "pilar_questionario"
        ordering = ["ordem"]


class PerguntaQuestionario(models.Model):
    """
    Perguntas (10 por pilar, mas deixei flexível).
    As alternativas A-E são textos armazenados aqui (mais simples para Admin).
    """

    class TipoResposta(models.TextChoices):
        MULTIPLA_ESCOLHA_A_E = "MULTIPLA_ESCOLHA_A_E", "Múltipla escolha (A-E)"

    pilar = models.ForeignKey(
        PilarQuestionario,
        on_delete=models.CASCADE,
        related_name="perguntas",
        verbose_name="Pilar",
    )
    codigo = models.CharField(
        "Código",
        max_length=40,
        help_text="Ex.: DADOS_01, IA_07. Útil para versionamento e rastreio.",
        unique=True,
    )
    ordem = models.PositiveSmallIntegerField("Ordem", default=1, validators=[MinValueValidator(1), MaxValueValidator(100)])
    enunciado = models.TextField("Enunciado")
    tipo_resposta = models.CharField(
        "Tipo de resposta",
        max_length=32,
        choices=TipoResposta.choices,
        default=TipoResposta.MULTIPLA_ESCOLHA_A_E,
    )

    alternativa_a = models.CharField("Alternativa A", max_length=240)
    alternativa_b = models.CharField("Alternativa B", max_length=240)
    alternativa_c = models.CharField("Alternativa C", max_length=240)
    alternativa_d = models.CharField("Alternativa D", max_length=240)
    alternativa_e = models.CharField("Alternativa E", max_length=240)

    ativo = models.BooleanField("Ativo", default=True)

    criado_em = models.DateTimeField("Criado em", auto_now_add=True)
    atualizado_em = models.DateTimeField("Atualizado em", auto_now=True)

    def __str__(self) -> str:
        return f"{self.codigo} - {self.enunciado[:60]}"

    class Meta:
        verbose_name = "Pergunta do Questionário"
        verbose_name_plural = "Perguntas do Questionário"
        db_table = "pergunta_questionario"
        ordering = ["pilar__ordem", "ordem"]


class RespostaQuestionario(models.Model):
    """
    Resposta de um usuário/empresa para um pilar específico dentro de uma AvaliacaoMaturidade.
    Guarda score e estágio do pilar (calculados pelo backend).
    """

    class Estagio(models.TextChoices):
        INICIAL = "INICIAL", "Inicial"
        EM_EVOLUCAO = "EM_EVOLUCAO", "Em evolução"
        ESTRUTURADO = "ESTRUTURADO", "Estruturado"
        AVANCADO = "AVANCADO", "Avançado"

    avaliacao = models.ForeignKey(
        AvaliacaoMaturidade,
        on_delete=models.CASCADE,
        related_name="respostas_pilares",
        verbose_name="Avaliação",
    )
    pilar = models.ForeignKey(
        PilarQuestionario,
        on_delete=models.PROTECT,
        related_name="respostas",
        verbose_name="Pilar",
    )

    pontuacao_pilar = models.DecimalField(
        "Pontuação do pilar (0-100)",
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    estagio_pilar = models.CharField(
        "Estágio do pilar",
        max_length=20,
        choices=Estagio.choices,
        default=Estagio.INICIAL,
    )

    criado_em = models.DateTimeField("Criado em", auto_now_add=True)
    atualizado_em = models.DateTimeField("Atualizado em", auto_now=True)

    def save(self, *args, **kwargs):
        """
        Aplica regra de coerência: IA capada se Dados for baixo.
        """
        if self.pilar.pilar == 'INTELIGENCIA_ARTIFICIAL':
            try:
                # Busca resposta de dados da mesma avaliação
                resp_dados = RespostaQuestionario.objects.filter(
                    avaliacao=self.avaliacao, 
                    pilar__pilar='DADOS'
                ).first()
                
                # Se Dados <= 55 (Em evolução), IA máxima = 80 (Estruturado)
                if resp_dados and resp_dados.pontuacao_pilar <= 55 and self.pontuacao_pilar > 80:
                    self.pontuacao_pilar = 80
                    self.estagio_pilar = self.Estagio.ESTRUTURADO
            except Exception:
                pass
        
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.avaliacao_id} - {self.pilar.get_pilar_display()}"

    class Meta:
        verbose_name = "Resposta do Pilar"
        verbose_name_plural = "Respostas dos Pilares"
        db_table = "resposta_questionario"
        unique_together = ("avaliacao", "pilar")
        ordering = ["pilar__ordem"]


class RespostaPergunta(models.Model):
    """
    Resposta para uma pergunta específica (A-E).
    Armazena letra escolhida e pontuação (0/25/50/75/100) para auditoria e recalcular facilmente.
    """

    class Alternativa(models.TextChoices):
        A = "a", "a"
        B = "b", "b"
        C = "c", "c"
        D = "d", "d"
        E = "e", "e"

    resposta_questionario = models.ForeignKey(
        RespostaQuestionario,
        on_delete=models.CASCADE,
        related_name="respostas_perguntas",
        verbose_name="Resposta do pilar",
    )
    pergunta = models.ForeignKey(
        PerguntaQuestionario,
        on_delete=models.PROTECT,
        related_name="respostas",
        verbose_name="Pergunta",
    )

    alternativa_escolhida = models.CharField(
        "Alternativa escolhida",
        max_length=1,
        choices=Alternativa.choices,
    )
    pontuacao = models.PositiveSmallIntegerField(
        "Pontuação",
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Sugestão: a=0, b=25, c=50, d=75, e=100",
    )

    respondido_em = models.DateTimeField("Respondido em", auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.pergunta.codigo} -> {self.alternativa_escolhida}"

    class Meta:
        verbose_name = "Resposta da Pergunta"
        verbose_name_plural = "Respostas das Perguntas"
        db_table = "resposta_pergunta"
        unique_together = ("resposta_questionario", "pergunta")
        ordering = ["pergunta__pilar__ordem", "pergunta__ordem"]
