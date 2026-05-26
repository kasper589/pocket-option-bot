import os
import telebot
from telebot import types
import yfinance as yf

TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

# Juftliklar ro'yxati
PAIRS = ["EURUSD", "GBPUSD", "AUDUSD", "USDJPY", "USDCHF", "NZDUSD"]

def analyze_market_data(pair, timeframe):
    ticker = yf.Ticker(f"{pair}=X")
    data = ticker.history(period="1d", interval="1m")
    
    if data.empty:
        return "Xatolik", "Ma'lumot topilmadi.", "Qayta urinib ko'ring."

    price = data['Close'].iloc[-1]
    open_price = data['Open'].iloc[-1]
    
    if price > open_price + 0.00003: 
        signal = "🟢 SOTIB OLISH (BUY)"
    elif price < open_price - 0.00003:
        signal = "🔴 SOTISH (SELL)"
    else:
        signal = "🟡 KUTISH (WAIT)"
        
    return signal, f"Joriy narx: {price:.4f}", f"{timeframe} daqiqalik tahlil."

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("Analizni boshlash 🔍"))
    bot.send_message(message.chat.id, "Pro-Bot yangilandi! 6 ta juftlik va 4 xil vaqt oralig'i faol.", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Analizni boshlash 🔍")
def choose_pair(message):
    markup = types.InlineKeyboardMarkup(row_width=3)
    for p in PAIRS:
        markup.add(types.InlineKeyboardButton(p, callback_data=f"pair_{p}"))
    bot.send_message(message.chat.id, "Juftlikni tanlang:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data.startswith("pair_"):
        pair = call.data.split("_")[1]
        markup = types.InlineKeyboardMarkup(row_width=2)
        # 1, 3, 5, 15 daqiqalar
        for t in ["1", "3", "5", "15"]:
            markup.add(types.InlineKeyboardButton(f"{t} min", callback_data=f"time_{t}_{pair}"))
        bot.edit_message_text(f"Tanlandi: {pair}\nVaqtni tanlang:", call.message.chat.id, call.message.message_id, reply_markup=markup)
    
    elif call.data.startswith("time_"):
        _, time, pair = call.data.split("_")
        signal, reason, advice = analyze_market_data(pair, time)
        result = f"📊 **{pair} PRO ANALIZ**\n\n{reason}\nSignal: {signal}\nInfo: {advice}"
        bot.edit_message_text(result, call.message.chat.id, call.message.message_id, parse_mode="Markdown")

bot.infinity_polling()
