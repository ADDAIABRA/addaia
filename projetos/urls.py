from django.urls import path
from . import views

urlpatterns = [
    path('', views.projetos, name='projetos'),
    path('projeto/', views.projeto, name='projeto'),
    path('exportar/', views.exportar_projetos_pdf, name='exportar_projetos_pdf'),
    path('exportar/<int:id>/', views.exportar_projeto_detalhado_pdf, name='exportar_projeto_detalhado_pdf'),
]
