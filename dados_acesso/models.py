from django.db import models


class Visitor(models.Model):
    ip_address = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    user_agent = models.CharField(max_length=300)
    referer = models.URLField(blank=True, null=True)
    page_visited = models.CharField(max_length=200)
    machine_key = models.UUIDField(null=True, blank=True, verbose_name="Chave da Máquina")
    username = models.CharField(max_length=150, default="Visitante", verbose_name="Nome do Usuário")

    def __str__(self):
        return f'{self.ip_address} - {self.timestamp}'
