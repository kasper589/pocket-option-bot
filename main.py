import os
import telebot
from telebot import types
import yfinance as yf

TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

PAIRS = ["EURUSD", "GBPUSD", "AUDUSD", "USDJPY", "USDCHF", "NZDUSD"]

def analyze_market_data(pair, timeframe):
    tf_map = {"1": "1m", "3": "3m", "5": "5m", "15": "15m"}
    interval = tf_map.get(timeframe, "1m")
    
    ticker = yf.Ticker(f"{pair}=X")
    data = ticker.history(period="1d", interval=interval)
    
    if len(data) < 10:
        return "Xatolik", "Ma'lumot yetarli emas.", "Biroz kuting."

    # 1. Momentum tahlili (Oxirgi 5 svecha farqi)
    momentum = data['Close'].iloc[-1] - data['Close'].iloc[-5]
    # 2. Volatillik (Shovqin filtri)
    std_dev = data['Close'].rolling(window=5).std().iloc[-1]
    
    # Signallar mantiqi
    if momentum > (std_dev * 0.1):
        signal = "🟢 SOTIB OLISH (BUY)"
        advice = "Kuchli yuqoriga impuls!"
    elif momentum < -(std_dev * 0.1):
        signal = "🔴 SOTISH (SELL)"
        advice = "Kuchli pastga impuls!"
    else:
        signal = "🟢 BUY (Trend bo'yicha)" if momentum > 0 else "🔴 SELL (Trend bo'yicha)"
        advice = "Impuls zaif, trend davom etmoqda."
        
    return signal, f"Joriy narx: {data['Close'].iloc[-1]:.4f}", advice

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("Analizni boshlash 🔍"))
    bot.send_message(message.chat.id, "Pro-Skalper faol! Har doim signal beradi.", reply_markup=markup)

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
        for t in ["1", "3", "5", "15"]:
            markup.add(types.InlineKeyboardButton(f"{t} min", callback_data=f"time_{t}_{pair}"))
        bot.edit_message_text(f"Tanlandi: {pair}\nVaqtni tanlang:", call.message.chat.id, call.message.message_id, reply_markup=markup)
    
    elif call.data.startswith("time_"):
        _, time, pair = call.data.split("_")
        signal, reason, advice = analyze_market_data(pair, time)
        result = f"📊 **{pair} PRO-SKALPER**\n\n{reason}\nSignal: {signal}\nMaslahat: {advice}"
        bot.edit_message_text(result, call.message.chat.id, call.message.message_id, parse_mode="Markdown")

bot.infinity_polling()
