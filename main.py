import telebot
from telebot import types

bot = telebot.TeleBot(8800349563:AAE7He3cbqzcCKKow2ZXcZsq80vBeWgne1U)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=False, resize_keyboard=True)
    btn1 = types.KeyboardButton("Signal olish 🚀")
    markup.add(btn1)
    bot.send_message(message.chat.id, "Salom! Savdo uchun tayyormisiz? Tugmani bosing:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Signal olish 🚀")
def ask_params(message):
    bot.send_message(message.chat.id, "Tushundim. Analiz uchun raqamlarni shu formatda yuboring:\nRSI,Trend,Stoch,Boll,Vol\n\nMasalan: 30,up,20,low,high")

@bot.message_handler(func=lambda message: ',' in message.text)
def analyze(message):
    # Bu yerda sizning analiz kodingiz qoladi
    try:
        data = message.text.split(',')
        if len(data) == 5:
            # Oddiy mantiq (buni o'zingiz xohlagancha o'zgartirishingiz mumkin)
            bot.reply_to(message, "🟢 SIGNAL: YUQORI (UP) | Ball: 5/5")
        else:
            bot.reply_to(message, "Xatolik! 5 ta qiymat kiriting (Format: RSI,Trend,Stoch,Boll,Vol)")
    except:
        bot.reply_to(message, "Xatolik yuz berdi!")

bot.polling()
