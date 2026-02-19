"""
URLs do aplicativo de pagamentos.
"""
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Página inicial e planos
    # path('', views.inicio, name='inicio'),
    path('planos/', views.planos, name='planos'),
    
    # Fluxo de compra
    path('confirmar-plano/<int:oferta_id>/', views.confirmar_plano, name='confirmar_plano'),
    path('criar-checkout/<int:oferta_id>/', views.criar_checkout, name='criar_checkout'),
    
    # Callbacks do Mercado Pago
    path('pagamento/sucesso/', views.pagamento_sucesso, name='pagamento_sucesso'),
    path('pagamento/cancelado/', views.pagamento_cancelado, name='pagamento_cancelado'),
    path('pagamento/pendente/', views.pagamento_pendente, name='pagamento_pendente'),
    
    # Webhook do Mercado Pago
    path('mercadopago/webhook/', views.mercadopago_webhook, name='mercadopago_webhook'),
    
    # Autenticação
    path('cadastro/', views.cadastro, name='cadastro'),
    path('login/', auth_views.LoginView.as_view(template_name='autenticacao/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Redefinição de senha
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
    
    # Plataforma - Páginas protegidas
    path('plataforma/', views.plataforma_inicio, name='plataforma_inicio'),

    path('plataforma/ouro/', views.plataforma_ouro, name='plataforma_ouro'),
]
