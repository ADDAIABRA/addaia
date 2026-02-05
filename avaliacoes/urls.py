from django.urls import path
from . import views

app_name = 'avaliacoes'

urlpatterns = [
    path('registrar/<int:projeto_id>/', views.registrar_avaliacao, name='registrar_avaliacao'),
]
