import sys
import os

# Adicionar o shim do imghdr ao path antes de importar telegram
sys.path.insert(0, os.path.dirname(__file__))

# Forçar a criação do módulo imghdr se não existir
try:
    import imghdr
except ImportError:
    # Criar um módulo imghdr simulado
    import types
    imghdr = types.ModuleType('imghdr')
    imghdr.what = lambda file, h=None: None
    sys.modules['imghdr'] = imghdr

from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import logging
from mercadopago import SDK

# Configuração inicial
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurações
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
MP_ACCESS_TOKEN = os.environ.get('MP_ACCESS_TOKEN')

# Verificar se as variáveis de ambiente estão carregadas corretamente
if not TELEGRAM_TOKEN:
    logger.error("TELEGRAM_TOKEN não encontrado nas variáveis de ambiente")
    raise ValueError("TELEGRAM_TOKEN não encontrado")

if not MP_ACCESS_TOKEN:
    logger.error("MP_ACCESS_TOKEN não encontrado nas variáveis de ambiente")
    raise ValueError("MP_ACCESS_TOKEN não encontrado")

logger.info("Variáveis de ambiente carregadas com sucesso")

# Inicializar Mercado Pago
try:
    mercadopago = SDK(MP_ACCESS_TOKEN)
    logger.info("Mercado Pago SDK inicializado com sucesso")
except Exception as e:
    logger.error(f"Erro ao inicializar Mercado Pago SDK: {e}")
    raise

# Criar aplicação do Telegram
telegram_app = Application.builder().token(TELEGRAM_TOKEN).build()

# Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"Olá {user.first_name}! 👋\n\n"
        "Bem-vindo à nossa loja! Use /produtos para ver nossos produtos."
    )

async def list_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    products = [
        {"name": "Produto 1", "price": 50.00},
        {"name": "Produto 2", "price": 75.00},
        {"name": "Produto 3", "price": 100.00}
    ]
    
    message = "📦 Nossos Produtos:\n\n"
    for i, product in enumerate(products, 1):
        message += f"{i}. {product['name']} - R$ {product['price']:.2f}\n"
    
    message += "\nPara comprar, digite /comprar"
    await update.message.reply_text(message)

async def create_preference(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        preference_data = {
            "items": [{
                "title": "Produto Teste",
                "quantity": 1,
                "unit_price": 100.00
            }],
            "back_urls": {
                "success": "https://your-app.onrender.com/success",
                "failure": "https://your-app.onrender.com/failure", 
                "pending": "https://your-app.onrender.com/pending"
            },
            "auto_return": "approved"
        }
        
        preference = mercadopago.preference().create(preference_data)
        payment_url = preference["response"]["init_point"]
        
        await update.message.reply_text(
            f"💳 Para finalizar sua compra, acesse:\n{payment_url}"
        )
        
    except Exception as e:
        logger.error(f"Erro: {e}")
        await update.message.reply_text("❌ Ocorreu um erro.")

# Registrar handlers
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CommandHandler("produtos", list_products))
telegram_app.add_handler(CommandHandler("comprar", create_preference))

# Rotas Flask
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.json
        logger.info(f"Webhook recebido: {data}")
        return jsonify({"status": "success"}), 200
    except Exception as e:
        logger.error(f"Erro no webhook: {e}")
        return jsonify({"status": "error"}), 500

@app.route('/webhook-telegram', methods=['POST'])
async def webhook_telegram():
    try:
        update = Update.de_json(request.get_json(force=True), telegram_app.bot)
        await telegram_app.process_update(update)
        return jsonify({"status": "success"}), 200
    except Exception as e:
        logger.error(f"Erro no webhook do Telegram: {e}")
        return jsonify({"status": "error"}), 500

@app.route('/')
def index():
    return "Bot do Telegram está funcionando!"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
