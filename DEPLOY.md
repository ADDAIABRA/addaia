# Guia de Deploy no PythonAnywhere

Este guia descreve os passos necessários para hospedar a aplicação **Datarize** no [PythonAnywhere](https://www.pythonanywhere.com/).

## 1. Preparação do Ambiente Local

Certifique-se de que o seu `requirements.txt` está atualizado.

```bash
pip freeze > requirements.txt
```

## 2. Upload do Código

Você pode subir o código via Git (recomendado) ou via painel "Files" do PythonAnywhere.

### Via Git:

No terminal do PythonAnywhere:

```bash
git clone https://github.com/seu-usuario/py_datarize.git
cd py_datarize/web
```

## 3. Configuração do Ambiente Virtual (Virtualenv)

No terminal do PythonAnywhere, crie um ambiente virtual para isolar as dependências:

```bash
mkvirtualenv --python=/usr/bin/python3.10 datarize-venv
pip install -r requirements.txt
```

_(Certifique-se de usar a versão do Python compatível com seu projeto, ex: 3.10 ou 3.11)_

## 4. Configuração das Variáveis de Ambiente (.env)

O PythonAnywhere não carrega o arquivo `.env` automaticamente. O projeto utiliza `python-decouple`.

Crie um arquivo `.env` dentro da pasta `web/` no PythonAnywhere:

```bash
nano .env
```

Adicione as configurações de produção:

```env
SECRET_KEY=sua-chave-secreta-de-producao
DEBUG=False
ALLOWED_HOSTS=seu-usuario.pythonanywhere.com
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
DOMINIO_BASE=https://seu-usuario.pythonanywhere.com
GROQ_API_KEY=gsk_...
```

## 5. Configuração da Web App no PythonAnywhere

No painel **Web** do PythonAnywhere:

1.  **Add a new web app**: Selecione "Manual Configuration" e escolha a versão do Python usada no virtualenv.
2.  **Virtualenv**: Insira o caminho para o seu ambiente criado (ex: `/home/seu-usuario/.virtualenvs/datarize-venv`).
3.  **Source Code**: `/home/seu-usuario/py_datarize/web`
4.  **Working Directory**: `/home/seu-usuario/py_datarize/web`

### Editar o arquivo WSGI

Clique no link em **"WSGI configuration file"** e substitua o conteúdo pelo seguinte (ajustando os caminhos):

```python
import os
import sys

# Caminho do projeto
path = '/home/seu-usuario/py_datarize/web'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'web.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

## 6. Arquivos Estáticos

No painel **Web**, vá até a seção **Static Files** e adicione:

- **URL**: `/static/`
- **Directory**: `/home/seu-usuario/py_datarize/web/staticfiles`

Em seguida, no terminal:

```bash
python manage.py collectstatic
```

## 7. Banco de Dados e Migrações

Se for usar SQLite (padrão atual do projeto):

```bash
python manage.py migrate
python manage.py createsuperuser
```

_Nota: Se desejar usar MySQL (oferecido pelo PythonAnywhere), você deve alterar o `DATABASES` no `settings.py` e configurar o banco no painel **Databases** do PythonAnywhere._

## 8. Mudanças Importantes para Produção

1.  **DEBUG=False**: Nunca rode em produção com `DEBUG=True`.
2.  **ALLOWED_HOSTS**: Deve conter o domínio final.
3.  **Segurança de Cookies (Opcional mas recomendado)**:
    No `settings.py` de produção, adicione:
    ```python
    if not DEBUG:
        CSRF_COOKIE_SECURE = True
        SESSION_COOKIE_SECURE = True
        SECURE_SSL_REDIRECT = True
    ```
4.  **Stripe Webhooks**: Lembre-se de atualizar a URL do Webhook no painel do Stripe para apontar para o seu domínio no PythonAnywhere.

## 9. Finalização

Vá no painel **Web** e clique no botão **Reload**. Sua aplicação deve estar online!
