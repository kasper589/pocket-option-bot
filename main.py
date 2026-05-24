import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import CommandStart
import aiohttp
import math

# Tokeningizni shu yerga yozing
BOT_TOKEN = "8800349563:AAExIc3e-ecukrbn07akiVBx69sZkNrdIxE"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

class TradingState(StatesGroup):
    waiting_for_pair = State()
    waiting_for_tf = State()

def get_main_keyboard():
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Signal olish 🚀")]], resize_keyboard=True)

def get_pairs_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="💱 EUR/USD"), KeyboardButton(text="💱 GBP/USD")],
            [KeyboardButton(text="🪙 BTC/USDT"), KeyboardButton(text="⬅️ Orqaga")]
        ],
        resize_keyboard=True
    )

def get_tf_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⏱ M1 (1 daqiqa)"), KeyboardButton(text="⏱ M5 (5 daqiqa)")],
            [KeyboardButton(text="⏱ M15 (15 daqiqa)"), KeyboardButton(text="⬅️ Orqaga")]
        ],
        resize_keyboard=True
    )

def calculate_rsi(prices, period=14):
    if len(prices) < period + 1: return 50.0
    gains, losses = [], []
    for i in range(1, len(prices)):
        change = prices[i] - prices[i-1]
        if change > 0:
            gains.append(change)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(change))
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    if avg_loss == 0: return 100.0
    return round(100 - (100 / (1 + (avg_gain / avg_loss))), 2)

def calculate_bollinger_bands(prices, period=20):
    if len(prices) < period: period = len(prices)
    sub_prices = prices[-period:]
    sma = sum(sub_prices) / period
    variance = sum((x - sma) ** 2 for x in sub_prices) / period
    std_dev = math.sqrt(variance)
    return round(sma + (2 * std_dev), 6), round(sma, 6), round(sma - (2 * std_dev), 6)

def calculate_sma(prices, period):
    if len(prices) < period: period = len(prices)
    return round(sum(prices[-period:]) / period, 6)

def calculate_stochastic(highs, lows, closes, period=14):
    if len(closes) < period: return 50.0
    current_close = closes[-1]
    lowest_low = min(lows[-period:])
    highest_high = max(highs[-period:])
    if (highest_high - lowest_low) == 0: return 50.0
    k_value = ((current_close - lowest_low) / (highest_high - lowest_low)) * 100
    return round(k_value, 2)

def calculate_ema(prices, period):
    if len(prices) == 0: return 0.0
    k = 2 / (period + 1)
    ema = prices[0]
    for price in prices[1:]:
        ema = (price * k) + (ema * (1 - k))
    return ema

def calculate_macd_signal(prices):
    if len(prices) < 26: return "NEUTRAL"
    ema12 = calculate_ema(prices, 12)
    ema26 = calculate_ema(prices, 26)
    macd_line = ema12 - ema26
    return "BUY_TREND" if macd_line > 0 else "SELL_TREND"

@dp.message(CommandStart())
async def start_cmd(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("🏦 QUANT-ALGO Terminaliga xush kelibsiz! Indikatorlar ulandi 🎯🤖", reply_markup=get_main_keyboard())

@dp.message(lambda message: message.text == "Signal olish 🚀")
async def show_pairs(message: Message, state: FSMContext):
    await message.answer("Valyuta juftligini tanlang 👇", reply_markup=get_pairs_keyboard())
    await state.set_state(TradingState.waiting_for_pair)

@dp.message(TradingState.waiting_for_pair)
async def process_pair(message: Message, state: FSMContext):
    if message.text == "⬅️ Orqaga":
        await state.clear()
        await message.answer("Bosh menyu", reply_markup=get_main_keyboard())
        return
    await state.update_data(chosen_pair=message.text)
    await message.answer("Taymfreymni tanlang 👇", reply_markup=get_tf_keyboard())
    await state.set_state(TradingState.waiting_for_tf)

@dp.message(TradingState.waiting_for_tf)
async def process_tf(message: Message, state: FSMContext):
    if message.text == "⬅️ Orqaga":
        await message.answer("Valyuta juftligini tanlang 👇", reply_markup=get_pairs_keyboard())
        await state.set_state(TradingState.waiting_for_pair)
        return

    user_data = await state.get_data()
    pair_text = user_data.get("chosen_pair")
    interval = {"⏱ M1 (1 daqiqa)": "1m", "⏱ M5 (5 daqiqa)": "5m", "⏱ M15 (15 daqiqa)": "15m"}[message.text]
    symbol = {"💱 EUR/USD": "EURUSDT", "💱 GBP/USD": "GBPUSDT", "🪙 BTC/USDT": "BTCUSDT"}[pair_text]

    status_msg = await message.answer(f"🛡️ Tahlil boshlandi...")
    binance_url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit=50"
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(binance_url) as response:
                if response.status == 200:
                    data = await response.json()
                    closes = [float(candle[4]) for candle in data]
                    highs = [float(candle[2]) for candle in data]
                    lows = [float(candle[3]) for candle in data]
                    current_price = closes[-1]
                    
                    rsi = calculate_rsi(closes)
                    upper, middle, lower = calculate_bollinger_bands(closes)
                    stoch = calculate_stochastic(highs, lows, closes)
                    macd = calculate_macd_signal(closes)
                    sma50 = calculate_sma(closes, 50)
                    
                    buy_score, sell_score = 0, 0
                    if rsi <= 35: buy_score += 2
                    elif rsi >= 65: sell_score += 2
                    if current_price <= lower: buy_score += 2
                    elif current_price >= upper: sell_score += 2
                    if stoch <= 20: buy_score += 2
                    elif stoch >= 80: sell_score += 2
                    if macd == "BUY_TREND": buy_score += 1
                    elif macd == "SELL_TREND": sell_score += 1
                    if current_price > sma50: buy_score += 1
                    else: sell_score += 1

                    if buy_score >= 6:
                        signal, stars, recom = "🟢 BUY", "⭐⭐⭐⭐", "Kuchli o'sish!"
                    elif sell_score >= 6:
                        signal, stars, recom = "🔴 SELL", "⭐⭐⭐⭐", "Kuchli tushish!"
                    else:
                        signal, stars, recom = "📈/📉 Impuls", "⭐⭐", "Bozor noaniq."

                    await status_msg.edit_text(f"📊 {signal}\nAktiv: {pair_text}\nNarx: {current_price}\n{recom}", parse_mode="Markdown")
        except Exception as e:
            await status_msg.edit_text(f"Xatolik: {e}")
    await state.set_state(TradingState.waiting_for_pair)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
