import yfinance as yf
import pandas as pd
from datetime import datetime
import requests

from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from bokeh.plotting import output_file, save

# ============================================================
#   DESCARGA DE DATOS
# ============================================================
def get_data(ticker="AAPL", period="1y", interval="1d"):
    df = yf.download(ticker, period=period, interval=interval)

    # Aplanar columnas si son MultiIndex
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[0] for col in df.columns]

    df.dropna(inplace=True)
    return df


# ============================================================
#   INDICADORES (RSI Y EMA)
# ============================================================
def RSI(series, period=14):
    series = pd.Series(series)
    delta = series.diff()
    gain = delta.where(delta > 0, 0).rolling(period).mean()
    loss = -delta.where(delta < 0, 0).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


def EMA(series, period):
    series = pd.Series(series)
    return series.ewm(span=period, adjust=False).mean()


# ============================================================
#   FEAR & GREED INDEX
# ============================================================
def get_fear_greed(api_url="https://api.alternative.me/fng/"):
    response = requests.get(api_url, params={"limit": 1})
    response.raise_for_status()
    latest = response.json()["data"][0]
    return int(latest["value"]), latest["value_classification"], datetime.fromtimestamp(int(latest["timestamp"]))


# ============================================================
#   ESTRATEGIA: EMA 5/20 + RSI + FGI
# ============================================================
class EmaRsiStrategy(Strategy):
    fgi_value = 0

    def init(self):
        close = self.data.Close
        self.ema5 = self.I(EMA, close, 5)
        self.ema20 = self.I(EMA, close, 20)
        self.rsi = self.I(RSI, close, 14)

    def next(self):
        if self.fgi_value > 70:
            return

        if crossover(self.ema5, self.ema20) and self.rsi[-1] < 30:
            self.buy()

        elif crossover(self.ema20, self.ema5) or self.rsi[-1] > 70:
            self.sell()


# ============================================================
#   MAIN
# ============================================================
def main():
    ticker = "AAPL"
    df = get_data(ticker)
    fgi_value, sentiment, timestamp = get_fear_greed()

    print(f"\n📊 FGI: {fgi_value} ({sentiment}) — {timestamp.strftime('%Y-%m-%d')}")

    EmaRsiStrategy.fgi_value = fgi_value

    bt = Backtest(df, EmaRsiStrategy,
                  commission=0.002,
                  exclusive_orders=True,
                  finalize_trades=True)

    stats = bt.run()

    # Guardar gráfico en HTML
    html_file = f"backtest_{ticker}_ema_rsi.html"
    output_file(html_file)
    save(bt.plot())

    print("\n📈 Resultados del Backtest:")
    for key in ['# Trades', 'Return [%]', 'Max. Drawdown [%]', 'Sharpe Ratio', 'Win Rate [%]']:
        print(f"{key}: {stats.get(key)}")


if __name__ == "__main__":
    main()
