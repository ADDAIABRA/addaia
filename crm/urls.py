from django.urls import path
from . import views

urlpatterns = [
    path('', views.crm, name='crm'),
    path('coletar/', views.coletar_leads, name='coletar_leads'),
    path('leads/', views.ver_leads, name='ver_leads'),
    path('leads/stream/<int:coleta_id>/', views.leads_stream, name='leads_stream'),
    path('leads/exportar/csv/', views.export_leads_csv, name='export_leads_csv'),
    path('leads/exportar/xlsx/', views.export_leads_excel, name='export_leads_excel'),
]
