from django.shortcuts import render
from pagamentos.models import Oferta

def pagina_inicial(request):
    oferta_ouro = Oferta.objects.filter(slug='ouro', ativo=True).first()
    return render(
        request=request,
        template_name='site/index.html',
        context={
            'oferta_ouro_id': oferta_ouro.id if oferta_ouro else None
        }
    )

def politica_privacidade(request):
    return render(
        request=request,
        template_name='site/privacy-policy.html',
        context={}
    )

def termos_condicoes(request):
    return render(
        request=request,
        template_name='site/terms-conditions.html',
        context={}
    )
