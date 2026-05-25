import telebot
from flask import Flask
from threading import Thread

# 1. Botni ishga tushirish
bot = telebot.TeleBot("8893762032:AAH23-yyQib8wdRnf4tk7inW-f9SiWLMJ-8")

# 2. Render (Web Service) uchun server qismi
app = Flask('')

@app.route('/')
def home():
    return "Bot ishlamoqda!"

def run():
    app.run(host='0.0.0.0', port=8080)

# Serverni fon rejimida yoqamiz
t = Thread(target=run)
t.start()

# 3. Asosiy bot funksiyalari
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Tizim faol. Analiz uchun 5 ta parametrni vergul bilan kiriting:\nFormat: RSI,Trend,Stoch,Boll,Vol\nMasalan: 30,up,20,low,high")

@bot.message_handler(func=lambda message: True)
def analyze(message):
    text = message.text
    if ',' not in text:
        return
        
    data = text.split(',')
    if len(data) != 5:
        bot.reply_to(message, "⚠️ Xatolik: 5 ta parametr kiriting (RSI,Trend,Stoch,Boll,Vol)")
        return

    try:
        rsi = float(data[0])
        trend = data[1].lower()
        stoch = float(data[2])
        boll = data[3].lower()
        vol = data[4].lower()

        # Strategiya ballari
        up_score = (rsi < 35) + (trend == 'up') + (stoch < 30) + (boll == 'low') + (vol == 'high')
        down_score = (rsi > 65) + (trend == 'down') + (stoch > 70) + (boll == 'high') + (vol == 'high')

        if up_score >= 3:
            bot.reply_to(message, f"🟢 SIGNAL: YUQORI (UP)\nBall: {up_score}/5")
        elif down_score >= 3:
            bot.reply_to(message, f"🔴 SIGNAL: PAST (DOWN)\nBall: {down_score}/5")
        else:
            bot.reply_to(message, f"⏳ Signal kuchsiz (Ball: {max(up_score, down_score)}/5). Kuting.")
            
    except Exception as e:
        bot.reply_to(message, "⚠️ Xatolik: Ma'lumotlarni to'g'ri raqamlar bilan kiriting.")

# Botni doimiy eshitish rejimida qoldiramiz
bot.polling(none_stop=True)
