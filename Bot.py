import requests
import time
import pandas as pd

TOKEN = "PUT_YOUR_BOT_TOKEN_HERE"
CHAT_ID = "7218908686"

BINANCE = "https://api.binance.com/api/v3"


# ================= TELEGRAM =================
def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.get(url, params={"chat_id": CHAT_ID, "text": text})


# ================= SYMBOLS =================
def get_usdt_symbols():
    data = requests.get(f"{BINANCE}/exchangeInfo").json()
    symbols = []
    for s in data["symbols"]:
        if s["quoteAsset"] == "USDT" and s["status"] == "TRADING":
            symbols.append(s["symbol"])
    return symbols[:50]  # برای سبک بودن


# ================= PRICE DATA =================
def get_klines(symbol):
    url = f"{BINANCE}/klines"
    params = {"symbol": symbol, "interval": "5m", "limit": 100}
    data = requests.get(url, params=params).json()
    closes = [float(c[4]) for c in data]
    return closes


# ================= RSI =================
def rsi(prices, period=14):
    prices = pd.Series(prices)
    delta = prices.diff()

    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))

    return rsi.iloc[-1]


# ================= MACD =================
def macd(prices):
    prices = pd.Series(prices)

    ema12 = prices.ewm(span=12).mean()
    ema26 = prices.ewm(span=26).mean()

    macd_line = ema12 - ema26
    signal = macd_line.ewm(span=9).mean()

    return macd_line.iloc[-1], signal.iloc[-1]


# ================= EMA TREND =================
def ema_trend(prices):
    prices = pd.Series(prices)

    ema50 = prices.ewm(span=50).mean().iloc[-1]
    ema200 = prices.ewm(span=200).mean().iloc[-1]

    return ema50, ema200


# ================= SUPER TREND (simplified) =================
def supertrend(prices):
    prices = pd.Series(prices)

    atr = prices.diff().abs().rolling(10).mean()
    hl2 = prices.rolling(2).mean()

    upper = hl2 + (2 * atr)
    lower = hl2 - (2 * atr)

    if prices.iloc[-1] > upper.iloc[-1]:
        return "up"
    elif prices.iloc[-1] < lower.iloc[-1]:
        return "down"
    else:
        return "neutral"


# ================= MAIN =================
symbols = get_usdt_symbols()

send_message("🚀 Bot Started Successfully")

while True:
    for sym in symbols:
        try:
            prices = get_klines(sym)

            r = rsi(prices)
            m, s = macd(prices)
            ema50, ema200 = ema_trend(prices)
            st = supertrend(prices)

            price = prices[-1]

            # BUY
            if r < 30 and m > s and ema50 > ema200 and st == "up":
                send_message(
                    f"""🟢 BUY SIGNAL

{sym}
Price: {price}
RSI: {r:.2f}
MACD: Bullish
Trend: UP
"""
                )

            # SELL
            elif r > 70 and m < s and ema50 < ema200 and st == "down":
                send_message(
                    f"""🔴 SELL SIGNAL

{sym}
Price: {price}
RSI: {r:.2f}
MACD: Bearish
Trend: DOWN
"""
                )

        except Exception as e:
            print(sym, e)

    time.sleep(300)
