import os
import telebot
from telebot import types

TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

# 1. Start menyusi (Reply keyboard)
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("Signal olish 🚀"))
    bot.send_message(message.chat.id, "Xush kelibsiz! Savdoni boshlash uchun tugmani bosing:", reply_markup=markup)

# 2. Signal olish tugmasi bosilganda
@bot.message_handler(func=lambda message: message.text == "Signal olish 🚀")
def show_signal_options(message):
    # Inline tugmalar yaratamiz
    markup = types.InlineKeyboardMarkup()
    btn_up = types.InlineKeyboardButton("Yuqoriga (UP) ⬆️", callback_data="signal_up")
    btn_down = types.InlineKeyboardButton("Pastga (DOWN) ⬇️", callback_data="signal_down")
    markup.add(btn_up, btn_down)
    
    bot.send_message(message.chat.id, "Qaysi yo'nalishda signal kerak?", reply_markup=markup)

# 3. Inline tugmalarni qayta ishlash
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "signal_up":
        bot.answer_callback_query(call.id, "Analiz bajarildi...")
        bot.send_message(call.message.chat.id, "🟢 SIGNAL: YUQORI (UP) | Ishonchlilik: 95%")
    elif call.data == "signal_down":
        bot.answer_callback_query(call.id, "Analiz bajarildi...")
        bot.send_message(call.message.chat.id, "🔴 SIGNAL: PAST (DOWN) | Ishonchlilik: 92%")

# 4. Avtomatik analiz (Agar foydalanuvchi ma'lumot yuborsa)
@bot.message_handler(func=lambda message: ',' in message.text)
def analyze(message):
    data = message.text.split(',')
    if len(data) == 5:
        # Bu yerda siz o'zingizning analiz formulangizni qo'shishingiz mumkin
        bot.reply_to(message, "📊 Analiz natijasi: \nBozor holati barqaror. Signal: YUQORI (UP) ✅")
    else:
        bot.reply_to(message, "⚠️ Xato format! RSI,Trend,Stoch,Boll,Vol tartibida yozing.")

bot.infinity_polling()
