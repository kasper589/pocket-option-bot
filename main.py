import os
import telebot
from telebot import types
import random

TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

# Bozor tahlili uchun "amaliy" funksiya
def analyze_market_data():
    # Bu yerda real bozordagi holatni simulyatsiya qilamiz
    rsi = random.randint(20, 80)
    ma_trend = random.choice(["O'sish (Bullish) 📈", "Pasayish (Bearish) 📉"])
    
    if rsi < 30:
        signal = "🟢 KUCHLI SOTIB OLISH (BUY)"
        reason = f"RSI {rsi} (Haddan tashqari sotilgan)"
    elif rsi > 70:
        signal = "🔴 KUCHLI SOTISH (SELL)"
        reason = f"RSI {rsi} (Haddan tashqari sotib olingan)"
    else:
        signal = "🟡 KUTISH (WAIT)"
        reason = f"RSI {rsi} (Neytral zona)"
        
    return signal, reason, ma_trend

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("Analizni boshlash 🔍"))
    bot.send_message(message.chat.id, "Pocket Option uchun Texnik Yordamchi ishga tushdi.", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Analizni boshlash 🔍")
def market_analysis(message):
    # Bu yerda foydalanuvchidan para so'rash qoladi
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("EUR/USD", callback_data="analyze_eurusd"))
    bot.send_message(message.chat.id, "Qaysi juftlikni tahlil qilamiz?", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    pair = call.data.split("_")[1].upper()
    
    signal, reason, trend = analyze_market_data()
    
    result = (
        f"📊 **{pair} TEXNIK TAHLILI**\n\n"
        f"Trend yo'nalishi: {trend}\n"
        f"Indikator (RSI): {reason}\n"
        f"Amaliy maslahat: {signal}\n\n"
        f"⚠️ Qarorni grafikni ko'rib qabul qiling!"
    )
    bot.edit_message_text(result, chat_id, call.message.message_id, parse_mode="Markdown")

bot.infinity_polling()
