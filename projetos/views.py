from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Projeto
from .utils import gerar_projetos_ia
from questionarios.models import AvaliacaoMaturidade
from .pdf_exporter import generate_project_pdf, generate_projects_summary_pdf
from django.http import FileResponse
import io
from django.forms.models import model_to_dict

@login_required
def projetos(request):
    perfil = getattr(request.user, 'perfil_empresa', None)
    if not perfil:
        messages.warning(request, "Por favor, preencha o perfil da sua empresa.")
        return redirect('perfil')

    # Busca a última avaliação completa para basear os projetos
    avaliacao = AvaliacaoMaturidade.objects.filter(perfil_empresa=perfil).order_by('-atualizado_em').first()
    lista_projetos = Projeto.objects.filter(perfil=perfil)

    if request.method == 'POST' and 'generate_projects' in request.POST:
        if lista_projetos.exists():
            messages.warning(request, "Você já gerou seus projetos estratégicos.")
        elif avaliacao:
            if gerar_projetos_ia(perfil, avaliacao):
                messages.success(request, "Projetos estratégicos gerados com sucesso!")
                return redirect('projetos')
            else:
                messages.error(request, "Erro ao gerar projetos estrategicos. Tente novamente mais tarde.")
        else:
            messages.info(request, "Complete pelo menos um diagnóstico para receber recomendações de projetos.")
        return redirect('projetos')

    titulo_pagina = 'Roadmap de Projetos'
    descricao_pagina = 'Aqui estão os projetos recomendados para acelerar sua maturidade digital.'
    context = {
        'titulo_pagina': titulo_pagina, 
        'descricao_pagina': descricao_pagina, 
        'perfil': perfil,
        'projetos': lista_projetos,
        'avaliacao': avaliacao
    }

    return render(
        request=request,
        template_name='app/projetos/projetos.html',
        context=context
    )

@login_required
def projeto(request):
    perfil = getattr(request.user, 'perfil_empresa', None)
    if not perfil:
        messages.warning(request, "Por favor, preencha o perfil da sua empresa.")
        return redirect('perfil')

    projeto_id = request.GET.get('id')
    projeto_obj = None
    if projeto_id:
        projeto_obj = Projeto.objects.filter(id=projeto_id, perfil=perfil).first()
    
    if not projeto_obj:
        messages.error(request, "Projeto não encontrado.")
        return redirect('projetos')

    titulo_pagina = projeto_obj.nome_projeto
    descricao_pagina = 'Plano de ação detalhado para este projeto.'
    context = {
        'titulo_pagina': titulo_pagina, 
        'descricao_pagina': descricao_pagina, 
        'perfil': perfil,
        'projeto': projeto_obj
    }

    return render(
        request=request,
        template_name='app/projetos/projeto.html',
        context=context
    )

@login_required
def exportar_projetos_pdf(request):
    perfil = getattr(request.user, 'perfil_empresa', None)
    if not perfil:
        return redirect('perfil')

    projetos = Projeto.objects.filter(perfil=perfil)
    if not projetos.exists():
        messages.warning(request, "Nenhum projeto encontrado para exportar.")
        return redirect('projetos')

    buffer = io.BytesIO()
    generate_projects_summary_pdf(projetos, buffer, empresa_nome=perfil.nome_empresa)
    buffer.seek(0)

    filename = f"Roadmap_Projetos_{perfil.nome_empresa.replace(' ', '_')}.pdf"
    return FileResponse(buffer, as_attachment=True, filename=filename)

@login_required
def exportar_projeto_detalhado_pdf(request, id):
    perfil = getattr(request.user, 'perfil_empresa', None)
    if not perfil:
        return redirect('perfil')

    projeto_obj = Projeto.objects.filter(id=id, perfil=perfil).first()
    if not projeto_obj:
        messages.error(request, "Projeto não encontrado.")
        return redirect('projetos')

    # Convert model to dict and add extra info
    data = model_to_dict(projeto_obj)
    data['empresa_nome'] = perfil.nome_empresa
    
    buffer = io.BytesIO()
    generate_project_pdf(data, buffer)
    buffer.seek(0)

    filename = f"Projeto_{projeto_obj.nome_projeto.replace(' ', '_')}.pdf"
    return FileResponse(buffer, as_attachment=True, filename=filename)
