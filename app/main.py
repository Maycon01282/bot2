from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.constants import ParseMode
import os
import logging
from mercadopago import SDK
import json

# Configuração inicial
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurações do Telegram
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')

# Configurações do Mercado Pago
MP_ACCESS_TOKEN = os.environ.get('MP_ACCESS_TOKEN')
mercadopago = SDK(MP_ACCESS_TOKEN)

# Criar aplicação do Telegram
telegram_app = Application.builder().token(TELEGRAM_TOKEN).build()

# Handler para o comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_text(
        f"Olá {user.first_name}! 👋\n\n"
        "Bem-vindo à nossa loja! Aqui você pode:\n"
        "• Ver nossos produtos\n"
        "• Fazer pedidos\n"
        "• Pagar com Mercado Pago\n\n"
        "Use /produtos para ver o que temos disponível."
    )

# Handler para listar produtos
async def list_products(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    products = [
        {"name": "Produto 1", "price": 50.00},
        {"name": "Produto 2", "price": 75.00},
        {"name": "Produto 3", "price": 100.00}
    ]
    
    message = "📦 Nossos Produtos:\n\n"
    for i, product in enumerate(products, 1):
        message += f"{i}. {product['name']} - R$ {product['price']:.2f}\n"
    
    message += "\nPara comprar, digite /comprar seguido do número do produto."
    await update.message.reply_text(message)

# Handler para criar preferência de pagamento
async def create_preference(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        preference_data = {
            "items": [
                {
                    "title": "Produto Teste",
                    "quantity": 1,
                    "unit_price": 100.00
                }
            ],
            "back_urls": {
                "success": "https://seu-site.com/success",
                "failure": "https://seu-site.com/failure",
                "pending": "https://seu-site.com/pending"
            },
            "auto_return": "approved"
        }
        
        preference = mercadopago.preference().create(preference_data)
        payment_url = preference["response"]["init_point"]
        
        await update.message.reply_text(
            f"💳 Para finalizar sua compra, acesse:\n{payment_url}\n\n"
            "Após o pagamento, você receberá a confirmação aqui mesmo!"
        )
        
    except Exception as e:
        logger.error(f"Erro ao criar preferência: {e}")
        await update.message.reply_text("❌ Ocorreu um erro ao processar sua solicitação.")

# Registrar handlers
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CommandHandler("produtos", list_products))
telegram_app.add_handler(CommandHandler("comprar", create_preference))

# Handler para webhook do Mercado Pago
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.json
        logger.info(f"Webhook recebido: {data}")
        
        if data.get('type') == 'payment':
            payment_id = data['data']['id']
            payment_info = mercadopago.payment().get(payment_id)
            
        return jsonify({"status": "success"}), 200
    except Exception as e:
        logger.error(f"Erro no webhook: {e}")
        return jsonify({"status": "error"}), 500

# Handler para mensagens do Telegram
@app.route('/webhook-telegram', methods=['POST'])
async def webhook_telegram():
    try:
        # Processar a atualização
        update = Update.de_json(request.get_json(force=True), telegram_app.bot)
        await telegram_app.process_update(update)
        
        return jsonify({"status": "success"}), 200
    except Exception as e:
        logger.error(f"Erro no webhook do Telegram: {e}")
        return jsonify({"status": "error"}), 500

# Rota inicial
@app.route('/')
def index():
    return "Bot do Telegram está funcionando!"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
