from django.shortcuts import render

def pagina_inicial(request):
    return render(
        request=request,
        template_name='site/index.html',
        context={}
    )

# TEMPORÁRIO
def outros(request):
    return render(
        request=request,
        template_name='site/outros-componentes.html',
        context={}
    )
