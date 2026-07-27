Redação
import os
import re
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters

# Token do bot
TOKEN = os.getenv("8825200843:AAE1NuHCZPeku5ZGeHS5uU7XE0CZ0cIt7HQ")

# Grupo ou canal onde será publicada a oferta
CHAT_ID = "@OfertasVareiShop_Oficial"

# Detecta links
LINK_REGEX = r"https?://\\S+"

async def receber_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text

    # Procura um link na mensagem
    match = re.search(LINK_REGEX, texto)
    if not match:
        await update.message.reply_text("❌ Envie apenas um link de oferta.")
        return

    link = match.group(0)

    # Mensagem personalizada
    mensagem = f"""
🔥 *VAREISHOP OFERTAS* 🔥

🛒 *Oferta Imperdível!*

💰 *Preço:* confira no link abaixo

👇 *Compre agora:*
{link}

⚡ *Aproveite antes que acabe!*

📢 Entre no nosso canal para mais promoções:
@OfertasVareiShop_Oficial
"""

    # Botão "Ver Oferta"
    teclado = InlineKeyboardMarkup([
        [InlineKeyboardButton("🛒 Ver Oferta", url=link)]
    ])

    # Envia para o grupo/canal
    await context.bot.send_message(
        chat_id=CHAT_ID,
        text=mensagem,
        parse_mode="Markdown",
        reply_markup=teclado,
        disable_web_page_preview=False
    )

    # Confirma para você
    await update.message.reply_text("✅ Oferta publicada com sucesso!")

def main():
    app = Application.builder().token(TOKEN).build()

    # Escuta qualquer mensagem de texto
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receber_link))

    print("Bot iniciado...")
    app.run_polling()

if __name__ == "__main__":
    main() 
