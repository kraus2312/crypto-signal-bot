from aiogram import types
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.filters import Command
from keyboards.inline.admin import admin_menu
from services.access_control import load_access_data
from config import ADMIN_IDS

def register_admin_handlers(dp: Dispatcher):
    @dp.message_handler(Command("admin"))
    async def admin_menu_handler(message: types.Message):
        if message.from_user.id not in ADMIN_IDS:
            return await message.answer("⛔ У вас немає доступу до адмін-панелі.")
        await message.answer("👮 Адмін-панель:", reply_markup=admin_menu)

    @dp.callback_query_handler(lambda c: c.data == "admin_users")
    async def show_users(callback: types.CallbackQuery):
        data = load_access_data()
        users = list(data.keys())
    text = "📜 <b>Список користувачів:</b>\n" + "\n".join([f"• <code>{u}</code>" for u in users])
" + "\n".join([f"• <code>{u}</code>" for u in users])
        await callback.message.answer(text, parse_mode="HTML")
        await callback.answer()

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from services.access_control import grant_premium

# Кеш для зберігання вибраного користувача
pending_user = {}

@dp.callback_query_handler(lambda c: c.data == "admin_activate")
async def admin_activate_step1(callback: types.CallbackQuery):
    data = load_access_data()
    keyboard = InlineKeyboardMarkup(row_width=2)
    for uid in data.keys():
        keyboard.insert(InlineKeyboardButton(text=uid, callback_data=f"select_user_{uid}"))
    await callback.message.answer("👤 Оберіть користувача для активації підписки:", reply_markup=keyboard)
    await callback.answer()

@dp.callback_query_handler(lambda c: c.data.startswith("select_user_"))
async def admin_activate_step2(callback: types.CallbackQuery):
    user_id = callback.data.split("_")[-1]
    pending_user[callback.from_user.id] = int(user_id)

    # Кнопки з тарифами
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("1 день", callback_data="grant_1"),
         InlineKeyboardButton("7 днів", callback_data="grant_7")],
        [InlineKeyboardButton("30 днів", callback_data="grant_30"),
         InlineKeyboardButton("180 днів", callback_data="grant_180")],
        [InlineKeyboardButton("365 днів", callback_data="grant_365")]
    ])
    await callback.message.answer(f"⏳ Оберіть тривалість підписки для користувача <code>{user_id}</code>:", parse_mode="HTML", reply_markup=keyboard)
    await callback.answer()

@dp.callback_query_handler(lambda c: c.data.startswith("grant_"))
async def admin_activate_final(callback: types.CallbackQuery):
    days = int(callback.data.split("_")[1])
    admin_id = callback.from_user.id
    if admin_id not in pending_user:
        return await callback.message.answer("⚠️ Спочатку оберіть користувача.")
    user_id = pending_user.pop(admin_id)
    grant_premium(user_id, days)
    await callback.message.answer(f"✅ Активовано підписку на {days} днів для користувача <code>{user_id}</code>", parse_mode="HTML")
    await callback.answer()

@dp.callback_query_handler(lambda c: c.data == "admin_stats")
async def show_stats(callback: types.CallbackQuery):
    data = load_access_data()
    total = len(data)
    trial = 0
    premium = 0
    now = datetime.now()

    for user in data.values():
        start = datetime.fromisoformat(user["start"])
        if (now - start).total_seconds() < 24 * 3600:
            trial += 1
        if "premium_until" in user:
            until = datetime.fromisoformat(user["premium_until"])
            if until > now:
                premium += 1

    await callback.message.answer(
        f"📊 <b>Статистика</b>:
"
        f"👥 Всього користувачів: <b>{total}</b>
"
        f"🧪 На пробному доступі: <b>{trial}</b>
"
        f"💎 З активною підпискою: <b>{premium}</b>",
        parse_mode="HTML"
    )
    await callback.answer()


@dp.callback_query_handler(lambda c: c.data == "admin_block")
async def block_user(callback: types.CallbackQuery):
    data = load_access_data()
    keyboard = InlineKeyboardMarkup(row_width=2)
    for uid in data.keys():
        keyboard.insert(InlineKeyboardButton(text=uid, callback_data=f"block_{uid}"))
    await callback.message.answer("🚫 Оберіть користувача для блокування:", reply_markup=keyboard)
    await callback.answer()

@dp.callback_query_handler(lambda c: c.data.startswith("block_"))
async def confirm_block(callback: types.CallbackQuery):
    uid = callback.data.split("_")[-1]
    data = load_access_data()
    if uid in data:
        del data[uid]
        save_access_data(data)
        await callback.message.answer(f"❌ Доступ для користувача <code>{uid}</code> видалено.", parse_mode="HTML")
    else:
        await callback.message.answer("⚠️ Користувача не знайдено.")
    await callback.answer()