
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import os

def generate_candlestick_image(signal: dict) -> str:
    dates = [datetime.now() - timedelta(minutes=15 * i) for i in range(30)][::-1]
    open_prices = np.linspace(signal['price'] * 0.98, signal['price'] * 1.02, 30)
    high_prices = open_prices + np.random.uniform(5, 30, 30)
    low_prices = open_prices - np.random.uniform(5, 30, 30)
    close_prices = open_prices + np.random.uniform(-15, 15, 30)

    df = pd.DataFrame({
        'Date': dates,
        'Open': open_prices,
        'High': high_prices,
        'Low': low_prices,
        'Close': close_prices
    })

    ohlc_data = [
        [mdates.date2num(row['Date']), row['Open'], row['High'], row['Low'], row['Close']]
        for index, row in df.iterrows()
    ]

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.xaxis_date()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

    for date, open_, high, low, close in ohlc_data:
        color = 'green' if close >= open_ else 'red'
        ax.plot([date, date], [low, high], color='black')
        ax.add_patch(plt.Rectangle((date - 0.01, min(open_, close)), 0.02, abs(close - open_), color=color))

    # Entry
    ax.axhline(signal['price'], color='black', linestyle='--', linewidth=1)
    ax.text(dates[-1], signal['price'], f"Entry: ${signal['price']}", color='black', va='bottom', ha='right', fontsize=9)

    # TP levels
    for i, tp in enumerate(signal['take_profits'], 1):
        ax.axhline(tp, color='green', linestyle='--', linewidth=1)
        ax.text(dates[-1], tp, f"TP{i}: ${tp}", color='green', va='bottom', ha='right', fontsize=9)

    # SL
    ax.axhline(signal['stop_loss'], color='red', linestyle='--', linewidth=1)
    ax.text(dates[-1], signal['stop_loss'], f"SL: ${signal['stop_loss']}", color='red', va='top', ha='right', fontsize=9)

    ax.set_title(f"Свічковий графік {signal['symbol']} ({signal['interval']})", fontsize=14)
    ax.set_ylabel("Ціна USDT")
    ax.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()

    filename = f"{signal['symbol'].replace('/', '')}_{signal['interval']}.png"
    path = f"/mnt/data/{filename}"
    plt.savefig(path)
    plt.close()

    return path
