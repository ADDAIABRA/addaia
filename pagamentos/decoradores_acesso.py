"""
Decoradores para controlar acesso às páginas protegidas.
Verifica se o usuário tem o nível mínimo de plano requerido.
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

NIVEL_DISPLAY = {'basico': 'Básico', 'profissional': 'Profissional', 'enterprise': 'Enterprise', 'ouro': 'Ouro'}


def _nivel_display(nivel):
    slug = (nivel or '').replace('_mensal', '').replace('_anual', '')
    return NIVEL_DISPLAY.get(slug, (nivel or 'N/A').title())


def verificar_acesso(nivel_minimo):
    """
    Decorador genérico que verifica se o usuário tem acesso ao nível especificado.
    
    Args:
        nivel_minimo: 'bronze', 'prata' ou 'ouro'
    
    Uso:
        @verificar_acesso('bronze')
        def minha_view(request):
            ...
    """
    def decorador(view_func):
        @wraps(view_func)
        @login_required
        def wrapped_view(request, *args, **kwargs):
            # Verificar se o usuário tem acesso
            try:
                acesso = request.user.acesso
                
                # Verificar se o acesso está ativo
                if acesso.status != 'ativo':
                    messages.warning(
                        request,
                        f"Seu acesso está {acesso.status}. Entre em contato com o suporte."
                    )
                    return redirect('planos')
                
                # Verificar se tem o nível mínimo
                if not acesso.tem_acesso_minimo(nivel_minimo):
                    nivel_necessario_display = {
                        'basico': 'Básico',
                        'profissional': 'Profissional',
                        'enterprise': 'Enterprise',
                        'ouro': 'Profissional',
                    }.get(nivel_minimo, nivel_minimo.title())
                    
                    messages.warning(
                        request,
                        f"Esta área requer o plano {nivel_necessario_display} ou superior. "
                        f"Você possui o plano {_nivel_display(acesso.nivel)}."
                    )
                    return redirect('planos')
                
                # Usuário tem acesso, executar a view
                return view_func(request, *args, **kwargs)
                
            except AttributeError:
                # Usuário não tem acesso nenhum
                messages.info(
                    request,
                    "Você precisa adquirir um plano para acessar esta área."
                )
                return redirect('planos')
        
        return wrapped_view
    return decorador





def exigir_assinante_ativo(view_func):
    """
    Decorador que exige usuário assinante ativo e pagante.
    Verifica: login, existência de AcessoUsuario, status ativo e pagamento em dia
    (assinatura autorizada ou compra paga no legado).
    """
    @wraps(view_func)
    @login_required
    def wrapped_view(request, *args, **kwargs):
        try:
            acesso = request.user.acesso
        except AttributeError:
            messages.info(
                request,
                "Você precisa adquirir um plano para acessar esta área."
            )
            return redirect('planos')

        if acesso.status != 'ativo':
            messages.warning(
                request,
                f"Seu acesso está {acesso.status}. Entre em contato com o suporte."
            )
            return redirect('planos')

        # Verificar se o pagamento está em dia
        if acesso.ultima_assinatura_id:
            if acesso.ultima_assinatura.status != 'authorized':
                messages.warning(
                    request,
                    "Sua assinatura não está ativa. Regularize seu pagamento para continuar acessando."
                )
                return redirect('planos')
        elif acesso.ultima_compra_id:
            if acesso.ultima_compra.status != 'paga':
                messages.warning(
                    request,
                    "Seu pagamento está pendente. Entre em contato com o suporte."
                )
                return redirect('planos')
        # Se não tem assinatura nem compra vinculada (ex.: acesso manual), permite se status ativo

        return view_func(request, *args, **kwargs)

    return wrapped_view


def exigir_ouro(view_func):
    """
    Decorador legado que exige plano Ouro/Profissional ou superior.
    Use exigir_assinante_ativo para novas views.
    """
    return verificar_acesso('ouro')(view_func)
