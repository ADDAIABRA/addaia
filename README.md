# Plataforma de Pagamentos Django + Stripe

Aplicação completa de vendas de planos vitalícios (Bronze, Prata, Ouro) com integração segura via Stripe Checkout e Webhooks.

## 🚀 Funcionalidades

- **Planos**: Sistema hierárquico (Bronze < Prata < Ouro).
- **Pagamento**: Checkout seguro com Stripe (cartão, boleto, pix, etc).
- **Acesso**: Liberação automática via Webhook com idempotência.
- **Proteção**: Decoradores de nível de acesso (`@exigir_prata`, etc).
- **Interface**: Design responsivo com Bootstrap 4.
- **Gestão**: Management command para provisionar produtos no Stripe.

---

## 🛠️ Instalação e Configuração

### 1. Pré-requisitos

- Python 3.12+
- Conta no [Stripe](https://dashboard.stripe.com/register)
- [Stripe CLI](https://stripe.com/docs/stripe-cli) (para testar webhooks localmente)

### 2. Configurar Ambiente

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente (Windows)
venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt
```

### 3. Configurar Variáveis

Copie o arquivo de exemplo e configure suas chaves:

```bash
copy .env.example .env
```

Edite o arquivo `.env` com suas chaves do Stripe Dashboard (Modo Teste):

- `STRIPE_SECRET_KEY`: sk*test*...
- `STRIPE_PUBLISHABLE_KEY`: pk*test*...

### 4. Banco de Dados e Usuário Admin

```bash
# Criar tabelas
python manage.py migrate

# Criar superusuário para acessar o /admin
python manage.py createsuperuser
```

### 5. Provisionar Catálogo no Stripe

Execute este comando para criar automaticamente os Produtos e Preços no seu Stripe:

```bash
python manage.py provisionar_catalogo
```

_Isso criará os 3 planos no seu dashboard do Stripe e salvará os IDs no banco de dados local._

---

## 🔄 Testando Webhooks (Essencial)

Para que o acesso seja liberado após o pagamento em `localhost`, você precisa encaminhar os eventos do Stripe para seu ambiente local.

1. **Login no Stripe CLI**:

   ```bash
   stripe login
   ```

2. **Iniciar o listener**:

   ```bash
   stripe listen --forward-to localhost:8000/stripe/webhook/
   ```

3. **Copiar o Webhook Secret**:
   O comando acima exibirá uma chave de assinatura (`whsec_...`).
   Copie essa chave e cole no seu arquivo `.env` na variável:
   `STRIPE_WEBHOOK_SECRET=whsec_...`

**Nota:** Mantenha o terminal do `stripe listen` aberto enquanto testa os pagamentos.

---

## ▶️ Rodando o Projeto

1. Inicie o servidor:

   ```bash
   python manage.py runserver
   ```

2. Acesse: [http://localhost:8000](http://localhost:8000)

### Cartões de Teste Stripe

Use estes dados no checkout para simular pagamentos:

- **Número**: `4242 4242 4242 4242`
- **Validade**: Qualquer data futura
- **CVV**: Qualquer 3 dígitos

---

## 📦 Estrutura do Projeto

```
web/
├── config/              # Configurações do projeto
├── pagamentos/          # App principal
│   ├── management/      # Scripts (provisionar catálogo)
│   ├── servicos/        # Lógica isolada do Stripe
│   ├── templates/       # HTML (Bootstrap 4)
│   ├── decoradores_acesso.py  # Controle de permissões
│   └── views.py         # Lógica de views e webhook
├── static/              # Arquivos estáticos
└── manage.py
```

## ✅ Checklist de Produção

Antes de ir para produção:

1. Alterar `DEBUG=False` no `.env`
2. Configurar `ALLOWED_HOSTS` com seu domínio
3. Usar chaves de **Produção** (Live Mode) do Stripe
4. Configurar Webhook real no Dashboard do Stripe apontando para `https://seu-dominio.com/stripe/webhook/`
5. Trocar Banco de Dados para PostgreSQL
6. Configurar servidor WSGI (Gunicorn)
