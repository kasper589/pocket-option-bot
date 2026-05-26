import os
import telebot
from telebot import types
import yfinance as yf

TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

def analyze_market_data(pair, timeframe):
    # Real vaqtda narxni olish (yfinance)
    ticker = yf.Ticker(f"{pair}=X")
    data = ticker.history(period="1d", interval="1m")
    
    if data.empty:
        return "Xatolik", "Ma'lumot topilmadi", "Qayta urinib ko'ring."

    price = data['Close'].iloc[-1]
    # RSI ni oddiy hisoblash (taxminiy logika real narxga asoslangan)
    rsi = 50 + (price - data['Open'].iloc[0]) * 10 
    rsi = max(20, min(80, rsi)) # RSI ni 20-80 oralig'ida ushlaymiz

    if rsi < 35:
        signal = "🟢 KUCHLI SOTIB OLISH (BUY)"
        advice = f"{timeframe} daqiqaga zdelka oching!"
    elif rsi > 65:
        signal = "🔴 KUCHLI SOTISH (SELL)"
        advice = f"{timeframe} daqiqaga zdelka oching!"
    else:
        signal = "🟡 KUTISH (WAIT)"
        advice = "Bozor noaniq, kuting."
        
    return signal, f"Real narx: {price:.4f} | RSI: {rsi:.2f}", advice

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("Analizni boshlash 🔍"))
    bot.send_message(message.chat.id, "Real vaqtli Pro bot ishga tushdi!", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Analizni boshlash 🔍")
def choose_pair(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton("EUR/USD", callback_data="pair_EURUSD"),
               types.InlineKeyboardButton("GBP/USD", callback_data="pair_GBPUSD"))
    bot.send_message(message.chat.id, "Juftlikni tanlang:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data.startswith("pair_"):
        pair = call.data.split("_")[1]
        markup = types.InlineKeyboardMarkup(row_width=3)
        markup.add(types.InlineKeyboardButton("1 min", callback_data=f"time_1_{pair}"),
                   types.InlineKeyboardButton("3 min", callback_data=f"time_3_{pair}"))
        bot.edit_message_text(f"Tanlandi: {pair}\nVaqtni tanlang:", call.message.chat.id, call.message.message_id, reply_markup=markup)
    
    elif call.data.startswith("time_"):
        _, time, pair = call.data.split("_")
        signal, reason, advice = analyze_market_data(pair, time)
        result = f"📊 **{pair} REAL ANALIZ**\n\n{reason}\nSignal: {signal}\nMaslahat: {advice}"
        bot.edit_message_text(result, call.message.chat.id, call.message.message_id, parse_mode="Markdown")

bot.infinity_polling()
