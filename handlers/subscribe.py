from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters import Text
from loader import dp, bot
from data.config import ADMIN_IDS

@dp.message_handler(Text(equals=[
    "1 день - 100 грн", "7 днів - 500 грн", 
    "1 місяць - 1500 грн", "6 місяців - 4000 грн", "1 рік - 7000 грн"
]))
async def payment_options(message: types.Message):
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("📋 Скопіювати номер картки", callback_data="pay_copied"),
        InlineKeyboardButton("✅ Я оплатив", callback_data="pay_notified")
    )
    await message.answer(
        "💳 Щоб оплатити підписку — зверніться до @adminuser\n\n"
        "🔢 Реквізити для оплати через Приват24:\n"
"
        "🔢 Реквізити для оплати через Приват24:
"
        "<b>5168 7451 2748 8390</b>

"
        f"Після оплати скиньте скриншот та ваш Telegram ID: <code>{message.from_user.id}</code> адміну! @adminuser",
        parse_mode="HTML",
        reply_markup=kb
    )

@dp.callback_query_handler(Text(startswith="pay_"))
async def handle_payment_action(call: types.CallbackQuery):
    action = call.data.split("_")[1]
    user_id = call.from_user.id
    if action == "copied":
        await call.answer("💾 Номер картки скопійовано!")
    elif action == "notified":
        await call.answer("📩 Адміну надіслано повідомлення!")
        text = (
            f"🔔 Користувач @{call.from_user.username or 'невідомо'} "
            f"(ID: <code>{user_id}</code>) натиснув "Оплатив"."
        )
        for admin_id in ADMIN_IDS:
            await bot.send_message(admin_id, text, parse_mode="HTML")