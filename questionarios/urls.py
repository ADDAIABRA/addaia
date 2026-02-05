from django.urls import path
from . import views

app_name = 'questionarios'

urlpatterns = [
    path('', views.overview, name='overview'),
    path('responder/<int:pilar_id>/', views.responder_pilar, name='responder_pilar'),
]
