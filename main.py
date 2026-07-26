import os
import re
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Configuração de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Variáveis de ambiente
TOKEN = os.environ.get('BOT_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

# Verifica se as variáveis estão configuradas
if not TOKEN:
    raise ValueError("BOT_TOKEN não configurado!")
if not CHAT_ID:
    raise ValueError("CHAT_ID não configurado!")

# Função para extrair informações da mensagem
def extract_info(text):
    """Extrai nome, preço, cupom e link da mensagem"""
    # Tenta separar por |
    parts = text.split('|')
    
    # Remove espaços extras
    parts = [p.strip() for p in parts]
    
    # Se tem 4 partes: nome, preço, cupom, link
    if len(parts) == 4:
        nome = parts[0]
        preco = parts[1]
        cupom = parts[2]
        link = parts[3]
        
        # Verifica se o link é válido
        if not link.startswith('http'):
            link = 'https://' + link
            
        return nome, preco, cupom, link
    
    # Se não tem 4 partes, tenta extrair link sozinho
    else:
        # Procura link na mensagem
        url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+])+')
        match = url_pattern.search(text)
        
        if match:
            link = match.group(0)
            # Pega o resto como nome
            nome = text.replace(link, '').strip()
            if not nome:
                nome = "Produto"
            return nome, "Preço não informado", "Sem cupom", link
        else:
            return None, None, None, None

# Função para criar mensagem personalizada
def create_offer_message(nome, preco, cupom, link):
    """Cria a mensagem formatada"""
    message = f"""🛒 OFERTA VAREISHOP

🎮 {nome}

💰 {preco}

🎫 Cupom: {cupom}

👉 {link}

📢 ANÚNCIO"""
    return message

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Responde ao comando /start"""
    welcome_message = """🤖 Olá! Bem-vindo ao VareiShop Ofertas Bot!

📝 Como enviar uma oferta:

Envie uma mensagem neste formato:
