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

# --- ANALIZ ENGINE ---
async def perform_deep_analysis(c, h, l, v):
    # RSI
    delta = [c[i] - c[i-1] for i in range(1, len(c))]
    gain = sum([d for d in delta[-14:] if d > 0]) / 14
    loss = sum([-d for d in delta[-14:] if d < 0]) / 14
    rsi = 100 - (100 / (1 + (gain / (loss + 0.001))))
    
    # EMA 200
    ema200 = sum(c[-200:]) / 200
    
    # SIGNAL LOGIKASI
    if rsi < 35 and c[-1] > ema200:
        return "🟢 BUY (KUCHLI)", c[-1] * 0.99, c[-1] * 1.02
    elif rsi > 65 and c[-1] < ema200:
        return "🔴 SELL (KUCHLI)", c[-1] * 1.01, c[-1] * 0.98
    else:
        return "🟡 KUTISH (NOANIQ)", 0, 0

# --- BOT LOGIKASI ---
@dp.message(CommandStart())
async def start(msg: Message): 
    await msg.answer("🔒 Tizim himoyalangan. Parolni kiriting:")

@dp.message(F.text == SECRET_PASSWORD)
async def unlock(msg: Message):
    AUTHORIZED.add(msg.from_user.id)
    kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="⚡ ANALIZNI BOSHLASH ⚡")]], resize_keyboard=True)
    await msg.answer("✅ Tizim faol. Analizni bosing!", reply_markup=kb)

@dp.message(F.text == "⚡ ANALIZNI BOSHLASH ⚡")
async def trade_start(msg: Message):
    if msg.from_user.id not in AUTHORIZED: return
    
    await msg.answer("⚙️ Tahlil qilinmoqda...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=15m&limit=500") as r:
                data = await r.json()
                c = [float(x[4]) for x in data]
                h = [float(x[2]) for x in data]
                l = [float(x[3]) for x in data]
                v = [float(x[5]) for x in data]
                
                sig, en, sl, tp = await perform_deep_analysis(c, h, l, v)
                
                if en == 0:
                    await msg.answer(f"📊 Signal: {sig}\nBozor hozirda noaniq, biroz kuting.")
                else:
                    await msg.answer(f"📊 SIGNAL: {sig}\n💰 Narx: {c[-1]}\n🎯 ENTRY: {en:.2f}\n🛡 SL: {sl:.2f}\n💰 TP: {tp:.2f}")
    except Exception as e:
        await msg.answer(f"Xatolik: {e}")

async def main(): await dp.start_polling(bot)
if __name__ == "__main__": asyncio.run(main())
