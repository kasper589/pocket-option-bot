import os
import telebot
from telebot import types
import yfinance as yf
import pandas as pd

TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

PAIRS = ["EURUSD", "GBPUSD", "AUDUSD", "USDJPY", "USDCHF", "NZDUSD", "EURJPY", "GBPJPY"]

# ===================== TAHLIL FUNKSIYASI =====================
def analyze(pair, timeframe):
    tf_map = {"1": "1m", "3": "2m", "5": "5m", "15": "15m"}
    interval = tf_map.get(timeframe, "1m")

    try:
        ticker = yf.Ticker(f"{pair}=X")
        data = ticker.history(period="2d", interval=interval)

        if len(data) < 30:
            return None

        close = data['Close']
        high = data['High']
        low = data['Low']

        # --- RSI (14) ---
        delta = close.diff()
        gain = delta.clip(lower=0).rolling(14).mean()
        loss = (-delta.clip(upper=0)).rolling(14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        rsi_val = rsi.iloc[-1]

        # --- EMA (9 va 21) ---
        ema9 = close.ewm(span=9).mean().iloc[-1]
        ema21 = close.ewm(span=21).mean().iloc[-1]

        # --- MACD ---
        ema12 = close.ewm(span=12).mean()
        ema26 = close.ewm(span=26).mean()
        macd = ema12 - ema26
        signal_line = macd.ewm(span=9).mean()
        macd_val = macd.iloc[-1]
        signal_val = signal_line.iloc[-1]

        # --- Bollinger Bands ---
        sma20 = close.rolling(20).mean()
        std20 = close.rolling(20).std()
        upper_band = sma20 + (std20 * 2)
        lower_band = sma20 - (std20 * 2)
        price = close.iloc[-1]
        upper = upper_band.iloc[-1]
        lower = lower_band.iloc[-1]

        # --- Stochastic (14,3) ---
        low14 = low.rolling(14).min()
        high14 = high.rolling(14).max()
        stoch_k = 100 * (close - low14) / (high14 - low14)
        stoch_val = stoch_k.iloc[-1]

        # ===================== SIGNAL MANTIQI =====================
        buy_score = 0
        sell_score = 0
        total = 5

        # RSI
        if rsi_val < 35:
            buy_score += 1
        elif rsi_val > 65:
            sell_score += 1
        else:
            buy_score += 0.5
            sell_score += 0.5

        # EMA
        if ema9 > ema21:
            buy_score += 1
        else:
            sell_score += 1

        # MACD
        if macd_val > signal_val:
            buy_score += 1
        else:
            sell_score += 1

        # Bollinger
        if price < lower:
            buy_score += 1
        elif price > upper:
            sell_score += 1
        else:
            buy_score += 0.5
            sell_score += 0.5

        # Stochastic
        if stoch_val < 20:
            buy_score += 1
        elif stoch_val > 80:
            sell_score += 1
        else:
            buy_score += 0.5
            sell_score += 0.5

        # Ishonch foizi
        if buy_score > sell_score:
            direction = "BUY"
            confidence = round((buy_score / total) * 100)
        else:
            direction = "SELL"
            confidence = round((sell_score / total) * 100)

        # Kuch darajasi
        if confidence >= 80:
            strength = "ðŸ’¥ JUDA KUCHLI"
        elif confidence >= 65:
            strength = "âœ… KUCHLI"
        else:
            strength = "âš ï¸ ZAIF"

        return {
            "pair": pair,
            "timeframe": timeframe,
            "price": round(price, 5),
            "direction": direction,
            "confidence": confidence,
            "strength": strength,
            "rsi": round(rsi_val, 1),
            "macd": "Yuqori" if macd_val > signal_val else "Past",
            "ema": "Yuqori trend" if ema9 > ema21 else "Past trend",
            "stoch": round(stoch_val, 1),
        }

    except Exception as e:
        return None


# ===================== TELEGRAM BOT =====================
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("ðŸ“Š Tahlil boshlash"))
    markup.add(types.KeyboardButton("â„¹ï¸ Bot haqida"))
    bot.send_message(
        message.chat.id,
        "ðŸ¤– *PRO SKALPER BOT* ga xush kelibsiz!\n\n"
        "Men 5 ta indikator yordamida signal beraman:\n"
        "â€¢ RSI\nâ€¢ EMA\nâ€¢ MACD\nâ€¢ Bollinger Bands\nâ€¢ Stochastic\n\n"
        "Boshlash uchun tugmani bosing ðŸ‘‡",
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.message_handler(func=lambda m: m.text == "â„¹ï¸ Bot haqida")
def about(message):
    bot.send_message(
        message.chat.id,
        "ðŸ“Œ *PRO SKALPER BOT*\n\n"
        "âœ… 5 ta professional indikator\n"
        "âœ… Ishonch foizi ko'rsatiladi\n"
        "âœ… 8 ta valyuta juftligi\n"
        "âœ… 4 ta timeframe\n\n"
        "âš ï¸ Eslatma: Bu bot faqat tahlil uchun. Har doim o'zingiz qaror qiling!",
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
    pair = call.data.split("_")[1]
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
    _, timeframe, pair = call.data.split("_")

    bot.edit_message_text(
        f"â³ *{pair}* tahlil qilinmoqda...",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="Markdown"
    )

    result = analyze(pair, timeframe)

    if result is None:
        bot.edit_message_text(
            "âŒ Ma'lumot olishda xatolik. Iltimos qayta urinib ko'ring.",
            call.message.chat.id,
            call.message.message_id
        )
        return

    emoji = "ðŸŸ¢" if result["direction"] == "BUY" else "ðŸ”´"
    msg = (
        f"ðŸ“Š *{result['pair']} â€” {result['timeframe']} daqiqa*\n"
        f"â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”\n"
        f"ðŸ’° Narx: `{result['price']}`\n\n"
        f"{emoji} *Signal: {result['direction']}*\n"
        f"ðŸ“ˆ Ishonch: *{result['confidence']}%*\n"
        f"âš¡ Kuch: {result['strength']}\n"
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
    markup.add(types.InlineKeyboardButton("ðŸ”„ Yangi tahlil", callback_data=f"pair_{pair}"))
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
    bot.edit_message_text("ðŸ’± *Valyuta juftligini tanlang:*", call.message.chat.id, call.message.message_id, parse_mode="Markdown", reply_markup=markup)

bot.infinity_polling()
