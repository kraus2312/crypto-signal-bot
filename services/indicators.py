import random

async def calculate_indicators(symbol: str, timeframe: str):
    # Тут можна буде додати реальні розрахунки через Binance API або TA-Lib
    close_price = round(random.uniform(100, 10000), 2)
    signal = random.choice(["LONG", "SHORT"])
    confidence = round(random.uniform(70, 95), 1)
    return {
        "close": close_price,
        "signal": signal,
        "confidence": confidence
    }
