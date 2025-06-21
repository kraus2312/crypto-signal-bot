import random
from services.indicators import calculate_indicators

async def generate_signal(symbol: str, timeframe: str = "1h"):
    indicators = await calculate_indicators(symbol, timeframe)
    entry = round(indicators['close'], 2)
    tp1 = round(entry * 1.01, 2)
    tp2 = round(entry * 1.02, 2)
    tp3 = round(entry * 1.03, 2)
    sl = round(entry * 0.98, 2)
    signal_type = indicators['signal']
    confidence = indicators['confidence']

    return {
        "pair": symbol,
        "timeframe": timeframe,
        "entry": entry,
        "tp1": tp1,
        "tp2": tp2,
        "tp3": tp3,
        "sl": sl,
        "signal": signal_type,
        "confidence": confidence
    }
