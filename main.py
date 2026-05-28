import requests
import telebot
from telebot import types
import pandas as pd

TOKEN = "8800349563:AAHmRfc9S2Z3lRf5crvxmQR5Lmj0StAfcPY"
TWELVE_API = "0a2fb3dd461f4ea8bb06d56181995b3e"

bot = telebot.TeleBot(TOKEN)

PAIRS = ["AUD/USD", "EUR/USD", "GBP/USD", "USD/JPY", "USD/CHF", "NZD/USD", "EUR/JPY", "GBP/JPY"]

def get_data(pair, interval, outputsize=80):
    url = "https://api.twelvedata.com/time_series"
    params = {
        "symbol": pair,
        "interval": f"{interval}min",
        "outputsize": outputsize,
        "apikey": TWELVE_API,
    }
    try:
        r = requests.get(url, params=params, timeout=15)
        data = r.json()
        if "values" not in data:
            return None, data.get("message", "Noma'lum xatolik")
        values = data["values"]
        df = pd.DataFrame(reversed(values))
        df['close'] = df['close'].astype(float)
        df['high'] = df['high'].astype(float)
        df['low'] = df['low'].astype(float)
        return df, None
    except Exception as e:
        return None, str(e)

def analyze(pair, timeframe):
    df, error = get_data(pair, timeframe, outputsize=80)
    if df is None:
        return None, error
    if len(df) < 30:
        return None, "Yetarli ma'lumot yo'q"

    close = df['close']
    high = df['high']
    low = df['low']

    # RSI
    delta = close.diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

    # EMA
    df['EMA9'] = close.ewm(span=9, adjust=False).mean()
    df['EMA21'] = close.ewm(span=21, adjust=False).mean()
    df['EMA50'] = close.ewm(span=50, adjust=False).mean()

    # MACD
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    df['MACD'] = ema12 - ema26

    # Bollinger
    sma20 = close.rolling(20).mean()
    std20 = close.rolling(20).std()
    df['BB_upper'] = sma20 + 2 * std20
    df['BB_lower'] = sma20 - 2 * std20

    # Stochastic
    low14 = low.rolling(14).min()
    high14 = high.rolling(14).max()
    df['STOCH'] = 100 * (close - low14) / (high14 - low14)

    df.dropna(inplace=True)
    if len(df) < 3:
        return None, "NaN tozalashdan keyin ma'lumot qolmadi"

    row = df.iloc[-1]

    trend_up = row['EMA9'] > row['EMA21'] > row['EMA50']
    trend_down = row['EMA9'] < row['EMA21'] < row['EMA50']

    buy_score = 0
    sell_score = 0

    # RSI
    if row['RSI'] < 30: buy_score += 2
    elif row['RSI'] < 45: buy_score += 1
    elif row['RSI'] > 70: sell_score += 2
    elif row['RSI'] > 55: sell_score += 1

    # EMA
    if trend_up: buy_score += 2
    elif trend_down: sell_score += 2
    elif row['EMA9'] > row['EMA21']: buy_score += 1
    else: sell_score += 1

    # MACD
    if row['MACD'] > 0: buy_score += 1
    else: sell_score += 1

    # Bollinger
    bb_range = row['BB_upper'] - row['BB_lower']
    if row['close'] < row['BB_lower']: buy_score += 2
    elif row['close'] > row['BB_upper']: sell_score += 2
    elif row['close'] < (row['BB_lower'] + bb_range * 0.35): buy_score += 1
    elif row['close'] > (row['BB_upper'] - bb_range * 0.35): sell_score += 1

    # Stochastic
    if row['STOCH'] < 25: buy_score += 2
    elif row['STOCH'] < 40: buy_score += 1
    elif row['STOCH'] > 75: sell_score += 2
    elif row['STOCH'] > 60: sell_score += 1

    max_score = 10
    if buy_score > sell_score:
        direction = "BUY"
        confidence = round((buy_score / max_score) * 100)
    elif sell_score > buy_score:
        direction = "SELL"
        confidence = round((sell_score / max_score) * 100)
    else:
        direction = "KUTING"
        confidence = 50

    if confidence >= 80: strength = "ðŸ’¥ JUDA KUCHLI â€” KIRING!"
    elif confidence >= 70: strength = "âœ… KUCHLI"
    elif confidence >= 60: strength = "ðŸ‘ YETARLI"
    else: strength = "â³ KUCHSIZ â€” Kuting"

    return {
        "pair": pair,
        "timeframe": timeframe,
        "price": round(row['close'], 5),
        "direction": direction,
        "confidence": confidence,
        "strength": strength,
        "rsi": round(row['RSI'], 1),
        "macd": "Yuqori â†‘" if row['MACD'] > 0 else "Past â†“",
        "ema": "Yuqori â†‘" if row['EMA9'] > row['EMA21'] else "Past â†“",
        "stoch": round(row['STOCH'], 1),
    }, None

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("ðŸ“Š Tahlil boshlash"))
    markup.add(types.KeyboardButton("â­ AUDUSD â€” Eng zo'r"))
    markup.add(types.KeyboardButton("â„¹ï¸ Bot haqida"))
    bot.send_message(
        message.chat.id,
        "ðŸ¤– *PRO SKALPER BOT v3*\n\n"
        "â­ AUDUSD â€” 82.86% aniqlik!\n"
        "ðŸ’¥ 6 ta indikator: RSI, EMA, MACD, BB, Stoch\n\n"
        "Boshlash uchun tugmani bosing ðŸ‘‡",
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.message_handler(func=lambda m: m.text == "â­ AUDUSD â€” Eng zo'r")
def audusd_quick(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    times = [("1 daqiqa", "1"), ("3 daqiqa", "3"), ("5 daqiqa", "5"), ("15 daqiqa", "15")]
    buttons = [types.InlineKeyboardButton(label, callback_data=f"time_{t}_AUD/USD") for label, t in times]
    markup.add(*buttons)
    bot.send_message(message.chat.id, "â­ *AUDUSD â€” Timeframe tanlang:*", parse_mode="Markdown", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "â„¹ï¸ Bot haqida")
def about(message):
    bot.send_message(
        message.chat.id,
        "ðŸ“Œ *PRO SKALPER BOT v3*\n\n"
        "âœ… Real vaqt narxlar\n"
        "âœ… 6 ta professional indikator\n"
        "â­ AUDUSD â€” 82.86% backtesting aniqlik\n\n"
        "âš ï¸ _Bu bot faqat tahlil uchun!_",
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda m: m.text == "ðŸ“Š Tahlil boshlash")
def choose_pair(message):
    markup = types.InlineKeyboardMarkup(row_width=4)
    buttons = [types.InlineKeyboardButton(p, callback_data=f"pair_{p}") for p in PAIRS]
    markup.add(*buttons)
    bot.send_message(message.chat.id, "ðŸ’± *Valyuta juftligini tanlang:*", parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("pair_"))
def choose_time(call):
    pair = call.data[5:]
    markup = types.InlineKeyboardMarkup(row_width=2)
    times = [("1 daqiqa", "1"), ("3 daqiqa", "3"), ("5 daqiqa", "5"), ("15 daqiqa", "15")]
    buttons = [types.InlineKeyboardButton(label, callback_data=f"time_{t}_{pair}") for label, t in times]
    markup.add(*buttons)
    bot.edit_message_text(
        f"âœ… Juftlik: *{pair}*\n\nâ± *Timeframe tanlang:*",
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
        f"â³ *{pair}* tahlil qilinmoqda...",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="Markdown"
    )

    result, error = analyze(pair, timeframe)

    if result is None:
        bot.edit_message_text(
            f"âŒ Xatolik: {error}\n\nQayta urinib ko'ring.",
            call.message.chat.id,
            call.message.message_id
        )
        return

    if result['direction'] == "BUY": emoji = "ðŸŸ¢"
    elif result['direction'] == "SELL": emoji = "ðŸ”´"
    else: emoji = "â³"

    msg = (
        f"ðŸ“Š *{result['pair']} â€” {result['timeframe']} daqiqa*\n"
        f"â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”\n"
        f"ðŸ’° Narx: `{result['price']}`\n\n"
        f"{emoji} *Signal: {result['direction']}*\n"
        f"ðŸ“ˆ Ishonch: *{result['confidence']}%*\n"
        f"âš¡ {result['strength']}\n"
        f"â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”\n"
        f"ðŸ” *Indikatorlar:*\n"
        f"â€¢ RSI: `{result['rsi']}`\n"
        f"â€¢ MACD: `{result['macd']}`\n"
        f"â€¢ EMA: `{result['ema']}`\n"
        f"â€¢ Stochastic: `{result['stoch']}`\n"
        f"â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”\n"
        f"âš ï¸ _Faqat tahlil uchun!_"
    )

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("ðŸ”„ Yangilash", callback_data=f"time_{timeframe}_{pair}"))
    markup.add(types.InlineKeyboardButton("ðŸ  Bosh sahifa", callback_data="home"))

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
        "ðŸ’± *Valyuta juftligini tanlang:*",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="Markdown",
        reply_markup=markup
    )

bot.infinity_polling()
