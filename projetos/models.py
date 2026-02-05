from django.db import models
from perfil.models import PerfilEmpresa

class Projeto(models.Model):
    perfil = models.ForeignKey(
        PerfilEmpresa, 
        on_delete=models.CASCADE, 
        related_name='projetos_recomendados'
    )
    area = models.CharField("Área", max_length=100)
    nome_projeto = models.CharField("Nome do Projeto", max_length=200)
    descricao = models.TextField("Descrição")
    segmento = models.CharField("Segmento", max_length=200)
    
    objetivo_principal = models.TextField("Objetivo Principal")
    objetivos_secundarios = models.JSONField("Objetivos Secundários", default=list)
    
    problema = models.TextField("Problema")
    causa_raiz = models.TextField("Causa Raiz")
    impacto_do_problema = models.TextField("Impacto do Problema")
    publico_impactado = models.TextField("Público Impactado")
    
    solucao = models.TextField("Solução")
    beneficios = models.JSONField("Benefícios", default=list)
    
    impacto_operacional = models.TextField("Impacto Operacional")
    impacto_financeiro = models.TextField("Impacto Financeiro")
    impacto_tempo = models.TextField("Impacto Tempo")
    
    indicadores_chave = models.JSONField("Indicadores Chave", default=list)
    fases_projeto = models.JSONField("Fases do Projeto", default=list)
    entregaveis = models.JSONField("Entregáveis", default=list)
    
    riscos = models.JSONField("Riscos", default=list)
    mitigacao_riscos = models.JSONField("Mitigação de Riscos", default=list)
    
    dados_necessarios = models.JSONField("Dados Necessários", default=list)
    vantagem_competitiva = models.TextField("Vantagem Competitiva")
    casos_uso_futuros = models.JSONField("Casos de Uso Futuros", default=list)
    
    # Novos campos de prazo e preço (alterados para string para suportar formatos da IA)
    prazo_minimo = models.CharField("Prazo Mínimo", max_length=100, default="")
    prazo_maximo = models.CharField("Prazo Máximo", max_length=100, default="")
    prazo_estimado = models.CharField("Prazo Estimado", max_length=100, default="")
    
    preco_minimo = models.CharField("Preço Mínimo", max_length=100, default="")
    preco_maximo = models.CharField("Preço Máximo", max_length=100, default="")
    preco_estimado = models.CharField("Preço Estimado", max_length=100, default="")
    
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Projeto Recomendado"
        verbose_name_plural = "Projetos Recomendados"
        ordering = ['area', 'nome_projeto']

    def __str__(self):
        return f"{self.nome_projeto} ({self.area})"
