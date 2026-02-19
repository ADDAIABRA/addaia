from django.urls import path
from . import views

urlpatterns = [
    path('', views.pagina_inicial, name='pagina_inicial'),
    path('politica-privacidade/', views.politica_privacidade, name='politica_privacidade'),
    path('termos-condicoes/', views.termos_condicoes, name='termos_condicoes'),
    path('403/', views.erro403, name='erro403'),
    path('404/', views.erro404, name='erro404'),
    path('500/', views.erro500, name='erro500'),
    path('503/', views.erro503, name='erro503'),
]
