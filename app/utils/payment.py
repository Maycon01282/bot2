from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def create_payment_options():
    keyboard = [
        [InlineKeyboardButton("R$ 10,00", callback_data="pay_10")],
        [InlineKeyboardButton("R$ 20,00", callback_data="pay_20")],
        [InlineKeyboardButton("R$ 50,00", callback_data="pay_50")],
        [InlineKeyboardButton("R$ 100,00", callback_data="pay_100")],
    ]
    return InlineKeyboardMarkup(keyboard)
