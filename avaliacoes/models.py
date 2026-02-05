from django.db import models
from projetos.models import Projeto
from perfil.models import PerfilEmpresa

class AvaliacaoProjeto(models.Model):
    class NivelInteresse(models.TextChoices):
        ALTO = 'ALTO', 'Alto Interesse - Prioridade'
        MEDIO = 'MEDIO', 'Médio Interesse - Roadmap'
        BAIXO = 'BAIXO', 'Baixo Interesse - Backlog'
        DESCARTADO = 'DESCARTADO', 'Não tenho interesse'
        JAEXISTE = 'JAEXISTE', 'Já possuo implementado'

    projeto = models.ForeignKey(Projeto, on_delete=models.CASCADE, related_name='avaliacoes')
    perfil = models.ForeignKey(PerfilEmpresa, on_delete=models.CASCADE)
    
    nivel_interesse = models.CharField("Nível de Interesse", max_length=20, choices=NivelInteresse.choices)
    feedback_texto = models.TextField("Feedback/Motivo", blank=True, null=True)
    
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Avaliação de Projeto"
        verbose_name_plural = "Avaliações de Projetos"
        unique_together = ('projeto', 'perfil')

    def __str__(self):
        return f"{self.perfil} - {self.projeto}: {self.get_nivel_interesse_display()}"
