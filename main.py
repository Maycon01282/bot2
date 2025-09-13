from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import os
import logging

# Configuração inicial
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurações
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')

if not TELEGRAM_TOKEN:
    logger.error("TELEGRAM_TOKEN não encontrado nas variáveis de ambiente")
    raise ValueError("TELEGRAM_TOKEN não encontrado")

logger.info("Variáveis de ambiente carregadas com sucesso")

# Criar aplicação do Telegram
telegram_app = Application.builder().token(TELEGRAM_TOKEN).build()

# Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.effective_user
        await update.message.reply_text(
            f"Olá {user.first_name}! 👋\n\n"
            "Bem-vindo à nossa loja! Use /produtos para ver nossos produtos."
        )
    except Exception as e:
        logger.error(f"Erro no handler start: {e}")

async def list_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        await update.message.reply_text(message)
    except Exception as e:
        logger.error(f"Erro no handler list_products: {e}")

async def create_preference(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text(
            "⚠️ Funcionalidade de compra temporariamente desativada. Estamos em manutenção."
        )
    except Exception as e:
        logger.error(f"Erro no handler create_preference: {e}")

# Registrar handlers
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CommandHandler("produtos", list_products))
telegram_app.add_handler(CommandHandler("comprar", create_preference))

@app.route('/webhook-telegram', methods=['POST'])
async def webhook_telegram():
    try:
        # Log para verificar se a requisição está chegando
        logger.info("Webhook do Telegram recebido")
        
        # Obter os dados JSON
        json_data = request.get_json(force=True)
        logger.info(f"Dados recebidos: {json_data}")
        
        # Processar a atualização
        update = Update.de_json(json_data, telegram_app.bot)
        await telegram_app.process_update(update)
        
        return jsonify({"status": "success"}), 200
    except Exception as e:
        logger.error(f"Erro no webhook do Telegram: {e}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/')
def index():
    return "Bot do Telegram está funcionando!"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
