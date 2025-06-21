from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

subscribe_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="1 день - 100 грн ($2.5)", callback_data="sub_1")],
    [InlineKeyboardButton(text="7 днів - 500 грн ($12)", callback_data="sub_7")],
    [InlineKeyboardButton(text="1 місяць - 1500 грн – 1500 грн ($35)", callback_data="sub_30")],
    [InlineKeyboardButton(text="6 місяців - 4000 грн – 4000 грн ($95)", callback_data="sub_180")],
    [InlineKeyboardButton(text="1 рік - 7000 грн – 7000 грн ($165)", callback_data="sub_365")]
])