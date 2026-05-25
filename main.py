import telebot
from flask import Flask
from threading import Thread

# Bot tokeningiz
bot = telebot.TeleBot("8893762032:AAH23-yyQib8wdRnf4tk7inW-f9SiWLMJ-8")
app = Flask('')

@app.route('/')
def home():
    return "Bot ishlamoqda!"

def run():
    app.run(host='0.0.0.0', port=8080)

t = Thread(target=run)
t.start()

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Tizim faol. Analiz uchun 5 ta parametrni vergul bilan kiriting (Format: RSI,Trend,Stoch,Boll,Vol)")

@bot.message_handler(func=lambda message: ',' in message.text)
def analyze(message):
    data = message.text.split(',')
    if len(data) != 5:
        bot.reply_to(message, "⚠️ Xatolik: 5 ta parametr kiriting (RSI,Trend,Stoch,Boll,Vol)")
        return
    try:
        rsi = float(data[0])
        trend = data[1].lower()
        stoch = float(data[2])
        boll = data[3].lower()
        vol = data[4].lower()

        up_score = (rsi < 35) + (trend == 'up') + (stoch < 30) + (boll == 'low') + (vol == 'high')
        down_score = (rsi > 65) + (trend == 'down') + (stoch > 70) + (boll == 'high') + (vol == 'high')

        if up_score >= 3:
            bot.reply_to(message, f"🟢 SIGNAL: YUQORI (UP) | Ball: {up_score}/5")
        elif down_score >= 3:
            bot.reply_to(message, f"🔴 SIGNAL: PAST (DOWN) | Ball: {down_score}/5")
        else:
            bot.reply_to(message, f"⏳ Signal kuchsiz (Ball: {max(up_score, down_score)}/5). Kuting.")
    except Exception:
        bot.reply_to(message, "⚠️ Xatolik: Ma'lumotlarni to'g'ri raqamlar bilan kiriting.")

bot.infinity_polling(none_stop=True)
