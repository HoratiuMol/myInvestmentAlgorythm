import yfinance as yf
from datetime import datetime
import requests
import matplotlib
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import SMA, GOOG
from bokeh.plotting import output_file, save
import os
import webbrowser

matplotlib.use('Qt5Agg')

# ----------------------------------------------------
# Funciones auxiliares
# ----------------------------------------------------
# -------------------------------------------
#-------------------Comandos git inicales
# cd C:\Users\horat\Documents\MyAlgoProject
# git init
# git remote add origin https://github.com/HoratiuMol/myInvestmentAlgorythm.git
# git add AlgoTest1.py
# git commit -m "commit code"
# git branch -M main
# git push -u origin main
#----------------------------------------------
#-----------Comando Git actualziar------------
# git add .
# git commit -m "Describe what you changed"
# git push
#-------------------------------------------
def get_data(ticker, period="1y", interval="1d"):
    data = yf.download(ticker, period=period, interval=interval)
    return data

def calculate_volatility(df):
    df["returns"] = df["Close"].pct_change()
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
    if value <= 5:
        return ("BUY BUY BUY BUY BUY NOW")
    elif value <= 20:
        return ("Extreme Fear", "✅ MARKET OPPORTUNITY: Consider other indicators also")
    elif value <= 49:
        return ("Fear", "⚠️ Market is cautious. Avoid impulsive entries.")
    elif value <= 75:
        return ("Greed", "⚠️ Market shows greed. Be selective and protect gains.")
    elif value <= 90:
        return ("consider sell")
    else:
        return ("Extreme Greed", "❌ MARKET RISK: Avoid new buys. Watch for corrections.")

# ----------------------------------------------------
# Estrategia con FGI
# ----------------------------------------------------

class SmaCross(Strategy):
    fgi_value = 0  # Valor del índice de miedo y codicia
    
    def init(self):
        price = self.data.Close
        self.ma1 = self.I(SMA, price, 10)
        self.ma2 = self.I(SMA, price, 20)

    def next(self):
        if self.fgi_value > 49:
            return  # Evitar operar en condiciones de codicia
        if crossover(self.ma1, self.ma2):
            self.buy()
        elif crossover(self.ma2, self.ma1):
            self.sell()

# ----------------------------------------------------
# Función principal
# ----------------------------------------------------

def main():
    fgi = get_fear_greed()
    sentiment, action = interpret_fgi(fgi["value"])

    print(f"\n📊 FGI: {fgi['value']} ({sentiment})")
    print(f"💡 Strategy Suggestion: {action}\n")

    SmaCross.fgi_value = fgi["value"]

    bt = Backtest(GOOG, SmaCross,
                  commission=.002,
                  exclusive_orders=True,
                  finalize_trades=True)

    stats = bt.run()

    # Mostrar y guardar gráfico
    plot = bt.plot()
    output_path = os.path.join(os.getcwd(), "backtest_result.html")
    output_file(output_path)
    save(plot)
    print(f"\n✅ Gráfico guardado en: {output_path}")
    # 🟢 Abrir automáticamente en el navegador
    
    webbrowser.open(output_path)

    print(f"\n✅ Gráfico guardado en: {output_path}")

    # Mostrar stats
    print("\n📈 Resultados del Backtest:")
    print(f"🔁 Total Trades: {stats['# Trades']}")
    print(f"📊 Retorno total: {stats['Return [%]']:.2f}%")
    print(f"📉 Max Drawdown: {stats['Max. Drawdown [%]']:.2f}%")
    print(f"📈 Mejor Trade: {stats['Best Trade [%]']:.2f}%")
    print(f"📉 Peor Trade: {stats['Worst Trade [%]']:.2f}%")
    print(f"⚖️ Ratio Sharpe: {stats['Sharpe Ratio']:.2f}")
    print(f"✅ Ganadoras: {stats['Win Rate [%]']:.2f}%")
    print(stats)

# ----------------------------------------------------

if __name__ == "__main__":
    main()
