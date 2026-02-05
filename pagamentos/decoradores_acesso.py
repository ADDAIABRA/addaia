"""
Decoradores para controlar acesso às páginas protegidas.
Verifica se o usuário tem o nível mínimo de plano requerido.
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required


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
                        'bronze': 'Bronze',
                        'prata': 'Prata',
                        'ouro': 'Ouro'
                    }.get(nivel_minimo, nivel_minimo)
                    
                    messages.warning(
                        request,
                        f"Esta área requer o plano {nivel_necessario_display} ou superior. "
                        f"Você possui o plano {acesso.get_nivel_display()}."
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


def exigir_bronze(view_func):
    """
    Decorador que exige plano Bronze ou superior.
    """
    return verificar_acesso('bronze')(view_func)


def exigir_prata(view_func):
    """
    Decorador que exige plano Prata ou superior.
    """
    return verificar_acesso('prata')(view_func)


def exigir_ouro(view_func):
    """
    Decorador que exige plano Ouro.
    """
    return verificar_acesso('ouro')(view_func)
