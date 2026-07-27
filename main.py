from telegram import Update
from telegram.ext import (
    Application,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = "8825200843:AAE1NuHCZPeku5ZGeHS5uU7XE0CZ0cIt7HQ"
CHAT_ID = "@OfertasVareiShop_Oficial"


async def receber_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    link = update.message.text.strip()

    # TODO:
    # Aqui você deve consultar a API da Shopee ou Mercado Livre
    # usando o link recebido.
    #
    # Exemplo:
    # nome_produto = resultado["title"]
    # preco = resultado["price"]

    nome_produto = "Nome do Produto"
    preco = "R$ 0,00"

    mensagem = f"""
🔥 <b>VAREISHOP OFERTAS</b>

📦 <b>{nome_produto}</b>

💰 <b>Preço:</b> {preco}

🛒 <b>Comprar:</b>
{link}

⚡ Aproveite antes que acabe!
"""

    await context.bot.send_message(
        chat_id=CHAT_ID,
        text=mensagem,
        parse_mode="HTML"
    )


app = Application.builder().token(TOKEN).build()

app.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND, receber_link)
)

print("Bot iniciado!")

app.run_polling()
