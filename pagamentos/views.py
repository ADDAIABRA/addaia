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

from .models import Oferta, Compra, Assinatura, AcessoUsuario, EventoMercadoPago
from .servicos.mercadopago_servico import MercadoPagoServico
from .decoradores_acesso import exigir_assinante_ativo
from .forms import CadastroUsuarioForm

logger = logging.getLogger(__name__)


def _validar_e_obter_oferta_id(request):
    """
    Obtém oferta_id válido de sessão, POST ou GET.
    Retorna o ID (int) se válido, None caso contrário.
    """
    for source in [request.session.get('oferta_escolhida'),
                   request.POST.get('oferta_id'),
                   request.GET.get('oferta_id')]:
        if source is None:
            continue
        try:
            oferta_id = int(source)
            if Oferta.objects.filter(id=oferta_id, ativo=True).exists():
                return oferta_id
        except (ValueError, TypeError):
            pass
    return None


def cadastro(request):
    """
    View de cadastro de novos usuários.
    Redireciona direto para o checkout do Mercado Pago após cadastro se houver oferta escolhida.
    """
    if request.method == 'POST':
        form = CadastroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Cadastro realizado com sucesso!')

            # Redirecionar direto para checkout (sem páginas intermediárias)
            oferta_id = _validar_e_obter_oferta_id(request)
            if oferta_id:
                request.session.pop('oferta_escolhida', None)
                return redirect('criar_checkout', oferta_id=oferta_id)

            return redirect('planos')
    else:
        form = CadastroUsuarioForm()

        # Salvar oferta na sessão e passar ao template (para hidden field)
        oferta_id = _validar_e_obter_oferta_id(request)
        if oferta_id:
            request.session['oferta_escolhida'] = oferta_id

    context = {'form': form}
    oferta_id = (request.session.get('oferta_escolhida') or
                 request.GET.get('oferta_id') or
                 request.POST.get('oferta_id'))
    if oferta_id:
        try:
            if Oferta.objects.filter(id=int(oferta_id), ativo=True).exists():
                context['oferta_id'] = int(oferta_id)
        except (ValueError, TypeError):
            pass

    return render(request, 'autenticacao/cadastro.html', context)


def logout_view(request):
    """
    Realiza o logout do usuário e redireciona para a página inicial.
    Suporta GET para facilitar o link de sair no menu.
    """
    logout(request)
    messages.success(request, 'Você saiu com sucesso.')
    return redirect('pagina_inicial')


def _agrupar_planos(ofertas):
    """Agrupa ofertas por plano base (basico, profissional, enterprise)."""
    planos = {}
    for o in ofertas:
        base = o.slug_base()
        if base not in planos:
            nomes = {'basico': 'Básico', 'profissional': 'Profissional', 'enterprise': 'Enterprise'}
            planos[base] = {'nome': nomes.get(base, base.title()), 'mensal': None, 'anual': None}
        if o.periodicidade == 'mensal':
            planos[base]['mensal'] = o
        else:
            planos[base]['anual'] = o
    return list(planos.values())


def inicio(request):
    """
    Página de planos com os 3 planos (Básico, Profissional, Enterprise)
    cada um com opção mensal e anual.
    """
    ofertas = Oferta.objects.filter(ativo=True).exclude(slug='ouro').order_by('valor_centavos')
    planos = _agrupar_planos(ofertas)
    
    acesso_atual = None
    if request.user.is_authenticated:
        try:
            acesso_atual = request.user.acesso
        except AcessoUsuario.DoesNotExist:
            pass
    
    context = {
        'planos': planos,
        'acesso_atual': acesso_atual,
    }
    return render(request, 'pagamentos/inicio.html', context)


def planos(request):
    """
    Página de planos (mesma que início, mas com URL diferente).
    """
    return inicio(request)


NIVEL_DISPLAY = {'basico': 'Básico', 'profissional': 'Profissional', 'enterprise': 'Enterprise', 'ouro': 'Ouro'}


def _nivel_display(nivel):
    """Retorna nome de exibição do nível."""
    slug_base = nivel.replace('_mensal', '').replace('_anual', '')
    return NIVEL_DISPLAY.get(slug_base, nivel.title())


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
                f"Você já possui o plano {_nivel_display(acesso.nivel)} ou superior."
            )
            return redirect('plataforma_inicio')
    except AcessoUsuario.DoesNotExist:
        pass
    
    context = {
        'oferta': oferta,
    }
    return render(request, 'pagamentos/confirmar_plano.html', context)


@login_required
def criar_checkout(request, oferta_id):
    """
    Cria uma assinatura no Mercado Pago (preapproval) e redireciona o usuário.
    Permite GET para facilitar redirecionamentos diretos após cadastro/login.
    """
    oferta = get_object_or_404(Oferta, id=oferta_id, ativo=True)
    
    try:
        # Criar registro de assinatura
        assinatura = Assinatura.objects.create(
            usuario=request.user,
            oferta=oferta,
            status='pendente'
        )
        
        # Criar preapproval no Mercado Pago (API de assinaturas)
        preapproval = MercadoPagoServico.criar_preapproval(
            assinatura=assinatura,
            oferta=oferta,
            dominio_base=settings.DOMINIO_BASE
        )
        
        # Salvar ID do preapproval
        assinatura.mercadopago_preapproval_id = preapproval.get('id', '')
        assinatura.save()
        
        logger.info(f"Checkout assinatura criado: Assinatura {assinatura.id}, Preapproval {assinatura.mercadopago_preapproval_id}")
        
        # Redirecionar para checkout de assinaturas do Mercado Pago
        init_point = preapproval.get('init_point')
        if not init_point:
            raise Exception("Mercado Pago não retornou init_point")
        return redirect(init_point)
        
    except Exception as e:
        logger.error(f"Erro ao criar checkout: {str(e)}")
        messages.error(
            request,
            "Ocorreu um erro ao processar seu pagamento. Por favor, tente novamente."
        )
        return redirect('planos')


def pagamento_sucesso(request):
    """
    Página exibida após retorno do Mercado Pago (checkout de assinatura).
    Suporta fluxo de assinatura (preapproval_id) e fluxo legado (collection_id).
    """
    preapproval_id = request.GET.get('preapproval_id')
    collection_id = request.GET.get('collection_id')
    collection_status = request.GET.get('collection_status')
    external_reference = request.GET.get('external_reference')
    
    # Fluxo de assinatura (preapproval)
    if preapproval_id:
        try:
            assinatura = Assinatura.objects.get(mercadopago_preapproval_id=preapproval_id)
            if assinatura.status not in ('authorized', 'pending'):
                info = MercadoPagoServico.get_preapproval_info(preapproval_id)
                if info:
                    status_mp = info.get('status', '')
                    if status_mp in ('authorized', 'pending'):
                        finalizar_assinatura(assinatura)
                        messages.success(request, "Assinatura confirmada! Seu acesso foi liberado.")
                    else:
                        messages.info(request, "Sua assinatura está sendo processada. O acesso será liberado em breve.")
                else:
                    messages.info(request, "Sua assinatura está sendo processada. O acesso será liberado em breve.")
            else:
                messages.info(request, "Sua assinatura já foi confirmada anteriormente.")
        except Assinatura.DoesNotExist:
            logger.error(f"Assinatura com preapproval_id {preapproval_id} não encontrada")
            messages.warning(request, "Não encontramos sua assinatura. Entre em contato com o suporte.")
        except Exception as e:
            logger.error(f"Erro ao processar sucesso da assinatura: {str(e)}")
            messages.warning(request, "Estamos processando sua assinatura. O acesso será liberado em breve.")
        
        return render(request, 'pagamentos/sucesso.html')
    
    # Fluxo legado (pagamento único - collection_id)
    if collection_status == 'approved' and external_reference and collection_id:
        try:
            compra_id = external_reference
            compra = Compra.objects.get(id=compra_id)
            
            if compra.status != 'paga':
                payment_info = MercadoPagoServico.get_payment_info(collection_id)
                response_data = payment_info.get("response") or {}
                if (payment_info.get("status") == 200 and
                        response_data.get("status") == "approved"):
                    finalizar_compra(compra, collection_id)
                    messages.success(request, "Pagamento confirmado! Seu acesso foi liberado.")
                else:
                    messages.warning(request, "Estamos processando seu pagamento. Seu acesso será liberado em breve.")
            else:
                messages.info(request, "Seu pagamento já foi confirmado anteriormente.")
        except Compra.DoesNotExist:
            logger.error(f"Compra {external_reference} não encontrada no retorno de sucesso")
        except Exception as e:
            logger.error(f"Erro ao processar sucesso do pagamento: {str(e)}")
    
    return render(request, 'pagamentos/sucesso.html')


def pagamento_cancelado(request):
    """
    Página exibida quando usuário cancela o pagamento ou ocorre erro.
    """
    messages.info(request, "Pagamento não concluído. Você pode tentar novamente quando quiser.")
    return render(request, 'pagamentos/cancelado.html')

def pagamento_pendente(request):
    """
    Página exibida quando o pagamento está pendente (ex: boleto ou processamento).
    """
    messages.info(request, "Seu pagamento está sendo processado. Assim que confirmado, seu acesso será liberado.")
    return render(request, 'pagamentos/sucesso.html') # Reutilizando a página de sucesso com mensagem apropriada


@csrf_exempt
@require_POST
def mercadopago_webhook(request):
    """
    Endpoint para receber webhooks do Mercado Pago.
    Trata: payment (pagamentos), subscription_preapproval (assinaturas).
    """
    try:
        topic = request.GET.get('topic') or request.GET.get('type')
        id_param = request.GET.get('id') or request.GET.get('data.id')
        
        if not id_param:
            try:
                data = json.loads(request.body)
                topic = data.get('type')
                id_param = data.get('data', {}).get('id')
            except Exception:
                pass

        logger.info(f"Webhook recebido: Topic={topic}, ID={id_param}")

        # Assinatura: subscription_preapproval
        if topic == 'subscription_preapproval' and id_param:
            event_id = f"sub_preapproval_{id_param}"
            if EventoMercadoPago.objects.filter(event_id=event_id).exists():
                logger.info(f"Evento {event_id} já processado.")
                return HttpResponse(status=200)
            
            info = MercadoPagoServico.get_preapproval_info(id_param)
            if info and info.get('status') in ('authorized', 'pending'):
                try:
                    assinatura = Assinatura.objects.get(mercadopago_preapproval_id=id_param)
                    if assinatura.status not in ('authorized', 'pending'):
                        finalizar_assinatura(assinatura)
                        EventoMercadoPago.objects.create(
                            event_id=event_id,
                            tipo=topic or 'subscription_preapproval',
                            dados_json=json.dumps(info)
                        )
                        logger.info(f"Assinatura {assinatura.id} confirmada via Webhook")
                    else:
                        EventoMercadoPago.objects.get_or_create(
                            event_id=event_id,
                            defaults={'tipo': topic or 'subscription_preapproval', 'dados_json': json.dumps(info)}
                        )
                except Assinatura.DoesNotExist:
                    logger.error(f"Assinatura preapproval_id={id_param} não encontrada")

        # Pagamento: payment (legado ou cobrança recorrente de assinatura)
        if topic == 'payment' and id_param:
            payment_info = MercadoPagoServico.get_payment_info(id_param)
            if payment_info.get("status") != 200:
                return HttpResponse(status=200)
            
            payment = payment_info.get("response") or {}
            external_reference = payment.get("external_reference")
            status = payment.get("status")
            event_id = f"payment_{id_param}_{status}"
            
            if EventoMercadoPago.objects.filter(event_id=event_id).exists():
                logger.info(f"Evento {event_id} já processado.")
                return HttpResponse(status=200)

            if external_reference and status == 'approved':
                # Assinatura: external_reference = "ass_123"
                if str(external_reference).startswith('ass_'):
                    try:
                        ass_id = int(external_reference.replace('ass_', ''))
                        assinatura = Assinatura.objects.get(id=ass_id)
                        if assinatura.status not in ('authorized', 'pending'):
                            finalizar_assinatura(assinatura)
                        EventoMercadoPago.objects.get_or_create(
                            event_id=event_id,
                            defaults={'tipo': topic or 'payment', 'dados_json': json.dumps(payment)}
                        )
                        # Renovação mensal: reset leads_consumidos_mes
                        try:
                            acesso = assinatura.usuario.acesso
                            acesso.leads_consumidos_mes = 0
                            acesso.mes_referencia = timezone.now().strftime('%Y-%m')
                            acesso.save()
                        except AcessoUsuario.DoesNotExist:
                            pass
                    except (ValueError, Assinatura.DoesNotExist):
                        logger.error(f"Assinatura ref {external_reference} não encontrada")
                else:
                    # Fluxo legado: Compra
                    try:
                        compra = Compra.objects.get(id=external_reference)
                        if compra.status != 'paga':
                            finalizar_compra(compra, str(payment['id']))
                            EventoMercadoPago.objects.create(
                                event_id=event_id,
                                tipo=topic or 'payment',
                                dados_json=json.dumps(payment)
                            )
                            logger.info(f"Compra {compra.id} confirmada via Webhook")
                        else:
                            EventoMercadoPago.objects.get_or_create(
                                event_id=event_id,
                                defaults={'tipo': topic or 'payment', 'dados_json': json.dumps(payment)}
                            )
                    except Compra.DoesNotExist:
                        logger.error(f"Compra {external_reference} não encontrada no webhook")
            
        return HttpResponse(status=200)

    except Exception as e:
        logger.error(f"Erro no webhook: {str(e)}")
        return HttpResponse(status=500)


@transaction.atomic
def finalizar_compra(compra, payment_id):
    """
    Finaliza a compra (fluxo legado), marca como paga e concede acesso.
    """
    compra.status = 'paga'
    compra.mercadopago_payment_id = payment_id
    compra.save()
    
    conceder_acesso_por_compra(compra)
    
    return compra


@transaction.atomic
def finalizar_assinatura(assinatura):
    """
    Finaliza a assinatura, marca como autorizada e concede acesso.
    """
    assinatura.status = 'authorized'
    assinatura.save()
    
    conceder_acesso_por_assinatura(assinatura)
    
    return assinatura


def conceder_acesso_por_compra(compra):
    """
    Concede ou atualiza o acesso do usuário ao plano (fluxo legado - compra única).
    """
    usuario = compra.usuario
    novo_nivel = compra.oferta.slug_base()
    leads_limite = compra.oferta.leads_mensais or 0
    
    acesso, criado = AcessoUsuario.objects.get_or_create(
        usuario=usuario,
        defaults={
            'nivel': novo_nivel,
            'status': 'ativo',
            'leads_limite_mensal': leads_limite,
            'leads_consumidos_mes': 0,
            'mes_referencia': timezone.now().strftime('%Y-%m'),
            'ultima_compra': compra,
        }
    )
    
    if not criado:
        acesso.nivel = novo_nivel
        acesso.status = 'ativo'
        acesso.leads_limite_mensal = leads_limite
        acesso.leads_consumidos_mes = 0
        acesso.mes_referencia = timezone.now().strftime('%Y-%m')
        acesso.ultima_compra = compra
        acesso.ultima_assinatura = None
        acesso.save()
    
    logger.info(f"Acesso concedido/atualizado para {usuario.username}: {novo_nivel}")


def conceder_acesso_por_assinatura(assinatura):
    """
    Concede ou atualiza o acesso do usuário ao plano (fluxo de assinatura recorrente).
    """
    usuario = assinatura.usuario
    oferta = assinatura.oferta
    novo_nivel = oferta.slug_base()
    leads_limite = oferta.leads_mensais or 0
    
    acesso, criado = AcessoUsuario.objects.get_or_create(
        usuario=usuario,
        defaults={
            'nivel': novo_nivel,
            'status': 'ativo',
            'leads_limite_mensal': leads_limite,
            'leads_consumidos_mes': 0,
            'mes_referencia': timezone.now().strftime('%Y-%m'),
            'ultima_assinatura': assinatura,
        }
    )
    
    if not criado:
        acesso.nivel = novo_nivel
        acesso.status = 'ativo'
        acesso.leads_limite_mensal = leads_limite
        acesso.leads_consumidos_mes = 0
        acesso.mes_referencia = timezone.now().strftime('%Y-%m')
        acesso.ultima_assinatura = assinatura
        acesso.ultima_compra = None
        acesso.save()
    
    logger.info(f"Acesso assinatura concedido/atualizado para {usuario.username}: {novo_nivel} ({leads_limite} leads/mes)")


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


@exigir_assinante_ativo
def plataforma_ouro(request):
    """
    Conteúdo exclusivo para ouro.
    """
    return render(request, 'app/plataforma/ouro.html')
