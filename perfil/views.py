from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import PerfilEmpresaForm
from .models import PerfilEmpresa
from .constants import SETORES_SEGMENTOS, DEFAULT_SEGMENTS
import json
from pagamentos.decoradores_acesso import exigir_assinante_ativo
from django.views.decorators.cache import never_cache

@exigir_assinante_ativo
@never_cache
def perfil(request):
    # Tenta buscar o perfil existente do usuário
    perfil_empresa, created = PerfilEmpresa.objects.get_or_create(usuario=request.user)
    
    if request.method == 'POST':
        # print(f"DEBUG: POST Data: {request.POST}") 
        form = PerfilEmpresaForm(request.POST, instance=perfil_empresa)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('perfil')
        else:
            # print(f"DEBUG: Form Errors: {form.errors}")
            messages.error(request, 'Erro ao atualizar o perfil. Verifique os campos abaixo.')
    else:
        form = PerfilEmpresaForm(instance=perfil_empresa)

    titulo_pagina = 'Perfil da Empresa'
    descricao_pagina = 'Mantenha os dados da sua empresa atualizados para receber diagnósticos mais precisos.'
    
    context = {
        'titulo_pagina': titulo_pagina,
        'descricao_pagina': descricao_pagina,
        'form': form,
        'perfil_empresa': perfil_empresa,
        'setores_segmentos_json': json.dumps(SETORES_SEGMENTOS),
        'default_segments_json': json.dumps(DEFAULT_SEGMENTS)
    }

    return render(
        request=request,
        template_name='app/perfil/perfil.html',
        context=context
    )
