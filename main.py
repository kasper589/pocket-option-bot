import os
import requests
import telebot
from telebot import types

TOKEN = os.environ.get("BOT_TOKEN")
TWELVE_API = os.environ.get("TWELVE_API_KEY")

bot = telebot.TeleBot(TOKEN)

PAIRS = ["EUR/USD", "GBP/USD", "AUD/USD", "USD/JPY", "USD/CHF", "NZD/USD", "EUR/JPY", "GBP/JPY"]

# ===================== REAL VAQT MA'LUMOT =====================
def get_realtime_data(pair, interval, outputsize=50):
    url = "https://api.twelvedata.com/time_series"
    params = {
        "symbol": pair,
        "interval": f"{interval}min",
        "outputsize": outputsize,
        "apikey": TWELVE_API,
    }
    r = requests.get(url, params=params, timeout=10)
    data = r.json()
    if "values" not in data:
        return None
    values = data["values"]
    closes = [float(v["close"]) for v in reversed(values)]
    highs  = [float(v["high"])  for v in reversed(values)]
    lows   = [float(v["low"])   for v in reversed(values)]
    return closes, highs, lows

# ===================== INDIKATORLAR =====================
def calc_rsi(closes, period=14):
    deltas = [closes[i] - closes[i-1] for i in range(1, len(closes))]
    gains = [d if d > 0 else 0 for d in deltas]
    losses = [-d if d < 0 else 0 for d in deltas]
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    if avg_loss == 0:
        return 100
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def calc_ema(closes, period):
    k = 2 / (period + 1)
    ema = closes[0]
    for price in closes[1:]:
        ema = price * k + ema * (1 - k)
    return ema

def calc_macd(closes):
    ema12 = calc_ema(closes, 12)
    ema26 = calc_ema(closes, 26)
    return ema12 - ema26

def calc_stoch(closes, highs, lows, period=14):
    low14 = min(lows[-period:])
    high14 = max(highs[-period:])
    if high14 == low14:
        return 50
    return 100 * (closes[-1] - low14) / (high14 - low14)

def calc_bollinger(closes, period=20):
    sma = sum(closes[-period:]) / period
    std = (sum((c - sma)**2 for c in closes[-period:]) / period) ** 0.5
    return sma + 2*std, sma - 2*std

# ===================== TAHLIL =====================
def analyze(pair, timeframe):
    result = get_realtime_data(pair, timeframe, outputsize=50)
    if result is None:
        return None

    closes, highs, lows = result
    price = closes[-1]

    rsi = calc_rsi(closes)
    ema9 = calc_ema(closes, 9)
    ema21 = calc_ema(closes, 21)
    macd = calc_macd(closes)
    stoch = calc_stoch(closes, highs, lows)
    upper_bb, lower_bb = calc_bollinger(closes)

    buy_score = 0
    sell_score = 0

    if rsi < 35:
        buy_score += 1
    elif rsi > 65:
        sell_score += 1
    else:
        buy_score += 0.5; sell_score += 0.5

    if ema9 > ema21:
        buy_score += 1
    else:
        sell_score += 1

    if macd > 0:
        buy_score += 1
    else:
        sell_score += 1

    if price < lower_bb:
        buy_score += 1
    elif price > upper_bb:
        sell_score += 1
    else:
        buy_score += 0.5; sell_score += 0.5

    if stoch < 20:
        buy_score += 1
    elif stoch > 80:
        sell_score += 1
    else:
        buy_score += 0.5; sell_score += 0.5

    total = 5
    if buy_score > sell_score:
        direction = "BUY"
        confidence = round((buy_score / total) * 100)
    else:
        direction = "SELL"
        confidence = round((sell_score / total) * 100)

    if confidence >= 80:
        strength = "💥 JUDA KUCHLI"
    elif confidence >= 65:
        strength = "✅ KUCHLI"
    else:
        strength = "⚠️ ZAIF — Kirmaslik tavsiya"

    return {
        "pair": pair,
        "timeframe": timeframe,
        "price": round(price, 5),
        "direction": direction,
        "confidence": confidence,
        "strength": strength,
        "rsi": round(rsi, 1),
        "macd": "Yuqori ↑" if macd > 0 else "Past ↓",
        "ema": "Yuqori trend ↑" if ema9 > ema21 else "Past trend ↓",
        "stoch": round(stoch, 1),
    }

# ===================== TELEGRAM =====================
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("📊 Tahlil boshlash"))
    markup.add(types.KeyboardButton("ℹ️ Bot haqida"))
    bot.send_message(
        message.chat.id,
        "🤖 *PRO SKALPER BOT* — Real Vaqt!\n\n"
        "⚡ Twelvedata orqali real narxlar\n"
        "📈 5 ta indikator: RSI, EMA, MACD, BB, Stoch\n"
        "💯 Ishonch foizi\n\n"
        "Boshlash uchun tugmani bosing 👇",
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.message_handler(func=lambda m: m.text == "ℹ️ Bot haqida")
def about(message):
    bot.send_message(
        message.chat.id,
        "📌 *PRO SKALPER BOT*\n\n"
        "✅ Real vaqt narxlar (Twelvedata)\n"
        "✅ 5 ta professional indikator\n"
        "✅ Ishonch foizi\n"
        "✅ 8 ta valyuta juftligi\n\n"
        "⚠️ _Bu bot faqat tahlil uchun!_",
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda m: m.text == "📊 Tahlil boshlash")
def choose_pair(message):
    markup = types.InlineKeyboardMarkup(row_width=4)
    buttons = [types.InlineKeyboardButton(p, callback_data=f"pair_{p}") for p in PAIRS]
    markup.add(*buttons)
    bot.send_message(message.chat.id, "💱 *Valyuta juftligini tanlang:*", parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("pair_"))
def choose_time(call):
    pair = call.data[5:]
    markup = types.InlineKeyboardMarkup(row_width=2)
    times = [("1 daqiqa", "1"), ("3 daqiqa", "3"), ("5 daqiqa", "5"), ("15 daqiqa", "15")]
    buttons = [types.InlineKeyboardButton(label, callback_data=f"time_{t}_{pair}") for label, t in times]
    markup.add(*buttons)
    bot.edit_message_text(
        f"✅ Juftlik: *{pair}*\n\n⏱ *Timeframe tanlang:*",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("time_"))
def show_signal(call):
    parts = call.data.split("_", 2)
    timeframe = parts[1]
    pair = parts[2]

    bot.edit_message_text(
        f"⏳ *{pair}* real vaqt tahlil qilinmoqda...",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="Markdown"
    )

    result = analyze(pair, timeframe)

    if result is None:
        bot.edit_message_text(
            "❌ Ma'lumot olishda xatolik. Iltimos qayta urinib ko'ring.",
            call.message.chat.id,
            call.message.message_id
        )
        return

    emoji = "🟢" if result["direction"] == "BUY" else "🔴"
    msg = (
        f"📊 *{result['pair']} — {result['timeframe']} daqiqa*\n"
        f"━━━━━━━━━━━━━━━\n"
        f"💰 Narx: `{result['price']}`\n\n"
        f"{emoji} *Signal: {result['direction']}*\n"
        f"📈 Ishonch: *{result['confidence']}%*\n"
        f"⚡ Kuch: {result['strength']}\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🔍 *Indikatorlar:*\n"
        f"• RSI: `{result['rsi']}`\n"
        f"• MACD: `{result['macd']}`\n"
        f"• EMA: `{result['ema']}`\n"
        f"• Stochastic: `{result['stoch']}`\n"
        f"━━━━━━━━━━━━━━━\n"
        f"⚠️ _Faqat tahlil uchun!_"
    )

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔄 Yangilash", callback_data=f"time_{timeframe}_{pair}"))
    markup.add(types.InlineKeyboardButton("🏠 Bosh sahifa", callback_data="home"))

    bot.edit_message_text(
        msg,
        call.message.chat.id,
        call.message.message_id,
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data == "home")
def go_home(call):
    markup = types.InlineKeyboardMarkup(row_width=4)
    buttons = [types.InlineKeyboardButton(p, callback_data=f"pair_{p}") for p in PAIRS]
    markup.add(*buttons)
    bot.edit_message_text(
        "💱 *Valyuta juftligini tanlang:*",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="Markdown",
        reply_markup=markup
    )

bot.infinity_polling()
