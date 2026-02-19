from django.shortcuts import render
from pagamentos.models import Oferta
from pagamentos.views import _agrupar_planos


def pagina_inicial(request):
    ofertas = Oferta.objects.filter(ativo=True).exclude(slug='ouro').order_by('valor_centavos')
    planos = _agrupar_planos(ofertas)
    return render(
        request=request,
        template_name='site/index.html',
        context={
            'planos': planos,
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

def erro403(request):
    return render(request, 'erros/403.html', status=403)

def erro404(request):
    return render(request, 'erros/404.html', status=404)

def erro500(request):
    return render(request, 'erros/500.html', status=500)

def erro503(request):
    return render(request, 'erros/503.html', status=503)
