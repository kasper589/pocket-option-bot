import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import CommandStart
import aiohttp
import math

BOT_TOKEN = "8800349563:AAExIc3e-ecukrbn07akiVBx69sZkNrdIxE"
PASSWORD = "KASPER404"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

class AuthState(StatesGroup):
    waiting_for_pass = State()
    authorized = State()

class TradingState(StatesGroup):
    waiting_for_pair = State()
    waiting_for_tf = State()

def get_main_keyboard():
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Signal olish 🚀")]], resize_keyboard=True)

def get_pairs_keyboard():
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="💱 EUR/USD"), KeyboardButton(text="💱 GBP/USD")], [KeyboardButton(text="🪙 BTC/USDT"), KeyboardButton(text="⬅️ Orqaga")]], resize_keyboard=True)

def get_tf_keyboard():
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="⏱ M1 (1 daqiqa)"), KeyboardButton(text="⏱ M5 (5 daqiqa)")], [KeyboardButton(text="⏱ M15 (15 daqiqa)")], [KeyboardButton(text="⬅️ Orqaga")]], resize_keyboard=True)

# INDIKATORLAR (Barchasi joyida!)
def calculate_rsi(prices, period=14):
    if len(prices) < period + 1: return 50.0
    gains, losses = [], []
    for i in range(1, len(prices)):
        change = prices[i] - prices[i-1]
        if change > 0: gains.append(change); losses.append(0)
        else: gains.append(0); losses.append(abs(change))
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    if avg_loss == 0: return 100.0
    return round(100 - (100 / (1 + (avg_gain / avg_loss))), 2)

def calculate_bollinger_bands(prices, period=20):
    if len(prices) < period: period = len(prices)
    sub_prices = prices[-period:]
    sma = sum(sub_prices) / period
    std_dev = math.sqrt(sum((x - sma) ** 2 for x in sub_prices) / period)
    return round(sma + (2 * std_dev), 6), round(sma, 6), round(sma - (2 * std_dev), 6)

def calculate_sma(prices, period):
    if len(prices) < period: period = len(prices)
    return round(sum(prices[-period:]) / period, 6)

def calculate_stochastic(highs, lows, closes, period=14):
    if len(closes) < period: return 50.0
    k_value = ((closes[-1] - min(lows[-period:])) / (max(highs[-period:]) - min(lows[-period:]))) * 100
    return round(k_value, 2)

def calculate_ema(prices, period):
    k = 2 / (period + 1)
    ema = prices[0]
    for price in prices[1:]: ema = (price * k) + (ema * (1 - k))
    return ema

def calculate_macd_signal(prices):
    if len(prices) < 26: return "NEUTRAL"
    return "BUY_TREND" if (calculate_ema(prices, 12) - calculate_ema(prices, 26)) > 0 else "SELL_TREND"

# START VA PAROL
@dp.message(CommandStart())
async def start_cmd(message: Message, state: FSMContext):
    await message.answer("Botga kirish uchun parolni kiriting:")
    await state.set_state(AuthState.waiting_for_pass)

@dp.message(AuthState.waiting_for_pass)
async def check_password(message: Message, state: FSMContext):
    if message.text == PASSWORD:
        await state.set_state(AuthState.authorized)
        await message.answer("Parol to'g'ri! ✅ Xush kelibsiz.", reply_markup=get_main_keyboard())
    else:
        await message.answer("Parol xato! ❌ Qayta urinib ko'ring.")

# ASOSIY LOGIKA (Sizning indikatorlar bilan)
@dp.message(F.text == "Signal olish 🚀")
async def show_pairs(message: Message, state: FSMContext):
    data = await state.get_state()
    if data != "AuthState:authorized":
        await message.answer("Avval parolni kiriting!")
        return
    await message.answer("Valyuta juftligini tanlang 👇", reply_markup=get_pairs_keyboard())
    await state.set_state(TradingState.waiting_for_pair)

@dp.message(TradingState.waiting_for_pair)
async def process_pair(message: Message, state: FSMContext):
    if message.text == "⬅️ Orqaga":
        await message.answer("Bosh menyu", reply_markup=get_main_keyboard())
        await state.set_state(AuthState.authorized)
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

    status_msg = await message.answer("🛡️ Tahlil boshlandi...")
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit=50") as response:
            data = await response.json()
            closes = [float(c[4]) for c in data]; highs = [float(c[2]) for c in data]; lows = [float(c[3]) for c in data]
            
            rsi = calculate_rsi(closes)
            upper, middle, lower = calculate_bollinger_bands(closes)
            stoch = calculate_stochastic(highs, lows, closes)
            macd = calculate_macd_signal(closes)
            
            buy, sell = 0, 0
            if rsi <= 35: buy += 2
            elif rsi >= 65: sell += 2
            if closes[-1] <= lower: buy += 2
            elif closes[-1] >= upper: sell += 2
            if stoch <= 20: buy += 2
            elif stoch >= 80: sell += 2
            if macd == "BUY_TREND": buy += 1
            else: sell += 1
            
            signal = "🟢 BUY" if buy >= 6 else "🔴 SELL" if sell >= 6 else "📈/📉 Impuls"
            stars = "⭐⭐⭐⭐" if buy >= 6 or sell >= 6 else "⭐⭐"
            await status_msg.edit_text(f"📊 {signal} {stars}\nAktiv: {pair_text}\nNarx: {closes[-1]}")
    await state.set_state(AuthState.authorized)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
