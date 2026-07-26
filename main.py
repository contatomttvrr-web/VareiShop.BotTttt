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

# Função para verificar se é um link válido
def is_valid_link(text):
    """Verifica se o texto contém um link válido"""
    url_pattern = re.compile(
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+])+'
    )
    return bool(url_pattern.search(text))

# Função para extrair o link da mensagem
def extract_link(text):
    """Extrai o primeiro link da mensagem"""
    url_pattern = re.compile(
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+])+'
    )
    match = url_pattern.search(text)
    return match.group(0) if match else None

# Função para criar mensagem personalizada
def create_offer_message(link):
    """Cria a mensagem formatada com o link"""
    message = f"""🔥 VAREISHOP OFERTAS 🔥

🛒 Promoção Imperdível!

👉 {link}

⚡ Aproveite antes que acabe!"""
    return message

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Responde ao comando /start"""
    welcome_message = """🤖 Olá! Bem-vindo ao VareiShop Ofertas Bot!

Envie um link de afiliado e eu publicarei automaticamente no grupo!

📌 Como usar:
1. Copie um link de afiliado (Shopee, Mercado Livre, etc.)
2. Cole aqui e envie
3. Pronto! A mensagem será publicada no grupo

🔗 Links de exemplo:
- https://s.shopee.com.br/xxxxx
- https://www.mercadolivre.com.br/xxxxx

⚡ Rápido e automático!"""
    
    await update.message.reply_text(welcome_message)

# Comando /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Responde ao comando /help"""
    help_text = """📖 Como usar o VareiShopBot:

1️⃣ Envie um link de afiliado
2️⃣ O bot vai criar uma mensagem bonita
3️⃣ A mensagem será publicada no grupo automaticamente

⚠️ Importante:
- Apenas links são aceitos
- O bot precisa ser administrador do grupo
- A mensagem é publicada instantaneamente

💡 Dica: Você pode enviar apenas o link ou uma mensagem com link.

❓ Dúvidas? Entre em contato com o administrador."""
    
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
        
        # Verifica se contém um link
        if not is_valid_link(user_message):
            await update.message.reply_text(
                "❌ Por favor, envie apenas um link de afiliado válido!\n\n"
                "Exemplo: https://s.shopee.com.br/xxxxx"
            )
            return
        
        # Extrai o link
        link = extract_link(user_message)
        if not link:
            await update.message.reply_text(
                "❌ Não foi possível identificar o link. Tente novamente!"
            )
            return
        
        # Cria a mensagem personalizada
        offer_message = create_offer_message(link)
        
        # Adiciona botão de confirmação (opcional)
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
        
        # Confirma para o usuário que enviou
        await update.message.reply_text(
            "✅ Oferta publicada com sucesso no grupo!\n\n"
            "🔗 Link enviado: " + link
        )
        
        logger.info(f"Usuário {user.username} publicou uma oferta: {link}")
        
    except Exception as e:
        logger.error(f"Erro ao processar mensagem: {e}")
        await update.message.reply_text(
            "❌ Ocorreu um erro ao publicar a oferta. Tente novamente!"
        )

# Função para erro
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Trata erros do bot"""
    logger.error(f"Update {update} causou erro {context.error}")
    
    if update and update.message:
        await update.message.reply_text(
            "⚠️ Ocorreu um erro inesperado. O administrador foi notificado."
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
