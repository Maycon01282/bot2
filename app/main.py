import os
import logging
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler

# Carregar variáveis de ambiente
load_dotenv()

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Handlers
def start(update: Update, context: CallbackContext):
    keyboard = [
        ['👤 Perfil', '💳 Adicionar Saldo'],
        ['📞 Suporte', '📝 Termos de Uso']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    update.message.reply_text(
        "🌟 *Latina Store | Telas Streaming* 🌟\n\n"
        "Bem-vindo à melhor plataforma de streaming!",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

def handle_message(update: Update, context: CallbackContext):
    text = update.message.text
    
    if text == '👤 Perfil':
        show_profile(update, context)
    elif text == '💳 Adicionar Saldo':
        add_balance(update, context)
    elif text == '📞 Suporte':
        update.message.reply_text("📞 Suporte: contato@latinastore.com")
    elif text == '📝 Termos de Uso':
        update.message.reply_text("Leia nossos termos em: ...")

def show_profile(update: Update, context: CallbackContext):
    profile_text = (
        "👤 *Seu Perfil*\n\n"
        "• *Nome:* Dog Dos Links\n"
        "• *ID:* 725009062\n"
        "• *Saldo Atual:* R$0.00\n"
        "• *Pontos de Indicação:* 0.00\n"
        "• *Pessoas indicadas:* 0"
    )
    update.message.reply_text(profile_text, parse_mode='Markdown')

def add_balance(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("R$ 10,00", callback_data="pay_10")],
        [InlineKeyboardButton("R$ 20,00", callback_data="pay_20")],
        [InlineKeyboardButton("R$ 50,00", callback_data="pay_50")],
        [InlineKeyboardButton("R$ 100,00", callback_data="pay_100")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    update.message.reply_text(
        "💳 *Adicionar Saldo*\n\nEscolha o valor:",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

def handle_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text=f"Opção selecionada: {query.data}")

def main():
    # Obter token do bot
    TOKEN = os.getenv('TELEGRAM_TOKEN')
    
    if not TOKEN:
        logger.error("Token do Telegram não encontrado!")
        return

    # Criar updater
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # Adicionar handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    dp.add_handler(CallbackQueryHandler(handle_callback))

    # Iniciar o bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
