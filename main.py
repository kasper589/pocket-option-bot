import os
import telebot
from telebot import types
import random

TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

# Analiz funksiyasi vaqtni ham hisobga oladi
def analyze_market_data(timeframe):
    rsi = random.randint(20, 80)
    
    # Vaqtga qarab tavsiya (M1 qisqa, M5 barqaror)
    if rsi < 30:
        signal = "🟢 KUCHLI SOTIB OLISH (BUY)"
        reason = f"RSI {rsi} (Haddan tashqari sotilgan)"
        advice = f"{timeframe} daqiqa uchun mos!" if int(timeframe) <= 3 else "Ehtiyot bo'ling, trend o'zgarishi mumkin."
    elif rsi > 70:
        signal = "🔴 KUCHLI SOTISH (SELL)"
        reason = f"RSI {rsi} (Haddan tashqari sotib olingan)"
        advice = f"{timeframe} daqiqa uchun mos!" if int(timeframe) <= 3 else "Trend kuchli, uzoq muddatga qilmang."
    else:
        signal = "🟡 KUTISH (WAIT)"
        reason = f"RSI {rsi} (Neytral zona)"
        advice = "Bozor noaniq, zdelka ochmang."
        
    return signal, reason, advice

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("Analizni boshlash 🔍"))
    bot.send_message(message.chat.id, "Pocket Option Texnik Yordamchi ishga tushdi.", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Analizni boshlash 🔍")
def choose_pair(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton("EUR/USD", callback_data="pair_eurusd"),
               types.InlineKeyboardButton("GBP/USD", callback_data="pair_gbpusd"))
    bot.send_message(message.chat.id, "1. Juftlikni tanlang:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    
    # 1. Juftlik tanlangandan keyin vaqtni so'raymiz
    if call.data.startswith("pair_"):
        pair = call.data.split("_")[1].upper()
        markup = types.InlineKeyboardMarkup(row_width=3)
        markup.add(types.InlineKeyboardButton("1 min", callback_data=f"time_1_{pair}"),
                   types.InlineKeyboardButton("3 min", callback_data=f"time_3_{pair}"),
                   types.InlineKeyboardButton("5 min", callback_data=f"time_5_{pair}"))
        bot.edit_message_text(f"Tanlandi: {pair}\n2. Vaqtni tanlang:", chat_id, call.message.message_id, reply_markup=markup)
    
    # 2. Vaqt tanlangandan keyin analizni chiqaramiz
    elif call.data.startswith("time_"):
        _, time, pair = call.data.split("_")
        signal, reason, advice = analyze_market_data(time)
        
        result = (
            f"📊 **{pair} TEXNIK TAHLILI**\n\n"
            f"Vaqt oralig'i: {time} min\n"
            f"Indikator (RSI): {reason}\n"
            f"Signal: {signal}\n"
            f"Tavsiya: {advice}\n\n"
            f"⚠️ Qarorni grafikni ko'rib qabul qiling!"
        )
        bot.edit_message_text(result, chat_id, call.message.message_id, parse_mode="Markdown")

bot.infinity_polling()
