
def format_signal(signal: dict) -> str:
    return (
        f"{'🟢' if signal['direction'] == 'LONG' else '🔴'} 📈 {signal['direction']} Signal: {signal['symbol']} ({signal['interval']})\n"
        f"💵 Ціна: ${signal['price']}\n"
        f"📊 RSI: {signal['rsi']} | 📈 MACD: {signal['macd']} | 📏 EMA: {signal['ema']}\n"
        f"🎯 Вірогідність: {signal['probability']}% ✅\n"
        f"📐 Плече: {signal['leverage']}x\n\n"
        f"🎯 TP1: ${signal['take_profits'][0]}\n"
        f"🎯 TP2: ${signal['take_profits'][1]}\n"
        f"🎯 TP3: ${signal['take_profits'][2]}\n"
        f"🛡️ SL: ${signal['stop_loss']}\n\n"
        f"⚖️ Ризик: {signal['risk_percent']}% → 💼 Позиція: ${signal['position_size']}\n"
        f"📈 Профіт: +${signal['potential_profit']} | 📉 Збиток: -${signal['potential_loss']}"
    )
