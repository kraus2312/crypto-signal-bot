from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

admin_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🔓 Активувати підписку", callback_data="admin_activate")],
    [InlineKeyboardButton(text="🚫 Заборонити доступ", callback_data="admin_block")],
    [InlineKeyboardButton(text="📜 Список користувачів", callback_data="admin_users")],
    [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")]
])