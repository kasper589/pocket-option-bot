import os
import telebot
from telebot import types

TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

# Foydalanuvchi tanlovlarini saqlash uchun lug'at
user_data = {}

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("Signal olish 🚀"))
    bot.send_message(message.chat.id, "Xush kelibsiz! Analizni boshlash uchun tugmani bosing.", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Signal olish 🚀")
def step1(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("EUR/USD", callback_data="pair_eurusd"),
               types.InlineKeyboardButton("BTC/USD", callback_data="pair_btcusd"))
    bot.send_message(message.chat.id, "1. Valyuta juftligini tanlang:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    
    if call.data.startswith("pair_"):
        user_data[chat_id] = {"pair": call.data.split("_")[1]}
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("1 min", callback_data="time_1"),
                   types.InlineKeyboardButton("5 min", callback_data="time_5"))
        bot.edit_message_text("2. Vaqt (M) ni tanlang:", chat_id, call.message.message_id, reply_markup=markup)

    elif call.data.startswith("time_"):
        pair = user_data[chat_id]["pair"]
        time = call.data.split("_")[1]
        
        # Bu yerda analiz formulangiz ishlaydi (hozircha shartli)
        result = "🟢 YUQORI (UP)" if "eur" in pair else "🔴 PAST (DOWN)"
        
        bot.edit_message_text(f"📊 ANALIZ NATIJASI:\n\nJuftlik: {pair.upper()}\nVaqt: {time} min\nSignal: {result}\n\nAnaliz tugallandi!", 
                              chat_id, call.message.message_id)

bot.infinity_polling()
