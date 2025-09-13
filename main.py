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
MP_ACCESS_TOKEN = os.environ.get('MP_ACCESS_TOKEN')

# Verificar se as variáveis de ambiente estão carregadas corretamente
if not TELEGRAM_TOKEN:
    logger.error("TELEGRAM_TOKEN não encontrado")
    raise ValueError("TELEGRAM_TOKEN não encontrado")

logger.info("Variáveis de ambiente carregadas com sucesso")

# Inicializar bot do Telegram
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
            "💳 Para comprar, entre em contato conosco diretamente."
        )
    except Exception as e:
        logger.error(f"Erro no handler create_preference: {e}")

# Registrar handlers
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CommandHandler("produtos", list_products))
telegram_app.add_handler(CommandHandler("comprar", create_preference))

# Rota do webhook do Telegram
@app.route('/webhook-telegram', methods=['POST'])
async def webhook_telegram():
    try:
        # Obter os dados JSON
        update_data = request.get_json(force=True)
        logger.info(f"Dados recebidos: {update_data}")
        
        # Processar a atualização
        update = Update.de_json(update_data, telegram_app.bot)
        await telegram_app.process_update(update)
        
        return jsonify({"status": "success"}), 200
    except Exception as e:
        logger.error(f"Erro no webhook do Telegram: {e}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/')
def index():
    return "Bot do Telegram está funcionando!"

if __name__ == '__main__':
    port_str = os.environ.get('PORT', '5000')
    # Garantir que a porta seja um número válido
    try:
        port = int(port_str)
    except ValueError:
        port = 5000  # Valor padrão se não for um número válido
        logger.warning(f"PORT inválida: '{port_str}'. Usando porta padrão: {port}")
    
    app.run(host='0.0.0.0', port=port, debug=False)
