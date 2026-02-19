from django.shortcuts import render
from pagamentos.decoradores_acesso import exigir_assinante_ativo

@exigir_assinante_ativo
def apresentacao(request):
    titulo_pagina = 'Apresentação'
    descricao_pagina = 'Bem-vindo à apresentação da plataforma.'
    context = {'titulo_pagina': titulo_pagina, 'descricao_pagina': descricao_pagina}

    return render(
        request=request,
        template_name='app/apresentacao/apresentacao.html',
        context=context
    )
