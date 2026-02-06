"""
Views do aplicativo de pagamentos.
Todas em português com lógica de negócio clara e comentada.
"""
import logging
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout

from .models import Oferta, Compra, AcessoUsuario, EventoStripe
from .servicos.stripe_servico import StripeServico
from .decoradores_acesso import exigir_bronze, exigir_prata, exigir_ouro
from .forms import CadastroUsuarioForm

logger = logging.getLogger(__name__)


def cadastro(request):
    """
    View de cadastro de novos usuários.
    Preserva o plano escolhido na sessão para redirecionar após o cadastro.
    """
    if request.method == 'POST':
        form = CadastroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Cadastro realizado com sucesso!')
            
            # Verificar se há um plano na sessão
            oferta_id = request.session.get('oferta_escolhida')
            if oferta_id:
                del request.session['oferta_escolhida']
                return redirect('confirmar_plano', oferta_id=oferta_id)
            
            return redirect('planos')
    else:
        form = CadastroUsuarioForm()
        
        # Salvar oferta escolhida na sessão se vier da URL
        oferta_id = request.GET.get('oferta_id')
        if oferta_id:
            request.session['oferta_escolhida'] = oferta_id
    
    return render(request, 'autenticacao/cadastro.html', {'form': form})


def logout_view(request):
    """
    Realiza o logout do usuário e redireciona para a página inicial.
    Suporta GET para facilitar o link de sair no menu.
    """
    logout(request)
    messages.success(request, 'Você saiu com sucesso.')
    return redirect('pagina_inicial')


def inicio(request):
    """
    Página inicial que lista o plano disponível.
    """
    ofertas = Oferta.objects.filter(ativo=True).order_by('valor_centavos')
    
    # Verificar se usuário já tem acesso
    acesso_atual = None
    if request.user.is_authenticated:
        try:
            acesso_atual = request.user.acesso
        except AcessoUsuario.DoesNotExist:
            pass
    
    context = {
        'ofertas': ofertas,
        'acesso_atual': acesso_atual,
    }
    return render(request, 'pagamentos/inicio.html', context)


def planos(request):
    """
    Página de planos (mesma que início, mas com URL diferente).
    """
    return inicio(request)


@login_required
def confirmar_plano(request, oferta_id):
    """
    Página de confirmação do plano escolhido.
    Usuário deve estar autenticado para chegar aqui.
    """
    oferta = get_object_or_404(Oferta, id=oferta_id, ativo=True)
    
    # Verificar se usuário já tem este plano ou superior
    try:
        acesso = request.user.acesso
        nivel_atual = Oferta.obter_nivel_numerico(acesso.nivel)
        nivel_novo = Oferta.obter_nivel_numerico(oferta.slug)
        
        if nivel_atual >= nivel_novo:
            messages.info(
                request,
                f"Você já possui o plano {acesso.get_nivel_display()} ou superior."
            )
            return redirect('plataforma_inicio')
    except AcessoUsuario.DoesNotExist:
        pass
    
    context = {
        'oferta': oferta,
    }
    return render(request, 'pagamentos/confirmar_plano.html', context)


@login_required
@require_POST
def criar_checkout(request, oferta_id):
    """
    Cria uma sessão de checkout do Stripe e redireciona o usuário.
    """
    oferta = get_object_or_404(Oferta, id=oferta_id, ativo=True)
    
    # Verificar se oferta tem IDs Stripe configurados
    if not oferta.stripe_product_id or not oferta.stripe_price_id:
        messages.error(
            request,
            "Este plano ainda não está disponível. Por favor, tente novamente mais tarde."
        )
        return redirect('planos')
    
    try:
        # Criar registro de compra
        compra = Compra.objects.create(
            usuario=request.user,
            oferta=oferta,
            status='pendente'
        )
        
        # Criar checkout session
        session = StripeServico.criar_checkout_session(
            compra=compra,
            oferta=oferta,
            dominio_base=settings.DOMINIO_BASE
        )
        
        # Salvar session_id
        compra.stripe_session_id = session.id
        compra.save()
        
        logger.info(f"Checkout criado: Compra {compra.id}, Session {session.id}")
        
        # Redirecionar para Stripe Checkout
        return redirect(session.url)
        
    except Exception as e:
        logger.error(f"Erro ao criar checkout: {str(e)}")
        messages.error(
            request,
            "Ocorreu um erro ao processar seu pagamento. Por favor, tente novamente."
        )
        return redirect('planos')


def pagamento_sucesso(request):
    """
    Página exibida após retorno bem-sucedido do Stripe Checkout.
    Verifica o status da sessão e concede acesso se o pagamento foi confirmado.
    Isso serve como fallback caso o webhook atrase ou falhe (comum em localhost).
    """
    session_id = request.GET.get('session_id')
    
    if session_id:
        try:
            # Recuperar sessão do Stripe para garantir status atualizado
            session = StripeServico.recuperar_session(session_id)
            
            if session.payment_status == 'paid':
                finalizar_compra(session)
        except Exception as e:
            logger.error(f"Erro ao validar sucesso do pagamento: {str(e)}")
    
    context = {
        'session_id': session_id,
    }
    return render(request, 'pagamentos/sucesso.html', context)


def pagamento_cancelado(request):
    """
    Página exibida quando usuário cancela o pagamento.
    """
    messages.info(request, "Pagamento cancelado. Você pode tentar novamente quando quiser.")
    return render(request, 'pagamentos/cancelado.html')


@csrf_exempt
@require_POST
def stripe_webhook(request):
    """
    Endpoint para receber webhooks do Stripe.
    Processa eventos de pagamento e concede acesso aos usuários.
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    # Validar assinatura do webhook
    try:
        event = StripeServico.verificar_assinatura_webhook(
            payload=payload,
            sig_header=sig_header,
            webhook_secret=settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        logger.error(f"Webhook inválido: {str(e)}")
        return HttpResponse(status=400)
    
    # Verificar idempotência - se já processamos este evento
    if EventoStripe.objects.filter(event_id=event.id).exists():
        logger.info(f"Evento {event.id} já foi processado anteriormente")
        return HttpResponse(status=200)
    
    # Processar evento
    if event.type == 'checkout.session.completed':
        processar_checkout_completo(event)
    else:
        logger.info(f"Evento ignorado: {event.type}")
    
    # Registrar evento como processado
    EventoStripe.objects.create(
        event_id=event.id,
        tipo=event.type,
        dados_json=json.dumps(event.data.object)
    )
    
    return HttpResponse(status=200)


@transaction.atomic
@transaction.atomic
def finalizar_compra(session):
    """
    Finaliza a compra com base na sessão do Stripe.
    Pode ser chamado pelo webhook ou pela view de sucesso.
    """
    # Extrair informações
    compra_id = session.get('client_reference_id')
    payment_intent_id = session.get('payment_intent')
    
    logger.info(f"Finalizando compra: {session.id}, Compra: {compra_id}")
    
    try:
        # Buscar compra
        compra = Compra.objects.select_for_update().get(id=compra_id)
        
        # Se já estiver paga, não fazer nada
        if compra.status == 'paga':
            logger.info(f"Compra {compra.id} já estava paga")
            return compra
        
        # Atualizar compra
        compra.status = 'paga'
        compra.stripe_payment_intent_id = payment_intent_id
        compra.save()
        
        logger.info(f"Compra {compra.id} marcada como paga")
        
        # Conceder ou atualizar acesso
        conceder_acesso_usuario(compra)
        
        return compra
        
    except Compra.DoesNotExist:
        logger.error(f"Compra {compra_id} não encontrada")
        raise
    except Exception as e:
        logger.error(f"Erro ao finalizar compra: {str(e)}")
        raise


def processar_checkout_completo(event):
    """
    Processa o evento checkout.session.completed do Stripe.
    Concede ou atualiza o acesso do usuário.
    """
    session = event.data.object
    finalizar_compra(session)


def conceder_acesso_usuario(compra):
    """
    Concede ou atualiza o acesso do usuário ao plano comprado.
    Permite apenas upgrades (bronze -> prata -> ouro).
    """
    usuario = compra.usuario
    novo_nivel = compra.oferta.slug
    
    # Verificar se usuário já tem acesso
    acesso, criado = AcessoUsuario.objects.get_or_create(
        usuario=usuario,
        defaults={
            'nivel': novo_nivel,
            'status': 'ativo',
            'ultima_compra': compra,
        }
    )
    
    if criado:
        logger.info(f"Novo acesso criado para {usuario.username}: {novo_nivel}")
    else:
        # Verificar se é um upgrade
        nivel_atual = Oferta.obter_nivel_numerico(acesso.nivel)
        nivel_novo = Oferta.obter_nivel_numerico(novo_nivel)
        
        if nivel_novo > nivel_atual:
            # Upgrade permitido
            acesso.nivel = novo_nivel
            acesso.status = 'ativo'
            acesso.ultima_compra = compra
            acesso.save()
            logger.info(f"Acesso atualizado para {usuario.username}: {acesso.nivel} -> {novo_nivel}")
        else:
            # Não fazer downgrade
            logger.info(f"Usuário {usuario.username} já tem nível {acesso.nivel}, nova compra: {novo_nivel} (não atualizado)")


# ============== VIEWS DAS PÁGINAS PROTEGIDAS ==============

@login_required
def plataforma_inicio(request):
    """
    Página inicial da plataforma (requer estar logado, mas não requer plano específico).
    """
    acesso = None
    try:
        acesso = request.user.acesso
    except AcessoUsuario.DoesNotExist:
        pass
    
    context = {
        'acesso': acesso,
    }
    return render(request, 'app/plataforma/inicio.html', context)


@exigir_bronze
def plataforma_bronze(request):
    """
    Conteúdo exclusivo para bronze ou superior.
    """
    return render(request, 'app/plataforma/bronze.html')


@exigir_prata
def plataforma_prata(request):
    """
    Conteúdo exclusivo para prata ou superior.
    """
    return render(request, 'app/plataforma/prata.html')


@exigir_ouro
def plataforma_ouro(request):
    """
    Conteúdo exclusivo para ouro.
    """
    return render(request, 'app/plataforma/ouro.html')
