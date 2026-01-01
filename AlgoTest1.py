# test
import yfinance as yf
from datetime import datetime
import requests
import matplotlib
import webbrowser
import pandas as pd
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import SMA
from bokeh.plotting import output_file

matplotlib.use('Qt5Agg')

# Obtener datos históricos de GOOG
def get_data(ticker="GOOG", period="1y", interval="1d"):
    data = yf.download(ticker, period=period, interval=interval)
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = [col[0] for col in data.columns]
    return data

# Calcular la volatilidad anualizada
def calculate_volatility(df):
    df["returns"] = df["Close"].pct_change()
    volatility = df["returns"].std() * (252 ** 0.5)
    return volatility

# Obtener el índice de miedo y codicia (FGI)
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

# Interpretación del FGI
def interpret_fgi(value):
    if value <= 5:
        return ("BUY NOW", "✅ MARKET OPPORTUNITY: Act decisively")
    elif value <= 20:
        return ("Extreme Fear", "✅ MARKET OPPORTUNITY: Consider other indicators also")
    elif value <= 49:
        return ("Fear", "⚠️ Market is cautious. Avoid impulsive entries.")
    elif value <= 75:
        return ("Greed", "⚠️ Market shows greed. Be selective and protect gains.")
    elif value <= 90:
        return ("Consider Selling", "❌ Watch out, market overheating")
    else:
        return ("Extreme Greed", "❌ MARKET RISK: Avoid new buys. Watch for corrections.")

# Estrategia de Cruce de Medias con filtro FGI
class SmaCross(Strategy):
    fgi_value = 0

    def init(self):
        price = self.data.Close
        self.ma1 = self.I(SMA, price, 10)
        self.ma2 = self.I(SMA, price, 20)

    def next(self):
        if self.fgi_value > 49:
            return
        if crossover(self.ma1, self.ma2):
            self.buy()
        elif crossover(self.ma2, self.ma1):
            self.sell()

# Función principal
def main():
    ticker = "GOOG"
    df = get_data(ticker)

    if df.empty or not all(col in df.columns for col in ['Open', 'High', 'Low', 'Close']):
        print(f"❌ Error: Datos inválidos para {ticker}")
        return

    vol = calculate_volatility(df)
    print(f"{ticker}: Volatilidad anualizada = {vol:.2%}")

    fgi = get_fear_greed()
    sentiment, action = interpret_fgi(fgi["value"])

    print(f"\n📊 FGI: {fgi['value']} ({sentiment})")
    print(f"💡 Strategy Suggestion: {action}\n")

    SmaCross.fgi_value = fgi["value"]

    bt = Backtest(df, SmaCross, commission=.002, exclusive_orders=True, finalize_trades=True)
    stats = bt.run()

    html_file = f"backtest_{ticker}.html"
    output_file(html_file)
    bt.plot(filename=html_file)
    webbrowser.open(html_file)

    print(f"\n📈 Resultados del Backtest para {ticker}:")
    print(f"🔁 Total Trades: {stats['# Trades']}")
    print(f"📊 Retorno total: {stats['Return [%]']:.2f}%")
    print(f"📉 Max Drawdown: {stats['Max. Drawdown [%]']:.2f}%")
    print(f"📈 Mejor Trade: {stats['Best Trade [%]']:.2f}%")
    print(f"📉 Peor Trade: {stats['Worst Trade [%]']:.2f}%")
    print(f"⚖️ Ratio Sharpe: {stats['Sharpe Ratio']:.2f}")
    print(f"✅ Ganadoras: {stats['Win Rate [%]']:.2f}%")
    print("-" * 50)

if __name__ == "__main__":
    main()
