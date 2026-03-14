import pandas as pd
from datetime import timedelta
from enum import Enum

from models import forming_candle
from models.timeframe import Timeframe
from strategies.strategy import Strategy
from strategies.strategy_manager import StrategyManager
from broker.virtual_broker import VirtualBroker
from broker.metrics_engine import MetricsEngine

candles = pd.read_csv("BTCUSDT-1m-100k.csv")
candles.columns = ["open_time", "open", "high", "low", "close", "volume", "close_time", "quote_volume", "count", "taker_buy_volume", "taker_buy_quote_volume", "ignore"]

# Some rows have microsecond timestamps (16 digits) instead of millisecond (13 digits) — normalize them
mask = candles["open_time"] > 1e15
candles.loc[mask, "open_time"] = candles.loc[mask, "open_time"] // 1000
candles.loc[mask, "close_time"] = candles.loc[mask, "close_time"] // 1000

candles["open_time"] = pd.to_datetime(candles["open_time"], unit="ms")
print(f"Loaded {len(candles)} candles")

STARTING_CAPITAL = 10_000
broker = VirtualBroker(starting_capital=STARTING_CAPITAL)

strategy_1 = Strategy(name="Test Strategy1", timeframe=Timeframe.MINUTE_30)
strategy_2 = Strategy(name="Test Strategy2", timeframe=Timeframe.HOUR_4)

manager = StrategyManager()
manager.add_strategy(strategy_1)
manager.add_strategy(strategy_2)

for _, row in candles.iterrows():
    row_dict = row.to_dict()

    # Fill signals queued on the previous tick at this candle's open price
    broker.fill_pending(open_price=row_dict["open"], open_time=row_dict["open_time"])

    # Check SL/TP for all open positions against this candle's high/low
    broker.check_sl_tp(row_dict)

    # Get new signals from all strategies for this 1m candle
    signals = manager.update(row_dict)

    # Queue each returned signal with the broker
    for strategy_name, signal in signals.items():
        if isinstance(signal, list):
            for s in signal:
                broker.submit_signal(s, strategy_name)
        else:
            broker.submit_signal(signal, strategy_name)

# Close any positions still open at end of data
last_row = candles.iloc[-1].to_dict()
broker.close_all(exit_price=last_row["close"], exit_time=last_row["open_time"])

metrics = MetricsEngine.compute(broker.closed_positions, STARTING_CAPITAL)

print()
print("=" * 42)
print(f"{'BACKTEST RESULTS':^42}")
print("=" * 42)
print(f"{'Trades':<20}: {metrics['total_trades']:>8}")
print(f"{'Win Rate':<20}: {metrics['win_rate']:>7.2f} %")
print(f"{'Total PnL':<20}: {metrics['total_pnl']:>+10.2f}  ({metrics['total_pnl_pct']:+.2f} %)")
print(f"{'Avg Win':<20}: {metrics['avg_win']:>+10.2f}")
print(f"{'Avg Loss':<20}: {metrics['avg_loss']:>+10.2f}")
print(f"{'Profit Factor':<20}: {metrics['profit_factor']:>10.2f}")
print(f"{'Max Drawdown':<20}: {metrics['max_drawdown']:>8.2f} %")
print(f"{'Sharpe Ratio':<20}: {metrics['sharpe_ratio']:>10.2f}")
print("=" * 42)
