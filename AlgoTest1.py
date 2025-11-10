import yfinance as yf
from datetime import datetime
import requests

# cd C:\Users\horat\Documents\MyAlgoProject
# git init
# git remote add origin https://github.com/HoratiuMol/myInvestmentAlgorythm.git
# git add AlgoTest1.py
# git commit -m "commit code"
# git branch -M main
# git push -u origin main


#NEW MODIFICATIONS AFTER DOING THE CD
# git add .
# git commit -m "Describe what you changed"
# git push

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

def interpret_fgi(value):
    if value <=5:
        return ("BUY BUY BUY BUY BUY NOW")
    elif value <= 20:
        return ("Extreme Fear", "✅ MARKET OPPORTUNITY: Consider other indicators also")
    elif value <= 49:
        return ("Fear", "⚠️ Market is cautious. Avoid impulsive entries.")
    elif value <= 75:
        return ("Greed", "⚠️ Market shows greed. Be selective and protect gains.")
    elif value <=90:
        return ("consider sell")
    else:
        return ("Extreme Greed", "❌ MARKET RISK: Avoid new buys. Watch for corrections.")
    
def main():
    tickers = ["AAPL", "MSFT", "TSLA"]
    
    #we print the sentiment interpreations
    fgi = get_fear_greed()
    sentiment, action = interpret_fgi(fgi["value"])
    
    print(f"\n📊 Fear & Greed Index: {fgi['value']} ({sentiment})")
    print(f"🗓️ As of: {fgi['timestamp'].strftime('%Y-%m-%d')}")
    print(f"💡 Strategy Suggestion: {action}\n")
    
    for ticker in tickers:
        df = get_data(ticker)
        vol = calculate_volatility(df)
        print(f"{ticker}: Volatilidad anualizada = {vol:.2%}")

if __name__ == "__main__":
    main()
