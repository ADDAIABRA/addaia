from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import AvaliacaoMaturidade, PilarQuestionario, RespostaQuestionario
from .forms import RespostaPilarForm
from perfil.models import PerfilEmpresa

from django.views.decorators.cache import never_cache

@login_required
@never_cache
def overview(request):
    """
    Exibe o progresso dos 5 pilares do diagnóstico.
    """
    perfil = getattr(request.user, 'perfil_empresa', None)
    if not perfil:
        messages.warning(request, "Por favor, preencha o perfil da sua empresa antes de iniciar o diagnóstico.")
        return redirect('perfil')

    # Busca ou cria a avaliação ativa para este perfil
    avaliacao, created = AvaliacaoMaturidade.objects.get_or_create(
        perfil_empresa=perfil,
        defaults={'titulo': f"Diagnóstico - {perfil.nome_empresa or request.user.username}"}
    )

    pilares = PilarQuestionario.objects.filter(ativo=True).order_by('ordem')
    progresso = []
    pilares_respondidos = 0

    for pilar in pilares:
        resposta = RespostaQuestionario.objects.filter(avaliacao=avaliacao, pilar=pilar).first()
        progresso.append({
            'pilar': pilar,
            'respondido': bool(resposta),
            'pontuacao': resposta.pontuacao_pilar if resposta else 0,
            'estagio': resposta.get_estagio_pilar_display() if resposta else 'Pendente'
        })
        if resposta:
            pilares_respondidos += 1

    # Atualizar resultados globais
    if pilares_respondidos > 0:
        avaliacao.calcular_resultados()

    # Verifica se o relatório já foi gerado
    relatorio_existe = hasattr(avaliacao, 'relatorio_gerado')

    context = {
        'avaliacao': avaliacao,
        'progresso': progresso,
        'concluido': pilares_respondidos == len(pilares),
        'relatorio_existe': relatorio_existe,
        'titulo_pagina': 'Painel do Diagnóstico',
        'perfil': perfil
    }
    return render(request, 'app/questionarios/overview.html', context)

@login_required
@never_cache
def responder_pilar(request, pilar_id):
    """
    View dinâmica para responder as 10 perguntas de um pilar.
    """
    perfil = getattr(request.user, 'perfil_empresa', None)
    if not perfil:
        messages.warning(request, "Por favor, preencha o perfil da sua empresa antes de iniciar o diagnóstico.")
        return redirect('perfil')
        
    pilar = get_object_or_404(PilarQuestionario, id=pilar_id, ativo=True)
    avaliacao = get_object_or_404(AvaliacaoMaturidade, perfil_empresa=perfil)
    
    # Busca respostas anteriores para preencher o formulário
    initial_data = {}
    resposta_pilar = RespostaQuestionario.objects.filter(avaliacao=avaliacao, pilar=pilar).first()
    if resposta_pilar:
        for rp in resposta_pilar.respostas_perguntas.all():
            initial_data[f'pergunta_{rp.pergunta.id}'] = rp.alternativa_escolhida

    if request.method == 'POST':
        form = RespostaPilarForm(pilar, request.POST)
        if form.is_valid():
            form.save(avaliacao)
            messages.success(request, f"Respostas de '{pilar.get_pilar_display()}' salvas!")
            return redirect('questionarios:overview')
    else:
        form = RespostaPilarForm(pilar, initial=initial_data)

    context = {
        'pilar': pilar,
        'form': form,
        'titulo_pagina': f"Questionário: {pilar.get_pilar_display()}",
    }
    return render(request, 'app/questionarios/responder.html', context)
