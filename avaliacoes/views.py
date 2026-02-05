from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from projetos.models import Projeto
from .models import AvaliacaoProjeto
import json

@login_required
@require_POST
def registrar_avaliacao(request, projeto_id):
    try:
        data = json.loads(request.body)
        nivel_interesse = data.get('nivel_interesse')
        
        perfil = getattr(request.user, 'perfil_empresa', None)
        if not perfil:
            return JsonResponse({'error': 'Perfil não encontrado'}, status=400)
            
        projeto = get_object_or_404(Projeto, id=projeto_id, perfil=perfil)
        
        avaliacao, created = AvaliacaoProjeto.objects.update_or_create(
            projeto=projeto,
            perfil=perfil,
            defaults={'nivel_interesse': nivel_interesse}
        )
        
        return JsonResponse({
            'status': 'success', 
            'nivel': avaliacao.nivel_interesse,
            'label': avaliacao.get_nivel_interesse_display()
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
