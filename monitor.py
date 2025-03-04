import os
import time
import requests
import threading
from flask import Flask

# Pegando os valores do ambiente do Render
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Configuração do servidor a ser monitorado
MERCADO_SERVER_URL = "https://0946-170-245-82-133.ngrok-free.app -> http://localhost:5000"  # Substitua pelo IP correto

def send_telegram(message):
    """Envia uma notificação para o Telegram"""
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
        try:
            response = requests.post(url, data=data)
            print(f"[INFO] Mensagem enviada: {message}")
        except Exception as e:
            print(f"[ERRO] Falha ao enviar mensagem: {e}")
    else:
        print("[ERRO] Token do Telegram ou Chat ID não configurados!")

def is_server_online():
    """Verifica se o servidor do mercadinho está online"""
    try:
        response = requests.get(MERCADO_SERVER_URL, timeout=5)
        if response.status_code == 200:
            print("[INFO] O servidor está respondendo corretamente.")
            return True
        else:
            print(f"[ERRO] O servidor respondeu com código {response.status_code}.")
            return False
    except requests.exceptions.ConnectionError:
        print("[ALERTA] Erro de conexão - O servidor está offline!")
        return False
    except requests.exceptions.Timeout:
        print("[ALERTA] Timeout - O servidor pode estar offline!")
        return False
    except requests.exceptions.RequestException as e:
        print(f"[ERRO] Falha ao acessar o servidor: {e}")
        return False

def monitor_loop():
    """Loop infinito para monitoramento"""
    global internet_off
    internet_off = None  # Inicializamos como None para evitar notificações falsas

    print("[INFO] Iniciando monitoramento contínuo...")

    while True:
        print("[INFO] Verificando status do servidor do mercadinho...")
        online = is_server_online()
        print(f"[INFO] Verificação concluída. Status do servidor: {'Online' if online else 'Offline'}")

        if online and internet_off is not False:  
            send_telegram("✅ A internet do mercadinho voltou!")
            print("[INFO] Enviada notificação: A internet voltou.")
            internet_off = False
        elif not online and internet_off is not True:
            send_telegram("🚨 A internet do mercadinho caiu! Verifique a conexão.")
            print("[INFO] Enviada notificação: A internet caiu!")
            internet_off = True
        else:
            print("[INFO] Nenhuma mudança detectada, continuando monitoramento...")

        time.sleep(60)  # Verifica a cada 1 minuto

# Criar um Web Server para evitar que o Render pare
app = Flask(__name__)

@app.route('/')
def home():
    return "Monitoramento rodando!", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))  # Pega a porta do Render
    print(f"[INFO] Servidor Flask rodando na porta {port}")
    app.run(host="0.0.0.0", port=port)

# Iniciar monitoramento e Flask em threads separadas
if __name__ == "__main__":
    print("[INFO] Iniciando o servidor Flask e o monitoramento...")

    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
    monitor_thread.start()

    print("[INFO] Monitoramento iniciado com sucesso!")

    while True:
        time.sleep(10)  # Mantém o script rodando para evitar encerramento

