from django.shortcuts import render, redirect
from pagamentos.decoradores_acesso import exigir_assinante_ativo
from django.contrib import messages

@exigir_assinante_ativo
def dashboard(request):
    perfil = getattr(request.user, 'perfil_empresa', None)
    if not perfil:
        messages.warning(request, "Por favor, preencha o perfil da sua empresa.")
        return redirect('perfil')

    titulo_pagina = 'Dashboard'
    descricao_pagina = 'Bem-vindo ao seu painel estratégico. Aqui você terá uma visão geral do seu negócio e próximos passos.'
    context = {'titulo_pagina': titulo_pagina, 'descricao_pagina': descricao_pagina, 'perfil': perfil}

    return render(
        request=request,
        template_name='app/dashboard/dashboard.html',
        context=context
    )
