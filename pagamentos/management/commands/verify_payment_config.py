from django.core.management.base import BaseCommand
from django.conf import settings
import mercadopago
import json

class Command(BaseCommand):
    help = 'Verifica a configuracao e credenciais do Mercado Pago'

    def handle(self, *args, **options):
        self.stdout.write("Iniciando verificação do Mercado Pago...")

        # 1. Verificar Credenciais
        token = settings.MERCADOPAGO_ACCESS_TOKEN
        if not token:
            self.stdout.write(self.style.ERROR("ERRO: MERCADOPAGO_ACCESS_TOKEN não encontrado no settings."))
            return
        
        masked_token = f"{token[:10]}...{token[-5:]}"
        self.stdout.write(f"Token encontrado: {masked_token}")

        try:
            sdk = mercadopago.SDK(token)
            self.stdout.write("SDK inicializado.")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"ERRO ao inicializar SDK: {e}"))
            return

        # 2. Testar Chamada de API (Listar pagamentos - operação de leitura segura)
        self.stdout.write("Testando autenticação (listando pagamentos)...")
        try:
            filters = {'sort': 'date_created', 'criteria': 'desc', 'limit': 1}
            res = sdk.payment().search(filters)
            
            if res["status"] == 200:
                self.stdout.write(self.style.SUCCESS(f"Autenticação OK! Status 200. Pagamentos encontrados: {len(res['response'].get('results', []))}"))
            else:
                self.stdout.write(self.style.ERROR(f"Falha na autenticação. Resposta: {res}"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Exceção ao chamar API: {e}"))

        # 3. Simular Criação de Preferência (Payload igual ao da produção)
        self.stdout.write("\nSimulando payload de Preferência...")
        
        # Dados mockados similares ao real
        preference_data = {
            "items": [
                {
                    "id": "1",
                    "title": "Plano Ouro Teste",
                    "description": "Teste de verificação",
                    "quantity": 1,
                    "currency_id": "BRL",
                    "unit_price": 100.00
                }
            ],
            "payer": {
                "name": "Teste",
                "surname": "Verificacao",
                "email": "test_user_123@test.com", # Email válido
                "phone": {
                    "area_code": "11",
                    "number": "999999999"
                },
                 "address": {
                    "zip_code": "06233200",
                    "street_name": "Av. das Nações Unidas",
                    "street_number": "3003"
                }
            },
            "back_urls": {
                "success": f"https://{settings.DOMINIO_BASE}/pagamentos/pagamento/sucesso/",
                "failure": f"https://{settings.DOMINIO_BASE}/pagamentos/pagamento/cancelado/",
                "pending": f"https://{settings.DOMINIO_BASE}/pagamentos/pagamento/pendente/"
            },
            "auto_return": "approved",
             # "binary_mode": True, # Testar se isso ajuda
        }
        
        self.stdout.write(f"Payload: {json.dumps(preference_data, indent=2)}")

        try:
            pref_res = sdk.preference().create(preference_data)
            if pref_res["status"] == 201:
                self.stdout.write(self.style.SUCCESS(f"Preferência criada com sucesso! ID: {pref_res['response']['id']}"))
                self.stdout.write(f"Init Point: {pref_res['response']['init_point']}")
            else:
                self.stdout.write(self.style.ERROR(f"Erro ao criar preferência: {pref_res}"))
        except Exception as e:
             self.stdout.write(self.style.ERROR(f"Exceção ao criar preferência: {e}"))

        # 4. Simular Caso de Borda: Sobrenome Vazio (Comum se usuário digitar apenas um nome)
        self.stdout.write("\nSimulando payload com Sobrenome Vazio...")
        preference_data_edge = preference_data.copy()
        preference_data_edge['payer'] = preference_data['payer'].copy()
        preference_data_edge['payer']['surname'] = ""
        
        try:
            pref_res = sdk.preference().create(preference_data_edge)
            if pref_res["status"] == 201:
                self.stdout.write(self.style.SUCCESS(f"Preferência (sem sobrenome) criada com sucesso! ID: {pref_res['response']['id']}"))
            else:
                self.stdout.write(self.style.WARNING(f"Alerta: Falha ao criar preferência sem sobrenome. Status: {pref_res['status']}"))
                self.stdout.write(f"Erro: {json.dumps(pref_res, indent=2)}")
        except Exception as e:
             self.stdout.write(self.style.ERROR(f"Exceção no teste de borda: {e}"))
