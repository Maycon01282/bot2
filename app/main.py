import os
import logging
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Carregar variáveis de ambiente
load_dotenv()

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Handlers
async def start(update: Update, context: CallbackContext):
    keyboard = [
        ['👤 Perfil', '💳 Adicionar Saldo'],
        ['📞 Suporte', '📝 Termos de Uso']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "🌟 *Latina Store | Telas Streaming* 🌟\n\n"
        "Bem-vindo à melhor plataforma de streaming!",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: CallbackContext):
    text = update.message.text
    
    if text == '👤 Perfil':
        await show_profile(update, context)
    elif text == '💳 Adicionar Saldo':
        await add_balance(update, context)
    elif text == '📞 Suporte':
        await update.message.reply_text("📞 Suporte: contato@latinastore.com")
    elif text == '📝 Termos de Uso':
        await update.message.reply_text("Leia nossos termos em: ...")

async def show_profile(update: Update, context: CallbackContext):
    profile_text = (
        "👤 *Seu Perfil*\n\n"
        "• *Nome:* Dog Dos Links\n"
        "• *ID:* 725009062\n"
        "• *Saldo Atual:* R$0.00\n"
        "• *Pontos de Indicação:* 0.00\n"
        "• *Pessoas indicadas:* 0"
    )
    await update.message.reply_text(profile_text, parse_mode='Markdown')

async def add_balance(update: Update, context: CallbackContext):
    from app.utils.payment import create_payment_options
    await update.message.reply_text(
        "💳 *Adicionar Saldo*\n\nEscolha o valor:",
        parse_mode='Markdown',
        reply_markup=create_payment_options()
    )

def main():
    # Obter token do bot
    TOKEN = os.getenv('TELEGRAM_TOKEN')
    
    if not TOKEN:
        logger.error("Token do Telegram não encontrado!")
        return

    # Criar aplicação
    application = Application.builder().token(TOKEN).build()
    
    # Adicionar handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Modo de desenvolvimento (polling)
    application.run_polling()

if __name__ == '__main__':
    main()
