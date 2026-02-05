from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def apresentacao(request):
    titulo_pagina = 'Apresentação'
    descricao_pagina = 'Bem-vindo à apresentação da plataforma.'
    context = {'titulo_pagina': titulo_pagina, 'descricao_pagina': descricao_pagina}

    return render(
        request=request,
        template_name='app/apresentacao/apresentacao.html',
        context=context
    )
