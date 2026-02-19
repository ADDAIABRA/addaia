"""
Serviço de coleta de leads via Google Places API (New).
Adaptado de rascunhos/buscar_empresas_google2.py e rascunhos/raio_busca.py.
"""
import time
import logging
import requests
from decimal import Decimal
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


def get_api_key():
    """Retorna a chave da API ou None se não configurada."""
    return getattr(settings, 'GOOGLE_PLACES_API_KEY', None) or ''


def get_coordinates(endereco):
    """
    Converte endereço em Latitude e Longitude usando Geocoding API.
    Retorna (lat, lng) ou (None, None) em caso de erro.
    """
    api_key = get_api_key()
    if not api_key:
        logger.error("GOOGLE_PLACES_API_KEY não configurada")
        return None, None

    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": endereco, "key": api_key}
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        if data.get('status') == 'OK':
            location = data['results'][0]['geometry']['location']
            return location['lat'], location['lng']
        logger.warning(f"Geocoding API status: {data.get('status')}")
    except Exception as e:
        logger.exception(f"Erro ao obter coordenadas: {e}")
    return None, None


def search_places_with_radius(keyword, lat, lng, radius_km):
    """
    Busca locais dentro de um raio específico.
    Usa locationRestriction (circle) - só retorna resultados dentro do círculo.
    """
    api_key = get_api_key()
    if not api_key:
        return []

    url = "https://places.googleapis.com/v1/places:searchText"
    all_places = []
    next_token = None
    radius_meters = float(radius_km * 1000)

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "places.id,places.displayName,nextPageToken"
    }

    while len(all_places) < 60:
        payload = {
            "textQuery": keyword,
            "languageCode": "pt-BR",
            "maxResultCount": 20,
            "locationRestriction": {
                "circle": {
                    "center": {"latitude": lat, "longitude": lng},
                    "radius": radius_meters
                }
            }
        }
        if next_token:
            payload["pageToken"] = next_token

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=15)
            data = response.json()

            if response.status_code != 200:
                logger.warning(f"Places API erro: {data}")
                break

            current_places = data.get("places", [])
            all_places.extend(current_places)
            next_token = data.get("nextPageToken")

            if not next_token:
                break
            time.sleep(2)
        except Exception as e:
            logger.exception(f"Erro na busca Places: {e}")
            break

    return all_places


def search_places_location(keyword, bairro, cidade):
    """
    Busca locais por texto: "keyword em bairro, cidade".
    Sem restrição de raio.
    """
    api_key = get_api_key()
    if not api_key:
        return []

    url = "https://places.googleapis.com/v1/places:searchText"
    all_places = []
    next_token = None

    location_str = f"{bairro}, {cidade}" if bairro else cidade
    text_query = f"{keyword} em {location_str}"

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "places.id,places.displayName,nextPageToken"
    }

    while len(all_places) < 60:
        payload = {
            "textQuery": text_query,
            "languageCode": "pt-BR",
            "maxResultCount": 20
        }
        if next_token:
            payload["pageToken"] = next_token

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=15)
            data = response.json()

            if response.status_code != 200:
                logger.warning(f"Places API erro: {data}")
                break

            current_places = data.get("places", [])
            all_places.extend(current_places)
            next_token = data.get("nextPageToken")

            if not next_token:
                break
            time.sleep(2)
        except Exception as e:
            logger.exception(f"Erro na busca Places: {e}")
            break

    return all_places


def get_place_details(place_id):
    """
    Obtém detalhes de um lugar pelo place_id.
    O place_id pode vir como "places/ChIJ..." - extraímos a parte final se necessário.
    """
    api_key = get_api_key()
    if not api_key:
        return None

    # Algumas respostas trazem "places/ChIJ..." - a API get aceita só "ChIJ..."
    clean_id = place_id.replace("places/", "") if place_id.startswith("places/") else place_id
    url = f"https://places.googleapis.com/v1/places/{clean_id}"

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "displayName,formattedAddress,nationalPhoneNumber,websiteUri,rating,userRatingCount"
    }

    try:
        response = requests.get(url, headers=headers, params={"languageCode": "pt-BR"}, timeout=10)
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        logger.exception(f"Erro ao obter detalhes do place {place_id}: {e}")
        return None


def _ensure_acesso_mensal(usuario):
    """
    Garante que mes_referencia está correto e reseta leads_consumidos_mes se mudou o mês.
    """
    from pagamentos.models import AcessoUsuario

    try:
        acesso = usuario.acesso
    except Exception:
        return None

    ano_mes_atual = timezone.now().strftime('%Y-%m')
    if acesso.mes_referencia != ano_mes_atual:
        acesso.leads_consumidos_mes = 0
        acesso.mes_referencia = ano_mes_atual
        acesso.save(update_fields=['leads_consumidos_mes', 'mes_referencia'])
    return acesso


def run_coleta(coleta_id):
    """
    Função principal executada em thread.
    Busca lugares, obtém detalhes, salva Lead, respeita limite mensal.
    """
    from crm.models import Coleta, Lead

    try:
        coleta = Coleta.objects.get(id=coleta_id)
    except Coleta.DoesNotExist:
        logger.error(f"Coleta {coleta_id} não encontrada")
        return

    usuario = coleta.usuario
    acesso = _ensure_acesso_mensal(usuario)
    if not acesso:
        coleta.status = 'erro'
        coleta.mensagem_erro = "Usuário sem acesso configurado."
        coleta.save(update_fields=['status', 'mensagem_erro'])
        return

    limite = acesso.leads_limite_mensal or 0
    if limite <= 0:
        coleta.status = 'erro'
        coleta.mensagem_erro = "Plano sem limite de leads disponível."
        coleta.save(update_fields=['status', 'mensagem_erro'])
        return

    if acesso.leads_consumidos_mes >= limite:
        coleta.status = 'concluida'
        coleta.mensagem_erro = "Limite mensal de leads já atingido."
        coleta.save(update_fields=['status', 'mensagem_erro'])
        return

    try:
        if coleta.usar_raio and coleta.raio_km:
            endereco = f"{coleta.bairro}, {coleta.cidade}" if coleta.bairro else coleta.cidade
            lat, lng = get_coordinates(endereco)
            if lat is None:
                coleta.status = 'erro'
                coleta.mensagem_erro = f"Não foi possível geocodificar: {endereco}"
                coleta.save(update_fields=['status', 'mensagem_erro'])
                return
            places = search_places_with_radius(
                coleta.keyword,
                lat, lng,
                float(coleta.raio_km)
            )
        else:
            places = search_places_location(
                coleta.keyword,
                coleta.bairro,
                coleta.cidade
            )

        for place in places:
            if acesso.leads_consumidos_mes >= limite:
                break

            place_id_raw = place.get('id', '')
            if not place_id_raw:
                continue

            # Evitar duplicata na mesma coleta
            if Lead.objects.filter(coleta=coleta, place_id=place_id_raw).exists():
                continue

            details = get_place_details(place_id_raw)
            if not details:
                time.sleep(0.2)
                continue

            nome = ""
            if isinstance(details.get('displayName'), dict):
                nome = details.get('displayName', {}).get('text', '')
            else:
                nome = str(details.get('displayName', ''))

            nota_val = details.get('rating')
            if nota_val is not None:
                try:
                    nota_decimal = Decimal(str(nota_val))
                except Exception:
                    nota_decimal = None
            else:
                nota_decimal = None

            total_avaliacoes = details.get('userRatingCount') or 0
            try:
                total_avaliacoes = int(total_avaliacoes)
            except (TypeError, ValueError):
                total_avaliacoes = 0

            try:
                lead_telefone = details.get('nationalPhoneNumber', '') or ''
                lead_endereco = details.get('formattedAddress', '') or ''
                lead_site = details.get('websiteUri', '') or ''
                Lead.objects.create(
                    usuario=usuario,
                    coleta=coleta,
                    place_id=place_id_raw,
                    categoria=coleta.keyword,
                    cidade=coleta.cidade,
                    bairro=coleta.bairro or '',
                    nome=nome[:300],
                    telefone=lead_telefone,
                    endereco=lead_endereco,
                    site=lead_site,
                    nota=nota_decimal,
                    total_avaliacoes=total_avaliacoes
                )
                print("[Lead coletado]", {
                    "usuario": usuario.id,
                    "coleta": coleta.id,
                    "place_id": place_id_raw,
                    "categoria": coleta.keyword,
                    "cidade": coleta.cidade,
                    "bairro": coleta.bairro or '',
                    "nome": nome[:300],
                    "telefone": lead_telefone,
                    "endereco": lead_endereco,
                    "site": lead_site,
                    "nota": nota_decimal,
                    "total_avaliacoes": total_avaliacoes,
                })
                acesso.leads_consumidos_mes += 1
                acesso.save(update_fields=['leads_consumidos_mes'])
            except Exception as e:
                logger.warning(f"Erro ao salvar lead {place_id_raw}: {e}")

            time.sleep(0.2)

        coleta.status = 'concluida'
        coleta.save(update_fields=['status', 'atualizado_em'])

    except Exception as e:
        logger.exception(f"Erro na coleta {coleta_id}: {e}")
        coleta.status = 'erro'
        coleta.mensagem_erro = str(e)[:2000]
        coleta.save(update_fields=['status', 'mensagem_erro'])
