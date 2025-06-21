from aiogram import types
from aiogram.dispatcher import FSMContext
from keyboards.inline.subscribe import get_subscribe_keyboard
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from loader import dp, db
from services import formatter, signals, signal_sender
from aiogram.dispatcher.filters import Command
import json
import os

@dp.message_handler(commands=["start", "menu"])
async def start_signal(message: types.Message):
    await message.answer("👋 Привіт! Я бот для криптосигналів.

Щоб отримувати сигнали, натисни кнопку нижче 👇")
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("📈 Отримати сигнал"))
    markup.add(KeyboardButton("🕓 Історія сигналів"))
    await message.answer("📍 Обери дію:", reply_markup=markup)

@dp.message_handler(lambda m: m.text == "🕓 Історія сигналів")
async def show_history(message: types.Message):
    user_id = str(message.from_user.id)
    path = f"database/users.json"

    if not os.path.exists(path):
        await message.answer("Історія відсутня.")
        return

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if user_id not in data or not data[user_id]["history"]:
        await message.answer("Історія порожня.")
        return

    last_signals = data[user_id]["history"][-5:]
    msg = "🕓 Останні сигнали:
"
    for s in reversed(last_signals):
        msg += f"{s['timestamp']} | {s['symbol']} {s['direction']} @ {s['price']} | TF: {s['interval']} | 🎯 {s['probability']}%
"

    await message.answer(msg)

def register(dp):
    dp.register_message_handler(start_signal, commands=["start", "menu"])
    dp.register_message_handler(show_history, lambda m: m.text == "🕓 Історія сигналів")