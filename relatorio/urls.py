from django.urls import path
from . import views

app_name = 'relatorio'

urlpatterns = [
    path('<int:avaliacao_id>/', views.exibir_relatorio, name='exibir_relatorio'),
    path('<int:avaliacao_id>/regenerar/', views.regenerar_relatorio, name='regenerar_relatorio'),
]
