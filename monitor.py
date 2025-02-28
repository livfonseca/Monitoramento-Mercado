import time
import requests

# Configuração do servidor a ser monitorado
MERCADO_SERVER_URL = "http://192.168.1.100:5000/"  # Troque pelo IP correto

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
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

# Loop infinito para monitorar a cada 1 minuto
internet_off = False
while True:
    if is_server_online():
        if internet_off:
            send_telegram("✅ A internet do mercadinho voltou!")
            internet_off = False
    else:
        if not internet_off:
            send_telegram("🚨 A internet do mercadinho caiu! Verifique a conexão.")
            internet_off = True
    time.sleep(60)  # Verifica a cada 1 minuto
