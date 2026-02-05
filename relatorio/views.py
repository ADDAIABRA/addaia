from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from questionarios.models import AvaliacaoMaturidade
from .models import Relatorio
from .utils import gerar_conteudo_relatorio

@login_required
def exibir_relatorio(request, avaliacao_id):
    """
    Exibe o relatório gerado. Se não existir, gera um novo.
    """
    perfil = getattr(request.user, 'perfil_empresa', None)
    if not perfil:
        messages.warning(request, "Por favor, preencha o perfil da sua empresa antes de acessar o relatório.")
        return redirect('perfil')
        
    avaliacao = get_object_or_404(AvaliacaoMaturidade, id=avaliacao_id, perfil_empresa=perfil)
    
    # Verifica se já existe um relatório gerado
    relatorio = Relatorio.objects.filter(avaliacao=avaliacao).first()
    
    # Se o usuário clicar em "Gerar" ou se não existir
    if not relatorio:
        # Verifica se todos os pilares foram respondidos (opcional, mas recomendado)
        if avaliacao.respostas_pilares.count() < 5:
            messages.warning(request, "Por favor, complete todos os 5 pilares do diagnóstico antes de gerar o relatório final.")
            return redirect('questionarios:overview')
            
        # Gerar via LLM
        conteudo = gerar_conteudo_relatorio(avaliacao)
        if conteudo:
            relatorio = Relatorio.objects.create(
                avaliacao=avaliacao,
                conteudo_json=conteudo
            )
        else:
            messages.error(request, "Ocorreu um erro ao gerar seu relatório. Por favor, tente novamente em instantes.")
            return redirect('questionarios:overview')

    context = {
        'titulo_pagina': f"Relatório - {avaliacao.perfil_empresa.nome_empresa}",
        'relatorio': relatorio,
        'dados': relatorio.conteudo_json,
        'avaliacao': avaliacao
    }

    return render(
        request=request,
        template_name='app/relatorio/relatorio.html',
        context=context
    )

@login_required
def regenerar_relatorio(request, avaliacao_id):
    """
    Redireciona para o relatório. A regeneração foi desativada.
    """
    return redirect('relatorio:exibir_relatorio', avaliacao_id=avaliacao_id)
