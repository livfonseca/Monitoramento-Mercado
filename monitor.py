import os
import time
import requests
import threading
from flask import Flask

# Configuração do servidor a ser monitorado
MERCADO_SERVER_URL = "http://192.168.1.100:5000/"  # Substitua pelo IP correto

# Configuração do Telegram
TELEGRAM_BOT_TOKEN = "SEU_BOT_TOKEN_AQUI"
TELEGRAM_CHAT_ID = "SEU_CHAT_ID_AQUI"

def send_telegram(message):
    """Envia uma notificação para o Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print(f"[ERRO] Falha ao enviar mensagem: {e}")

def is_server_online():
    """Verifica se o servidor do mercadinho está online"""
    try:
        response = requests.get(MERCADO_SERVER_URL, timeout=5)
        # Considera online apenas se responder com código 200
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        print("[ALERTA] Erro de conexão - O servidor está offline!")
        return False
    except requests.exceptions.Timeout:
        print("[ALERTA] Timeout - O servidor pode estar offline!")
        return False
    except requests.exceptions.RequestException as e:
        print(f"[ERRO] Falha ao acessar o servidor: {e}")
        return False

# Loop infinito para monitoramento
internet_off = False

while True:
    online = is_server_online()
    print(f"[INFO] Status do servidor: {'Online' if online else 'Offline'}")
    
    if online:
        if internet_off:
            send_telegram("✅ A internet do mercadinho voltou!")
            internet_off = False
    else:
        if not internet_off:
            send_telegram("🚨 A internet do mercadinho caiu! Verifique a conexão.")
            internet_off = True
    
    time.sleep(60)  # Verifica a cada 1 minuto

# Criar um Web Server para evitar que o Render pare
app = Flask(__name__)

@app.route('/')
def home():
    return "Monitoramento rodando!", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))  # Pega a porta do Render
    app.run(host="0.0.0.0", port=port)

# Iniciar monitoramento e Flask em threads separadas
monitor_thread = threading.Thread(target=monitor_loop)
monitor_thread.start()

flask_thread = threading.Thread(target=run_flask)
flask_thread.start()
