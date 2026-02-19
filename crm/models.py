"""
Models do CRM - Coleta e Leads.
Leads vinculados ao usuário (user1 não vê leads do user2).
"""
from django.db import models
from django.conf import settings
from decimal import Decimal


class Coleta(models.Model):
    """
    Lote de coleta vinculado ao usuário.
    Armazena critérios de busca e status da execução.
    """
    STATUS_CHOICES = [
        ('em_andamento', 'Em andamento'),
        ('concluida', 'Concluída'),
        ('erro', 'Erro'),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='coletas',
        verbose_name='Usuário'
    )
    keyword = models.CharField(max_length=200, verbose_name='Palavra-chave / Categoria')
    cidade = models.CharField(max_length=150, verbose_name='Cidade')
    bairro = models.CharField(max_length=150, blank=True, verbose_name='Bairro')
    usar_raio = models.BooleanField(default=False, verbose_name='Usar raio de busca')
    raio_km = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Raio em km (1-50)'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='em_andamento',
        verbose_name='Status'
    )
    mensagem_erro = models.TextField(blank=True, verbose_name='Mensagem de erro')
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')

    class Meta:
        verbose_name = 'Coleta'
        verbose_name_plural = 'Coletas'
        ordering = ['-criado_em']

    def __str__(self):
        return f"Coleta #{self.id} - {self.keyword} em {self.cidade} ({self.status})"


class Lead(models.Model):
    """
    Lead individual coletado via Google Places.
    Vinculado ao usuário e à coleta.
    """
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='leads',
        verbose_name='Usuário'
    )
    coleta = models.ForeignKey(
        Coleta,
        on_delete=models.CASCADE,
        related_name='leads',
        verbose_name='Coleta'
    )
    place_id = models.CharField(
        max_length=200,
        verbose_name='ID do Google Places'
    )
    categoria = models.CharField(max_length=200, blank=True, verbose_name='Categoria')
    cidade = models.CharField(max_length=150, blank=True, verbose_name='Cidade')
    bairro = models.CharField(max_length=150, blank=True, verbose_name='Bairro')
    nome = models.CharField(max_length=300, verbose_name='Nome')
    telefone = models.CharField(max_length=50, blank=True, verbose_name='Telefone')
    endereco = models.TextField(blank=True, verbose_name='Endereço')
    site = models.URLField(max_length=500, blank=True, verbose_name='Site')
    nota = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Nota Google'
    )
    total_avaliacoes = models.PositiveIntegerField(
        default=0,
        verbose_name='Total de avaliações'
    )
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')

    class Meta:
        verbose_name = 'Lead'
        verbose_name_plural = 'Leads'
        ordering = ['-criado_em']
        unique_together = [['coleta', 'place_id']]
        indexes = [
            models.Index(fields=['usuario']),
            models.Index(fields=['coleta']),
        ]

    def __str__(self):
        return f"{self.nome} ({self.place_id})"
