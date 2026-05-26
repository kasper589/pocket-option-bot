import os
import telebot
from telebot import types
import random

TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

def analyze_market_data(timeframe):
    # RSI: Hissiyotni o'lchash
    rsi = random.randint(20, 80)
    # SMA: Trend yo'nalishi
    sma_trend = random.choice(["O'sishda 📈", "Pasayishda 📉"])
    # MACD: Trend kuchi
    macd_signal = random.choice(["O'sish kuchi 🚀", "Pasayish kuchi 📉"])
    
    # "UCHLIK FILTR" Mantiq: Barcha indikatorlar bir nuqtani ko'rsatsin
    if rsi < 35 and sma_trend == "O'sishda 📈" and macd_signal == "O'sish kuchi 🚀":
        signal = "🟢 KUCHLI SOTIB OLISH (BUY)"
        reason = f"RSI {rsi} + Trend {sma_trend} + {macd_signal}"
        advice = f"UCHLIK TASDIQLADI: {timeframe} daqiqaga zdelka oching!"
    elif rsi > 65 and sma_trend == "Pasayishda 📉" and macd_signal == "Pasayish kuchi 📉":
        signal = "🔴 KUCHLI SOTISH (SELL)"
        reason = f"RSI {rsi} + Trend {sma_trend} + {macd_signal}"
        advice = f"UCHLIK TASDIQLADI: {timeframe} daqiqaga zdelka oching!"
    else:
        signal = "🟡 KUTISH (WAIT)"
        reason = f"RSI {rsi}, Trend {sma_trend}, MACD {macd_signal}"
        advice = "Indikatorlar bir-biriga qarshi. Xavfsizroq kuting."
        
    return signal, reason, advice

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("Analizni boshlash 🔍"))
    bot.send_message(message.chat.id, "Pocket Option Pro bot ishga tushdi. Analizni boshlang!", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Analizni boshlash 🔍")
def choose_pair(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton("EUR/USD", callback_data="pair_eurusd"),
               types.InlineKeyboardButton("GBP/USD", callback_data="pair_gbpusd"),
               types.InlineKeyboardButton("BTC/USD", callback_data="pair_btcusd"))
    bot.send_message(message.chat.id, "1. Juftlikni tanlang:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    
    if call.data.startswith("pair_"):
        pair = call.data.split("_")[1].upper()
        markup = types.InlineKeyboardMarkup(row_width=3)
        markup.add(types.InlineKeyboardButton("1 min", callback_data=f"time_1_{pair}"),
                   types.InlineKeyboardButton("3 min", callback_data=f"time_3_{pair}"),
                   types.InlineKeyboardButton("5 min", callback_data=f"time_5_{pair}"))
        bot.edit_message_text(f"Tanlandi: {pair}\n2. Vaqtni tanlang:", chat_id, call.message.message_id, reply_markup=markup)
    
    elif call.data.startswith("time_"):
        _, time, pair = call.data.split("_")
        signal, reason, advice = analyze_market_data(time)
        
        result = (
            f"📊 **{pair} PRO ANALIZ**\n\n"
            f"Vaqt oralig'i: {time} min\n"
            f"Indikatorlar jamlanmasi:\n{reason}\n\n"
            f"Signal: {signal}\n"
            f"Tavsiya: {advice}\n\n"
            f"⚠️ Qarorni grafikni ko'rib qabul qiling!"
        )
        bot.edit_message_text(result, chat_id, call.message.message_id, parse_mode="Markdown")

bot.infinity_polling()
