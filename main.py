import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart

BOT_TOKEN = "8800349563:AAExIc3e-ecukrbn07akiVBx69sZkNrdIxE"
SECRET_PASSWORD = "KASPER404"
AUTHORIZED = set()

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

def analyze_market(c, h, l):
    rsi = 100 - (100 / (1 + (sum([max(0, c[i]-c[i-1]) for i in range(1, 14)]) / (sum([max(0, c[i-1]-c[i]) for i in range(1, 14)]) + 0.001))))
    ema12 = sum(c[-12:]) / 12
    ema26 = sum(c[-26:]) / 26
    stoch = ((c[-1] - min(l[-14:])) / (max(h[-14:]) - min(l[-14:]) + 0.001)) * 100
    bollinger_mid = sum(c[-20:]) / 20
    score = (1 if rsi < 35 else 0) + (1 if ema12 > ema26 else 0) + (1 if stoch < 20 else 0) + (1 if c[-1] < bollinger_mid else 0)
    return ("🟢 BUY" if score >= 2 else "🔴 SELL"), rsi, stoch

@dp.message(CommandStart())
async def start(msg: Message): await msg.answer("🔒 Parolni kiriting:")

@dp.message(F.text == SECRET_PASSWORD)
async def unlock(msg: Message):
    AUTHORIZED.add(msg.from_user.id)
    kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Signal olish 🚀")]], resize_keyboard=True)
    await msg.answer("✅ Tizim faol.", reply_markup=kb)

@dp.message(F.text == "Signal olish 🚀")
async def get_signal(msg: Message):
    if msg.from_user.id not in AUTHORIZED: return
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=15m&limit=50") as resp:
                data = await resp.json()
                c = [float(x[4]) for x in data]; h = [float(x[2]) for x in data]; l = [float(x[3]) for x in data]
                sig, rsi, stoch = analyze_market(c, h, l)
                await msg.answer(f"📊 {sig}\n📈 RSI: {rsi:.2f}\n📉 Stoch: {stoch:.2f}")
    except Exception as e: await msg.answer(f"Xatolik: {e}")

async def main(): await dp.start_polling(bot)
if __name__ == "__main__": asyncio.run(main())
