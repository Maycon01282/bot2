from flask import Flask, request, jsonify
from telegram import Update, Bot
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters, CallbackContext
import os
import logging
from mercadopago import SDK

# Configuração inicial
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurações - com verificação de variáveis de ambiente
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
MP_ACCESS_TOKEN = os.environ.get('MP_ACCESS_TOKEN')

# Verificar se as variáveis de ambiente estão carregadas corretamente
if not TELEGRAM_TOKEN:
    logger.error("TELEGRAM_TOKEN não encontrado nas variáveis de ambiente")
    raise ValueError("TELEGRAM_TOKEN não encontrado")

if not MP_ACCESS_TOKEN:
    logger.error("MP_ACCESS_TOKEN não encontrado nas variáveis de ambiente")
    raise ValueError("MP_ACCESS_TOKEN não encontrado")

logger.info(f"TELEGRAM_TOKEN: {TELEGRAM_TOKEN[:10]}...")  # Log parcial por segurança
logger.info(f"MP_ACCESS_TOKEN: {MP_ACCESS_TOKEN[:10]}...")  # Log parcial por segurança

# Inicializar Mercado Pago
try:
    mercadopago = SDK(MP_ACCESS_TOKEN)
    logger.info("Mercado Pago SDK inicializado com sucesso")
except Exception as e:
    logger.error(f"Erro ao inicializar Mercado Pago SDK: {e}")
    raise

# Criar bot do Telegram
bot = Bot(token=TELEGRAM_TOKEN)

# Handlers
def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    update.message.reply_text(
        f"Olá {user.first_name}! 👋\n\n"
        "Bem-vindo à nossa loja! Use /produtos para ver nossos produtos."
    )

def list_products(update: Update, context: CallbackContext) -> None:
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

def create_preference(update: Update, context: CallbackContext) -> None:
    try:
        preference_data = {
            "items": [{
                "title": "Produto Teste",
                "quantity": 1,
                "unit_price": 100.00
            }],
            "back_urls": {
                "success": "https://seu-site.com/success",
                "failure": "https://seu-site.com/failure",
                "pending": "https://seu-site.com/pending"
            },
            "auto_return": "approved"
        }
        
        preference = mercadopago.preference().create(preference_data)
        payment_url = preference["response"]["init_point"]
        
        update.message.reply_text(
            f"💳 Para finalizar sua compra, acesse:\n{payment_url}"
        )
        
    except Exception as e:
        logger.error(f"Erro: {e}")
        update.message.reply_text("❌ Ocorreu um erro.")

# Rotas Flask
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.json
        logger.info(f"Webhook: {data}")
        return jsonify({"status": "success"}), 200
    except Exception as e:
        logger.error(f"Erro: {e}")
        return jsonify({"status": "error"}), 500

@app.route('/webhook-telegram', methods=['POST'])
def webhook_telegram():
    try:
        # Criar dispatcher para processar a atualização
        dispatcher = Dispatcher(bot, None, workers=4)
        
        # Registrar handlers
        dispatcher.add_handler(CommandHandler("start", start))
        dispatcher.add_handler(CommandHandler("produtos", list_products))
        dispatcher.add_handler(CommandHandler("comprar", create_preference))
        
        # Processar a atualização
        update = Update.de_json(request.get_json(force=True), bot)
        dispatcher.process_update(update)
        
        return jsonify({"status": "success"}), 200
    except Exception as e:
        logger.error(f"Erro no webhook do Telegram: {e}")
        return jsonify({"status": "error"}), 500

@app.route('/')
def index():
    return "Bot funcionando!"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
