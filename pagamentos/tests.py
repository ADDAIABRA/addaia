"""
Testes unitários para o app de pagamentos.
Cobre models, níveis de acesso e lógica de upgrade.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from .models import Oferta, Compra, AcessoUsuario

class OfertaModelTest(TestCase):
    def test_comparacao_niveis(self):
        """Testa se a conversão de níveis numéricos está correta."""
        self.assertEqual(Oferta.obter_nivel_numerico('bronze'), 1)
        self.assertEqual(Oferta.obter_nivel_numerico('prata'), 2)
        self.assertEqual(Oferta.obter_nivel_numerico('ouro'), 3)
        self.assertEqual(Oferta.obter_nivel_numerico('invalido'), 0)

class AcessoUsuarioModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='testuser')
        self.acesso = AcessoUsuario.objects.create(
            usuario=self.user,
            nivel='prata',
            status='ativo'
        )

    def test_verificacao_acesso(self):
        """Testa a lógica de hierarquia de acesso (Prata deve acessar Bronze, mas não Ouro)."""
        # Prata deve acessar Bronze
        self.assertTrue(self.acesso.tem_acesso_minimo('bronze'))
        # Prata deve acessar Prata
        self.assertTrue(self.acesso.tem_acesso_minimo('prata'))
        # Prata NÃO deve acessar Ouro
        self.assertFalse(self.acesso.tem_acesso_minimo('ouro'))

    def test_status_inativo(self):
        """Testa se acesso suspenso bloqueia tudo."""
        self.acesso.status = 'suspenso'
        self.acesso.save()
        
        self.assertFalse(self.acesso.tem_acesso_minimo('bronze'))
        self.assertFalse(self.acesso.tem_acesso_minimo('prata'))

class FluxoUpgradeTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='upgradeuser')
        self.oferta_bronze = Oferta.objects.create(
            slug='bronze', nome_exibicao='Bronze', valor_centavos=1000, lookup_key='brz'
        )
        self.oferta_ouro = Oferta.objects.create(
            slug='ouro', nome_exibicao='Ouro', valor_centavos=3000, lookup_key='gld'
        )
        
    def test_logica_upgrade(self):
        """Simula o fluxo de upgrade de plano."""
        # 1. Compra Bronze
        compra1 = Compra.objects.create(
            usuario=self.user, oferta=self.oferta_bronze, status='paga'
        )
        
        # Cria acesso inicial
        acesso = AcessoUsuario.objects.create(
            usuario=self.user, nivel='bronze', status='ativo', ultima_compra=compra1
        )
        
        # Verifica estado inicial
        self.assertEqual(acesso.nivel, 'bronze')
        
        # 2. Compra Ouro (Upgrade)
        compra2 = Compra.objects.create(
            usuario=self.user, oferta=self.oferta_ouro, status='paga'
        )
        
        # Simula lógica da view (simplificada)
        nivel_atual = Oferta.obter_nivel_numerico(acesso.nivel)
        nivel_novo = Oferta.obter_nivel_numerico('ouro')
        
        if nivel_novo > nivel_atual:
            acesso.nivel = 'ouro'
            acesso.save()
            
        # Verifica se atualizou
        acesso.refresh_from_db()
        self.assertEqual(acesso.nivel, 'ouro')
