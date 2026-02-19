import mercadopago
import requests
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import logging
import json

logger = logging.getLogger(__name__)

MP_PREAPPROVAL_URL = 'https://api.mercadopago.com/preapproval'


class MercadoPagoServico:
    """
    Serviço para interagir com a API do Mercado Pago.
    """
    
    @staticmethod
    def _get_sdk():
        return mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)
    
    @staticmethod
    def criar_preferencia(compra, oferta, dominio_base):
        """
        Cria uma preferência de pagamento no Mercado Pago.
        """
        sdk = MercadoPagoServico._get_sdk()
        
        # URLs de retorno
        back_urls = {
            "success": f"https://{dominio_base}/pagamentos/pagamento/sucesso/",
            "failure": f"https://{dominio_base}/pagamentos/pagamento/cancelado/",
            "pending": f"https://{dominio_base}/pagamentos/pagamento/pendente/"
        }
        
        preference_data = {
            "items": [
                {
                    "id": str(oferta.id),
                    "title": oferta.nome_exibicao,
                    "description": oferta.descricao or f"Assinatura {oferta.nome_exibicao}",
                    "quantity": 1,
                    "currency_id": "BRL",
                    "unit_price": float(oferta.valor_centavos) / 100
                }
            ],
            "payer": {
                "name": compra.usuario.first_name,
                "surname": compra.usuario.last_name,
                "email": compra.usuario.email,
            },
            "back_urls": back_urls,
            "auto_return": "approved",
            "external_reference": str(compra.id),
            "notification_url": f"https://{dominio_base}/pagamentos/mercadopago/webhook/"
        }
        
        preference_response = sdk.preference().create(preference_data)
        
        if preference_response["status"] == 201:
            return preference_response["response"]
        else:
            logger.error(f"Erro ao criar preferência MP. Status: {preference_response.get('status')}")
            logger.error(f"Resposta completa MP: {json.dumps(preference_response, indent=2)}")
            raise Exception("Erro ao criar preferência de pagamento no Mercado Pago")

    @staticmethod
    def get_payment_info(payment_id):
        sdk = MercadoPagoServico._get_sdk()
        return sdk.payment().get(payment_id)
    
    @staticmethod
    def criar_preapproval(assinatura, oferta, dominio_base):
        """
        Cria uma assinatura recorrente no Mercado Pago (API preapproval).
        Usa status=pending para permitir redirect ao checkout sem card_token.
        Retorna dict com init_point para redirecionar o usuário.
        """
        token = settings.MERCADOPAGO_ACCESS_TOKEN
        back_url = f"https://{dominio_base}/pagamentos/pagamento/sucesso/"
        
        # frequency: 1=mensal (cobra todo mês), 12=anual (cobra a cada 12 meses)
        frequency = 12 if oferta.periodicidade == 'anual' else 1
        valor_reais = float(oferta.valor_centavos) / 100
        
        start_date = timezone.now()
        end_date = start_date + timedelta(days=365 * 2)
        
        payload = {
            "reason": oferta.nome_exibicao,
            "external_reference": f"ass_{assinatura.id}",
            "payer_email": assinatura.usuario.email,
            "auto_recurring": {
                "frequency": frequency,
                "frequency_type": "months",
                "transaction_amount": valor_reais,
                "currency_id": "BRL",
                "start_date": start_date.strftime("%Y-%m-%dT%H:%M:%S.000-03:00"),
                "end_date": end_date.strftime("%Y-%m-%dT%H:%M:%S.000-03:00"),
            },
            "back_url": back_url,
            "status": "pending",
        }
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        
        response = requests.post(MP_PREAPPROVAL_URL, json=payload, headers=headers, timeout=30)
        
        if response.status_code in (200, 201):
            data = response.json()
            return data
        else:
            logger.error(f"Erro ao criar preapproval MP. Status: {response.status_code}")
            logger.error(f"Resposta: {response.text}")
            raise Exception("Erro ao criar assinatura no Mercado Pago")
    
    @staticmethod
    def get_preapproval_info(preapproval_id):
        """Obtém informações de uma assinatura pelo ID do preapproval."""
        token = settings.MERCADOPAGO_ACCESS_TOKEN
        url = f"{MP_PREAPPROVAL_URL}/{preapproval_id}"
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            return response.json()
        return None
