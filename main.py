import os
import telebot
from telebot import types

# Render'dagi Environment Variable'dan tokenni o'qiydi
TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=False, resize_keyboard=True)
    btn1 = types.KeyboardButton("Signal olish 🚀")
    markup.add(btn1)
    bot.send_message(message.chat.id, "Salom! Savdo uchun tayyormisiz? Tugmani bosing:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Signal olish 🚀")
def ask_params(message):
    bot.send_message(message.chat.id, "Tushundim. Analiz uchun raqamlarni shu formatda yuboring:\nRSI,Trend,Stoch,Boll,Vol")

@bot.message_handler(func=lambda message: ',' in message.text)
def analyze(message):
    try:
        data = message.text.split(',')
        if len(data) == 5:
            bot.reply_to(message, "🟢 SIGNAL: YUQORI (UP) | Ball: 5/5")
        else:
            bot.reply_to(message, "Xatolik! 5 ta qiymat kiriting.")
    except Exception as e:
        bot.reply_to(message, f"Xatolik yuz berdi: {e}")

bot.polling()
