from django.db import models
from questionarios.models import AvaliacaoMaturidade

class Relatorio(models.Model):
    avaliacao = models.OneToOneField(
        AvaliacaoMaturidade,
        on_delete=models.CASCADE,
        related_name='relatorio_gerado'
    )
    conteudo_json = models.JSONField("Conteúdo do Relatório JSON")
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Relatório Gerado"
        verbose_name_plural = "Relatórios Gerados"
        db_table = "relatorio_gerado"

    def __str__(self):
        return f"Relatório #{self.id} - {self.avaliacao.perfil_empresa.nome_empresa if self.avaliacao.perfil_empresa else 'Empresa não identificada'}"
