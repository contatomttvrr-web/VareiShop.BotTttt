import os
import re
import logging
import requests
from bs4 import BeautifulSoup
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

# Função para extrair informações da Amazon
def extract_amazon_info(url):
    """Tenta extrair nome e preço de um link da Amazon"""
    try:
        # Headers para simular um navegador
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Faz a requisição
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Tenta pegar o nome do produto
        nome = None
        title_tag = soup.find('span', {'id': 'productTitle'})
        if title_tag:
            nome = title_tag.get_text().strip()
        else:
            # Tenta outro seletor
            title_tag = soup.find('h1', {'class': 'a-size-large'})
            if title_tag:
                nome = title_tag.get_text().strip()
        
        # Tenta pegar o preço
        preco = None
        # Tenta vários seletores de preço da Amazon
        price_selectors = [
            {'id': 'priceblock_ourprice'},
            {'id': 'priceblock_dealprice'},
            {'id': 'price_inside_buybox'},
            {'class': 'a-price-whole'}
        ]
        
        for selector in price_selectors:
            if 'id' in selector:
                price_tag = soup.find('span', {'id': selector['id']})
            elif 'class' in selector:
                price_tag = soup.find('span', {'class': selector['class']})
            else:
                continue
                
            if price_tag:
                preco = price_tag.get_text().strip()
                # Limpa o preço
                preco = re.sub(r'[^\d,.]', '', preco)
                if preco:
                    preco = f"R$ {preco}"
                    break
        
        # Se não achou preço, tenta outro método
        if not preco:
            price_tag = soup.find('span', {'class': 'a-price'})
            if price_tag:
                whole = price_tag.find('span', {'class': 'a-price-whole'})
                fraction = price_tag.find('span', {'class': 'a-price-fraction'})
                if whole and fraction:
                    preco = f"R$ {whole.get_text().strip()},{fraction.get_text().strip()}"
        
        return nome, preco
        
    except Exception as e:
        logger.error(f"Erro ao extrair informações: {e}")
        return None, None

# Função para extrair o link da mensagem
def extract_link(text):
    """Extrai o link da mensagem"""
    url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+])+')
    match = url_pattern.search(text)
    return match.group(0) if match else None

# Função para criar mensagem personalizada
def create_offer_message(nome, preco, link):
    """Cria a mensagem formatada"""
    if not nome:
        nome = "Produto"
    if not preco:
        preco = "Preço não disponível"
        
    message = f"""🛒 OFERTA VAREISHOP

🎮 {nome}

💰 {preco}

👉 {link}

📢 ANÚNCIO"""
    return message

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Responde ao comando /start"""
    welcome_message = """🤖 Olá! Bem-vindo ao VareiShop Ofertas Bot!

📝 Como funciona:

Basta enviar um LINK de produto da Amazon e eu:
1️⃣ Busco o nome do produto
2️⃣ Busco o preço
3️⃣ Publico no grupo automaticamente!

📌 Exemplo:
https://www.amazon.com.br/PlayStation-Controle-DualSense-Branco/dp/B0E1T03AQa

✅ Tudo automático!"""
    
    await update.message.reply_text(welcome_message)

# Comando /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Responde ao comando /help"""
    help_text = """📖 Como usar o VareiShopBot:

1️⃣ Copie um link de produto da Amazon

2️⃣ Cole e envie para o bot

3️⃣ O bot vai pegar nome e preço automaticamente

4️⃣ A mensagem será publicada no grupo

⚠️ Importante:
- Funciona com links da Amazon
- Pode demorar alguns segundos para processar
- Se não conseguir pegar as informações, use o formato manual:    
    await update.message.reply_text(help_text)

# Função para processar mensagens
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processa as mensagens enviadas ao bot"""
    try:
        user_message = update.message.text
        user = update.effective_user
        
        # Verifica se é uma mensagem válida
        if not user_message:
            return
        
        # Extrai o link
        link = extract_link(user_message)
        
        # Se não encontrou link, avisa
        if not link:
            await update.message.reply_text(
                "❌ Envie um link válido!\n\n"
                "Exemplo: https://www.amazon.com.br/...\n\n"
                "Digite /help para ajuda."
            )
            return
        
        # Avisa que está processando
        await update.message.reply_text("⏳ Buscando informações do produto...")
        
        # Tenta extrair informações da Amazon
        nome, preco = extract_amazon_info(link)
        
        # Se não conseguiu extrair, pergunta ao usuário
        if not nome or not preco:
            await update.message.reply_text(
                "⚠️ Não consegui buscar as informações automaticamente.\n\n"
                "Por favor, envie a oferta neste formato:\n"
                "`Nome do Produto | Preço | Link`\n\n"
                "Exemplo:\n"
                "`PlayStation DualSense | R$ 449,90 | https://link...`"
            )
            return
        
        # Cria a mensagem personalizada
        offer_message = create_offer_message(nome, preco, link)
        
        # Adiciona botões
        keyboard = [
            [InlineKeyboardButton("🛒 Ver Oferta", url=link)],
            [InlineKeyboardButton("📱 Canal de Ofertas", url="https://t.me/OfertasVareiShop_Oficial")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Envia a mensagem para o grupo
        await context.bot.send_message(
            chat_id=CHAT_ID,
            text=offer_message,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
        
        # Confirma para o usuário
        await update.message.reply_text(
            f"✅ Oferta publicada com sucesso!\n\n"
            f"📦 Produto: {nome}\n"
            f"💰 Preço: {preco}"
        )
        
        logger.info(f"Usuário {user.username} publicou: {nome}")
        
    except Exception as e:
        logger.error(f"Erro ao processar mensagem: {e}")
        await update.message.reply_text(
            "❌ Ocorreu um erro. Tente novamente!"
        )

# Função para erro
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Trata erros do bot"""
    logger.error(f"Update {update} causou erro {context.error}")
    
    if update and update.message:
        await update.message.reply_text(
            "⚠️ Ocorreu um erro. Tente novamente!"
        )

# Função principal
def main():
    """Função principal do bot"""
    print("🤖 Iniciando VareiShopBot...")
    print(f"📢 CHAT_ID: {CHAT_ID}")
    
    # Cria a aplicação
    application = Application.builder().token(TOKEN).build()
    
    # Adiciona handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)
    
    # Inicia o bot
    print("✅ Bot está rodando!")
    print("🔄 Aguardando mensagens...")
    
    # Inicia o polling
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
