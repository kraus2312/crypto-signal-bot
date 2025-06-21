# 📊 Crypto Signal Bot (Python 3.13.4 Compatible)

Telegram-бот для отримання торгових сигналів з технічним аналізом на основі RSI, MACD, EMA. Працює з Binance API, генерує графіки, підтримує пробний доступ, платні підписки, історію сигналів та адмін-панель.

---

## ✅ Основні можливості:
- Теханаліз (RSI, MACD, EMA)
- Вірогідність входу, TP1/TP2/TP3 + SL, плечі до 100x
- Пробний доступ 24 години
- Платні тарифи (1д/3д/м/рік)
- Адмін-панель з керуванням користувачами
- Telegram-інтерфейс українською

---

## 🧱 Технології
- Python 3.13.4
- Aiogram 2.25.2
- Binance API (`python-binance`)
- TA Indicators (`ta`)
- Pandas, Matplotlib, NumPy

---

## 🚀 Запуск локально

### 1. Встановіть Python 3.13.4
[Завантажити з python.org](https://www.python.org/downloads/release/python-3134/)

### 2. Клонуйте репозиторій або розпакуйте ZIP
```bash
unzip final_crypto_signal_bot_py313_full_fixed.zip
cd final_crypto_signal_bot_fixed
```

### 3. Створіть та активуйте віртуальне середовище
```bash
python -m venv .venv
source .venv/bin/activate  # або .venv\Scripts\activate на Windows
```

### 4. Встановіть залежності
```bash
pip install -r requirements.txt
```

### 5. Запуск
```bash
python main.py
```

---

## ☁️ Деплой на Render.com

1. Залийте проект на GitHub
2. Створіть Web Service на [Render.com](https://render.com/)
3. У середовищі додайте:
   - `PYTHON_VERSION = 3.13.4`
   - `BOT_TOKEN`, `BINANCE_API_KEY`, `BINANCE_SECRET_KEY` — у Settings > Environment
4. У `Start Command` введіть:
```bash
python main.py
```

---

## 🛠 Змінні середовища (env)
У `.env` або в Render:
- `BOT_TOKEN` — токен Telegram бота
- `BINANCE_API_KEY` і `BINANCE_SECRET_KEY` — ключі Binance

---

## 🧑‍💻 Автор / Підтримка
- Код оновлено для сумісності з Python 3.13.4
- Telegram-бот написаний з урахуванням кращих практик Python/AsyncIO

---

## 🔐 Права
Використання лише з освітньою або тестовою метою. Торгівля — на ваш страх і ризик.
