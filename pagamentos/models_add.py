from django.db import models
from django.contrib.auth.models import User

class Perfil(models.Model):
    """
    Extensão do modelo de usuário para armazenar dados adicionais.
    """
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil', verbose_name='Usuário')
    telefone = models.CharField(max_length=20, verbose_name='Celular/WhatsApp')
    
    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfis'
    
    def __str__(self):
        return f"Perfil de {self.usuario.username}"
