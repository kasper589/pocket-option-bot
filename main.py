alculate_macd_signal(closes)
    impuls)"
                            stars = "⭐⭐"
                            recom = "Bozor o'rta zonada, narx pastga intilyapti."

                    header = "💎 INSTITUTIONAL VIP SIGNAL 💎" if "⭐⭐⭐⭐" in stars else "📊 SKALPING SIGNAL"

                    await status_msg.edit_text(
                        f"{header}\n\n"
                        f"💱 Aktiv: **{pair_text}** | TM: `{interval.upper()}`\n"
                        f"💰 Hozirgi narx: `{current_price}`\n\n"
                        f"📈 **TEHNIK TAHLIL:**\n"
                        f"   • RSI (14): `{rsi}`\n"
                        f"   • Stochastic: `{stoch}`\n"
                        f"   • MACD Trend: `{macd}`\n"
                        f"   • Bollinger: `{'CHIQDI' if current_price>=upper or current_price<=lower else 'NORMA'}`\n\n"
                        f"📢 **PRO SIGNAL:** **{signal}**\n"
                        f"🎯 Ishonchlilik darajasi: {stars}\n"
                        f"💡 **Tavsiya:** {recom}",
                        parse_mode="Markdown"
                    )
                else:
                    await status_msg.edit_text("Ma'lumot olishda xatolik bo'ldi.")
        except Exception as e:
            await status_msg.edit_text(f"Xatolik: {e}")
            
    await state.set_state(TradingState.waiting_for_pair)
    await message.answer("Keyingi signal uchun juftlikni tanlang 👇", reply_markup=get_pairs_keyboard())

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
