import uuid
from .models import Visitor


class VisitorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def __call__(self, request):
        # 1. Identificar Usuário
        if request.user.is_authenticated:
            username = request.user.username
        else:
            username = "Visitante"

        # 2. Obter IP Real
        ip_address = self.get_client_ip(request)
        
        # 3. Chave de Máquina (via Cookie)
        machine_key = request.COOKIES.get('machine_id')
        set_new_id = False
        
        if not machine_key:
            machine_key = str(uuid.uuid4())
            set_new_id = True

        # 4. Dados Básicos
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        referer = request.META.get('HTTP_REFERER', '')
        page_visited = request.path

        # 5. Salvar no Banco
        try:
            Visitor.objects.create(
                ip_address=ip_address,
                user_agent=user_agent[:300],
                referer=referer,
                page_visited=page_visited[:200],
                machine_key=machine_key,
                username=username
            )
        except Exception:
            pass

        response = self.get_response(request)

        # Vincular Cookie se for novo
        if set_new_id:
            # Expira em 10 anos
            response.set_cookie('machine_id', machine_key, max_age=315360000)
            
        return response
