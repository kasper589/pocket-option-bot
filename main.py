import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart

BOT_TOKEN = "8800349563:AAExIc3e-ecukrbn07akiVBx69sZkNrdIxE"
SECRET_PASSWORD = "KASPER404"
AUTHORIZED_USERS = set()

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- ANALIZ FUNKSIYASI ---
def analyze_market(c, h, l):
    rsi = 100 - (100 / (1 + (sum([max(0, c[i]-c[i-1]) for i in range(1, 14)]) / (sum([max(0, c[i-1]-c[i]) for i in range(1, 14)]) + 0.001))))
    ema12 = sum(c[-12:]) / 12
    ema26 = sum(c[-26:]) / 26
    stoch = ((c[-1] - min(l[-14:])) / (max(h[-14:]) - min(l[-14:]) + 0.001)) * 100
    bollinger_mid = sum(c[-20:]) / 20
    
    score = 0
    if rsi < 35: score += 1
    if ema12 > ema26: score += 1
    if stoch < 20: score += 1
    if c[-1] < bollinger_mid: score += 1
    
    signal = "🟢 BUY" if score >= 2 else "🔴 SELL"
    return signal, rsi, stoch

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("🔒 Parolni kiriting:")

@dp.message(F.text == SECRET_PASSWORD)
async def unlock(message: Message):
    AUTHORIZED_USERS.add(message.from_user.id)
    kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Signal olish 🚀")]], resize_keyboard=True)
    await message.answer("✅ Tizim faol.", reply_markup=kb)

@dp.message(F.text == "Signal olish 🚀")
async def get_signal(message: Message):
    if message.from_user.id not in AUTHORIZED_USERS: return
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=15m&limit=50") as resp:
                data = await resp.json()
                c = [float(x[4]) for x in data]; h = [float(x[2]) for x in data]; l = [float(x[3]) for x in data]
                sig, rsi, stoch = analyze_market(c, h, l)
                await message.answer(f"📊 {sig}\n📈 RSI: {rsi:.2f}\n📉 Stoch: {stoch:.2f}")
    except Exception as e:
        await message.answer(f"Xatolik: {e}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
