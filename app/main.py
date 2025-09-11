import os
import logging
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler
from flask import Flask, request

# Carregar variáveis de ambiente
load_dotenv()

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Inicializar Flask
app = Flask(__name__)

# Handlers do Telegram
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
    keyboard = [
        [InlineKeyboardButton("R$ 10,00", callback_data="pay_10")],
        [InlineKeyboardButton("R$ 20,00", callback_data="pay_20")],
        [InlineKeyboardButton("R$ 50,00", callback_data="pay_50")],
        [InlineKeyboardButton("R$ 100,00", callback_data="pay_100")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "💳 *Adicionar Saldo*\n\nEscolha o valor:",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def handle_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text=f"Opção selecionada: {query.data}")

# Configurar aplicação do Telegram
def setup_application():
    TOKEN = os.getenv('TELEGRAM_TOKEN')
    if not TOKEN:
        raise ValueError("Token do Telegram não encontrado!")
    
    # Usar ApplicationBuilder sem criar Updater (evita o erro)
    application = Application.builder().token(TOKEN).build()
    
    # Adicionar handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(handle_callback))
    
    return application

# Criar aplicação
application = setup_application()

# Rota para webhook
@app.route('/webhook', methods=['POST'])
async def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_data = request.get_json(force=True)
        update = Update.de_json(json_data, application.bot)
        await application.process_update(update)
        return 'ok'
    return 'Bad Request', 400

# Rota para health check
@app.route('/')
def health_check():
    return "Bot está rodando via webhook!"

# Configurar webhook no startup
@app.before_first_request
def configure_webhook():
    webhook_url = os.getenv('WEBHOOK_URL')
    if webhook_url:
        # Define a URL do webhook
        application.bot.set_webhook(url=f"{webhook_url}/webhook")
        logger.info(f"Webhook configurado para: {webhook_url}/webhook")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    # Configurar webhook ao iniciar a aplicação
    webhook_url = os.getenv('WEBHOOK_URL')
    if webhook_url:
        application.bot.set_webhook(url=f"{webhook_url}/webhook")
        logger.info(f"Webhook configurado para: {webhook_url}/webhook")
    app.run(host='0.0.0.0', port=port)
