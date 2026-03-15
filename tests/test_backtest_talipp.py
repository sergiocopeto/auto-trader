import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd

from models.timeframe import Timeframe
from implementations.talipp_rsi_strategy import TalippRSIStrategy
from strategies.strategy_manager import StrategyManager
from broker.virtual_broker import VirtualBroker
from broker.metrics_engine import MetricsEngine

candles = pd.read_csv("BTCUSDT-1m-100k.csv")
candles.columns = ["open_time", "open", "high", "low", "close", "volume", "close_time", "quote_volume", "count", "taker_buy_volume", "taker_buy_quote_volume", "ignore"]

mask = candles["open_time"] > 1e15
candles.loc[mask, "open_time"] = candles.loc[mask, "open_time"] // 1000
candles.loc[mask, "close_time"] = candles.loc[mask, "close_time"] // 1000

candles["open_time"] = pd.to_datetime(candles["open_time"], unit="ms")
print(f"Loaded {len(candles)} candles")

STARTING_CAPITAL = 10_000
broker = VirtualBroker(starting_capital=STARTING_CAPITAL)

strategy = TalippRSIStrategy(name="Talipp RSI 1h", timeframe=Timeframe.HOUR_1)

manager = StrategyManager()
manager.add_strategy(strategy)

for _, row in candles.iterrows():
    row_dict = row.to_dict()

    broker.fill_pending(open_price=row_dict["open"], open_time=row_dict["open_time"])
    broker.check_sl_tp(row_dict)

    signals = manager.update(row_dict)

    for strategy_name, signal in signals.items():
        if isinstance(signal, list):
            for s in signal:
                broker.submit_signal(s, strategy_name)
        else:
            broker.submit_signal(signal, strategy_name)

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
