import yfinance as yf
from datetime import datetime
import requests

def get_data(ticker, period="1y", interval="1d"):
    data = yf.download(ticker, period=period, interval=interval)
    return data

# Ejemplo de análisis técnico simple
def calculate_volatility(df):
    df["returns"] = df["Close"].pct_change()  # antes era 'Adj Close'
    volatility = df["returns"].std() * (252 ** 0.5)
    return volatility

def get_fear_greed(api_url="https://api.alternative.me/fng/"):
    response = requests.get(api_url, params={"limit": 1})
    response.raise_for_status()
    payload = response.json()
    latest = payload["data"][0]
    return {
        "value": int(latest["value"]),
        "classification": latest["value_classification"],
        "timestamp": datetime.fromtimestamp(int(latest["timestamp"]))
    }

def main():
    tickers = ["AAPL", "MSFT", "TSLA"]
    for ticker in tickers:
        df = get_data(ticker)
        vol = calculate_volatility(df)
        print(f"{ticker}: Volatilidad anualizada = {vol:.2%}")

if __name__ == "__main__":
    main()
