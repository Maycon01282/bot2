from flask import Flask, request, jsonify
from telegram import Update, Bot
from telegram.ext import Dispatcher, CommandHandler, CallbackContext
import os
import logging

# Configuração inicial
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurações
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
MP_ACCESS_TOKEN = os.environ.get('MP_ACCESS_TOKEN')

# Verificar se as variáveis de ambiente estão carregadas corretamente
if not TELEGRAM_TOKEN:
    logger.error("TELEGRAM_TOKEN não encontrado")
    raise ValueError("TELEGRAM_TOKEN não encontrado")

logger.info("Variáveis de ambiente carregadas com sucesso")

# Inicializar bot do Telegram
bot = Bot(token=TELEGRAM_TOKEN)

# Handlers
def start(update: Update, context: CallbackContext):
    try:
        user = update.effective_user
        update.message.reply_text(
            f"Olá {user.first_name}! 👋\n\n"
            "Bem-vindo à nossa loja! Use /produtos para ver nossos produtos."
        )
    except Exception as e:
        logger.error(f"Erro no handler start: {e}")

def list_products(update: Update, context: CallbackContext):
    try:
        products = [
            {"name": "Produto 1", "price": 50.00},
            {"name": "Produto 2", "price": 75.00},
            {"name": "Produto 3", "price": 100.00}
        ]
        
        message = "📦 Nossos Produtos:\n\n"
        for i, product in enumerate(products, 1):
            message += f"{i}. {product['name']} - R$ {product['price']:.2f}\n"
        
        message += "\nPara comprar, digite /comprar"
        update.message.reply_text(message)
    except Exception as e:
        logger.error(f"Erro no handler list_products: {e}")

def create_preference(update: Update, context: CallbackContext):
    try:
        update.message.reply_text(
            "💳 Para comprar, entre em contato conosco diretamente."
        )
    except Exception as e:
        logger.error(f"Erro no handler create_preference: {e}")

# Rota do webhook do Telegram
@app.route('/webhook-telegram', methods=['POST'])
def webhook_telegram():
    try:
        # Obter os dados JSON
        update_data = request.get_json(force=True)
        logger.info(f"Dados recebidos: {json.dumps(update_data)}")
        
        # Criar dispatcher para processar a atualização
        dispatcher = Dispatcher(bot, None, workers=4)
        
        # Registrar handlers
        dispatcher.add_handler(CommandHandler("start", start))
        dispatcher.add_handler(CommandHandler("produtos", list_products))
        dispatcher.add_handler(CommandHandler("comprar", create_preference))
        
        # Processar a atualização
        update = Update.de_json(update_data, bot)
        dispatcher.process_update(update)
        
        return jsonify({"status": "success"}), 200
    except Exception as e:
        logger.error(f"Erro no webhook do Telegram: {str(e)}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/')
def index():
    return "Bot do Telegram está funcionando!"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
