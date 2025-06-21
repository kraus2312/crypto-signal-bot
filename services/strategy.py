import pandas as pd
from binance.client import Client
from ta.momentum import RSIIndicator
from ta.trend import MACD, EMAIndicator
from datetime import datetime
import os

# Binance API (можна використати без ключа — public endpoint)
client = Client()

def get_klines(symbol: str, interval: str, limit: int = 150):
    """Отримати OHLCV дані з Binance"""
    data = client.get_klines(symbol=symbol.replace("/", ""), interval=interval, limit=limit)
    df = pd.DataFrame(data, columns=[
        "timestamp", "open", "high", "low", "close", "volume",
        "close_time", "quote_asset_volume", "number_of_trades",
        "taker_buy_base_volume", "taker_buy_quote_volume", "ignore"
    ])
    df["close"] = df["close"].astype(float)
    df["open"] = df["open"].astype(float)
    df["high"] = df["high"].astype(float)
    df["low"] = df["low"].astype(float)
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    return df

def analyze_signal(symbol: str, interval: str, leverage: int):
    df = get_klines(symbol, interval)

    # Індикатори
    rsi = RSIIndicator(close=df["close"]).rsi().iloc[-1]
    macd = MACD(close=df["close"]).macd_diff().iloc[-1]
    ema = EMAIndicator(close=df["close"], window=20).ema_indicator().iloc[-1]

    # Поточна ціна
    price = df["close"].iloc[-1]

    # Напрям сигналу
    direction = "LONG" if macd > 0 and price > ema else "SHORT"

    # Вірогідність — умовна оцінка
    probability = round(70 + min(abs(macd * 100), 15), 1)

    # Take Profits / Stop Loss
    tp1 = round(price * (1.01 if direction == "LONG" else 0.99), 2)
    tp2 = round(price * (1.02 if direction == "LONG" else 0.98), 2)
    tp3 = round(price * (1.03 if direction == "LONG" else 0.97), 2)
    sl = round(price * (0.98 if direction == "LONG" else 1.02), 2)

    # Ризик фіксований (2%), позиція — 100 USDT
    risk = 2
    position = 100
    profit = round(position * (tp2 / price - 1), 2)
    loss = round(position * (1 - sl / price), 2)

    return {
        "direction": direction,
        "symbol": symbol,
        "interval": interval,
        "price": round(price, 2),
        "rsi": round(rsi, 2),
        "macd": round(macd, 4),
        "ema": round(ema, 2),
        "probability": probability,
        "leverage": leverage,
        "take_profits": [tp1, tp2, tp3],
        "stop_loss": sl,
        "risk_percent": risk,
        "position_size": position,
        "potential_profit": profit,
        "potential_loss": loss
    }