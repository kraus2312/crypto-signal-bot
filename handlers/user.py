from aiogram import types
from aiogram.dispatcher import Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import ADMIN_ID, TRIAL_HOURS
from datetime import datetime, timedelta
import json
import os
from services.signals import generate_signal

DATA_FILE = "database/users.json"
HISTORY_FILE = "database/signals.json"
USER_STATE = {}

def load_users():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_users(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def save_signal_to_history(user_id, signal):
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            history = json.load(f)
    else:
        history = {}
    if str(user_id) not in history:
        history[str(user_id)] = []
    signal["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    history[str(user_id)].append(signal)
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

def has_access(user_id):
    users = load_users()
    if str(user_id) in users:
        if users[str(user_id)].get("banned"):
            return False
        access_until = users[str(user_id)].get("access_until")
        if access_until and datetime.strptime(access_until, "%Y-%m-%d %H:%M:%S") > datetime.now():
            return True
    return False

def register(dp: Dispatcher):
    @dp.message_handler(commands=["start"])
    async def start_handler(message: types.Message):
        user_id = str(message.from_user.id)
        users = load_users()
        if user_id not in users:
            trial_end = datetime.now() + timedelta(hours=TRIAL_HOURS)
            users[user_id] = {
                "username": message.from_user.username,
                "access_until": trial_end.strftime("%Y-%m-%d %H:%M:%S"),
                "banned": False
            }
            save_users(users)
            await message.answer(f"👋 Привіт! Безкоштовний доступ на 24 години до {trial_end.strftime('%Y-%m-%d %H:%M:%S')}")
        elif has_access(user_id):
            await message.answer("✅ У тебе є активний доступ.")
        else:
            await message.answer("⛔ Пробний період завершено. Напиши адміну @admin_username")
            return
        await show_coin_selection(message)

    @dp.message_handler(commands=["history"])
    async def history_command(message: types.Message):
    history = get_user_history(message.from_user.id)
    if not history:
        return await message.answer("📭 У вас ще немає збережених сигналів.")
    text = '🕓 <b>Ваші останні сигнали:</b>\n\n'
    for item in reversed(history):
        text += f"🕓 {item['timestamp'][:16]}\n<code>{item['text']}</code>\n"
        if item.get("image"):
            await message.answer_photo(open(item["image"], "rb"))
        text += "\n"
    await message.answer(text, parse_mode="HTML")
    async def history_handler(message: types.Message):
        user_id = str(message.from_user.id)
        if not has_access(user_id):
            await message.answer("⛔ Немає доступу.")
            return
        if not os.path.exists(HISTORY_FILE):
            await message.answer("📭 Історія порожня.")
            return
        with open(HISTORY_FILE, "r") as f:
            history = json.load(f)
        signals = history.get(user_id, [])
        if not signals:
            await message.answer("📭 Історія сигналів порожня.")
            return
        last_signals = signals[-5:]  # останні 5
        msg = "🕓 Останні сигнали:

"
        for s in reversed(last_signals):
            msg += f"{s['timestamp']} | {s['symbol']} {s['direction']} @ {s['price']} | TF: {s['interval']} | 🎯 {s['probability']}%
"
        await message.answer(msg)

    async def show_coin_selection(message):
        keyboard = InlineKeyboardMarkup(row_width=3)
        for coin in ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "PEPEUSDT", "TONUSDT"]:
            keyboard.insert(InlineKeyboardButton(coin, callback_data=f"coin_{coin}"))
        await message.answer("🔍 Обери монету:", reply_markup=keyboard)

    @dp.callback_query_handler(lambda c: c.data.startswith("coin_"))
    async def select_coin(call: types.CallbackQuery):
        coin = call.data.replace("coin_", "")
        USER_STATE[call.from_user.id] = {"symbol": coin}
        keyboard = InlineKeyboardMarkup(row_width=4)
        for tf in ["15m", "1h", "4h", "1d"]:
            keyboard.insert(InlineKeyboardButton(tf, callback_data=f"time_{tf}"))
        await call.message.answer(f"🕒 Обрано: {coin}. Тепер обери таймфрейм:", reply_markup=keyboard)

    @dp.callback_query_handler(lambda c: c.data.startswith("time_"))
    async def select_time(call: types.CallbackQuery):
        tf = call.data.replace("time_", "")
        USER_STATE[call.from_user.id]["interval"] = tf
        keyboard = InlineKeyboardMarkup(row_width=3)
        for lev in [1, 5, 10, 20, 50, 100]:
            keyboard.insert(InlineKeyboardButton(f"{lev}x", callback_data=f"lev_{lev}"))
        await call.message.answer("📐 Обери плече:", reply_markup=keyboard)

    @dp.callback_query_handler(lambda c: c.data.startswith("lev_"))
    async def select_leverage(call: types.CallbackQuery):
        lev = int(call.data.replace("lev_", ""))
        USER_STATE[call.from_user.id]["leverage"] = lev
        keyboard = InlineKeyboardMarkup(row_width=4)
        for risk in [0.5, 1, 2, 3]:
            keyboard.insert(InlineKeyboardButton(f"{risk}%", callback_data=f"risk_{risk}"))
        await call.message.answer("⚖️ Обери ризик:", reply_markup=keyboard)

    @dp.callback_query_handler(lambda c: c.data.startswith("risk_"))
    async def generate(call: types.CallbackQuery):
        risk = float(call.data.replace("risk_", ""))
        uid = call.from_user.id
        USER_STATE[uid]["risk"] = risk

        if not has_access(uid):
            await call.message.answer("⛔ Доступ завершено.")
            return

        s = USER_STATE[uid]
        signal = generate_signal(s["symbol"], s["interval"], s["leverage"], s["risk"])

        save_signal_to_history(uid, signal)

        msg = (
            f"{'🟢' if signal['direction']=='LONG' else '🔴'} 📈 {signal['direction']} Signal: {signal['symbol']} ({signal['interval']})
"
            f"💵 Ціна: ${signal['price']}
"
            f"📊 RSI: {signal['rsi']} | 📈 MACD: {signal['macd']} | 📏 EMA: {signal['ema']}
"
            f"🎯 Вірогідність: {signal['probability']}% ✅
"
            f"📐 Плече: {signal['leverage']}x

"
            f"🎯 TP1: ${signal['take_profits'][0]}
"
            f"🎯 TP2: ${signal['take_profits'][1]}
"
            f"🎯 TP3: ${signal['take_profits'][2]}
"
            f"🛡️ SL: ${signal['stop_loss']}

"
            f"⚖️ Ризик: {signal['risk_percent']}% → 💼 Позиція: ${signal['position_size']}
"
            f"📈 Профіт: +${signal['potential_profit']} | 📉 Збиток: -${signal['potential_loss']}"
        )
        await call.message.answer(msg)

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InputFile
from services.formatter import format_signal
import asyncio

async def send_trade_signal(message: types.Message, signal: dict):
    from services.plotter import generate_candlestick_image
from services.history import add_signal_to_history, get_user_history
from services.access_control import has_access
from services.strategy import analyze_signal  # функція, яку ми додамо

    # Генеруємо картинку свічкового графіка
    image_path = generate_candlestick_image(signal)

    # Форматуємо текст сигналу
    text = format_signal(signal)

    # Надсилаємо повідомлення з картинкою
    with open(image_path, "rb") as photo:
        await message.answer_photo(photo=photo, caption=text)

from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from services.formatter import format_signal
from services.plotter import generate_candlestick_image
from services.history import add_signal_to_history, get_user_history
from services.access_control import has_access
from services.strategy import analyze_signal
from aiogram import types
import asyncio

class SignalFSM(StatesGroup):
    choosing_symbol = State()
    choosing_interval = State()
    choosing_leverage = State()

@dp.message_handler(commands=["start"])
async def start_signal(message: types.Message):
    if not has_access(message.from_user.id):
        return await message.answer("❌ Ваш пробний доступ завершився. Активуйте підписку, щоб продовжити.")
    await message.answer("👋 Привіт! Я бот технічного аналізу криптовалют. Обери параметри для сигналу 👇")
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
    coins = [
        "BTC/USDT", "ETH/USDT", "BNB/USDT", "SOL/USDT", "XRP/USDT", "DOGE/USDT",
        "ADA/USDT", "AVAX/USDT", "DOT/USDT", "TRX/USDT", "LINK/USDT", "MATIC/USDT",
        "LTC/USDT", "SHIB/USDT", "BCH/USDT", "TON/USDT", "UNI/USDT", "ICP/USDT",
        "NEAR/USDT", "ETC/USDT", "FIL/USDT", "APT/USDT", "INJ/USDT", "HBAR/USDT",
        "STX/USDT", "OP/USDT", "ARB/USDT", "SUI/USDT", "LDO/USDT", "EGLD/USDT",
        "RNDR/USDT", "IMX/USDT", "TIA/USDT", "FTM/USDT", "CRO/USDT", "MKR/USDT",
        "PEPE/USDT", "GRT/USDT", "QNT/USDT", "AAVE/USDT", "XLM/USDT", "SEI/USDT",
        "RUNE/USDT", "FLOW/USDT", "SNX/USDT", "DYDX/USDT", "COMP/USDT", "ZIL/USDT",
        "WOO/USDT", "1INCH/USDT"
    ]
    for coin in coins:
        markup.add(KeyboardButton(coin))
    await message.answer("🔍 Оберіть монету:", reply_markup=markup)
    await SignalFSM.choosing_symbol.set()

@dp.message_handler(state=SignalFSM.choosing_symbol)
async def choose_interval(message: types.Message, state: FSMContext):
    await state.update_data(symbol=message.text)
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for tf in ["15m", "1h", "4h", "1d"]:
        markup.add(KeyboardButton(tf))
    await message.answer("🕒 Оберіть таймфрейм:", reply_markup=markup)
    await SignalFSM.choosing_interval.set()

@dp.message_handler(state=SignalFSM.choosing_interval)
async def choose_leverage(message: types.Message, state: FSMContext):
    await state.update_data(interval=message.text)
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for lev in ["1x", "5x", "10x", "20x", "50x", "100x"]:
        markup.add(KeyboardButton(lev))
    await message.answer("📐 Оберіть плече:", reply_markup=markup)
    await SignalFSM.choosing_leverage.set()

@dp.message_handler(state=SignalFSM.choosing_leverage)
async def finish_and_send_signal(message: types.Message, state: FSMContext):
    await state.update_data(leverage=int(message.text.replace("x", "")))
    data = await state.get_data()

    # Створюємо фейковий сигнал
    signal = analyze_signal(data["symbol"], data["interval"], data["leverage"])

    # Графік + текст
    image_path = generate_candlestick_image(signal)
    text = format_signal(signal)

    with open(image_path, "rb") as photo:
        await message.answer_photo(photo=photo, caption=text)

    await state.finish()

from services.history import add_signal_to_history, get_user_history
from services.access_control import check_user_access, load_access_data
from datetime import datetime

@dp.message_handler(commands=["help"])
async def help_command(message: types.Message):
    await message.answer(
        "❓ <b>Допомога</b>

"
        "• /start — перезапустити бота
"
        "• /help — список команд
"
        "• /subscription — статус доступу
"
        "• /history — останні сигнали
",
        parse_mode="HTML"
    )

@dp.message_handler(commands=["subscription"])
async def subscription_command(message: types.Message):
    data = load_access_data()
    user_id = str(message.from_user.id)
    if user_id not in data:
        return await message.answer("⛔ Ви не зареєстровані.")
    access = data[user_id]
    text = f"📅 Дата реєстрації: <code>{access['start']}</code>"
    if "premium_until" in access:
        text += f"
💎 Преміум до: <code>{access['premium_until']}</code>"
    else:
        text += "
🧪 Ви на пробному доступі."
    await message.answer(text, parse_mode="HTML")

@dp.message_handler(commands=["history"])
async def history_command(message: types.Message):
    history = get_user_history(message.from_user.id)
    if not history:
        return await message.answer("📭 У вас ще немає збережених сигналів.")
    text = '🕓 <b>Ваші останні сигнали:</b>\n\n'
    for item in reversed(history):
        text += f"🕓 {item['timestamp'][:16]}\n<code>{item['text']}</code>\n"
        if item.get("image"):
            await message.answer_photo(open(item["image"], "rb"))
        text += "\n"
    await message.answer(text, parse_mode="HTML")
async def history_command(message: types.Message):
    await message.answer("📊 Історія сигналів тимчасово недоступна. У майбутньому ви зможете переглядати свої останні сигнали.")