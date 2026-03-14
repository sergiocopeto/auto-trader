import pandas as pd
from datetime import timedelta
from enum import Enum

from models import forming_candle
from models.timeframe import Timeframe
from strategies.strategy import Strategy
from strategies.strategy_manager import StrategyManager

candles = pd.read_csv("BTCUSDT-1m-100k.csv")
candles.columns = ["open_time", "open", "high", "low", "close", "volume", "close_time", "quote_volume", "count", "taker_buy_volume", "taker_buy_quote_volume", "ignore"]

# Some rows have microsecond timestamps (16 digits) instead of millisecond (13 digits) — normalize them
mask = candles["open_time"] > 1e15
candles.loc[mask, "open_time"] = candles.loc[mask, "open_time"] // 1000
candles.loc[mask, "close_time"] = candles.loc[mask, "close_time"] // 1000

candles["open_time"] = pd.to_datetime(candles["open_time"], unit="ms")
print(f"Loaded {len(candles)} candles")

strategy_1 = Strategy(name="Test Strategy1", timeframe=Timeframe.MINUTE_30)
strategy_2 = Strategy(name="Test Strategy2", timeframe=Timeframe.HOUR_4)

manager = StrategyManager()
manager.add_strategy(strategy_1)
manager.add_strategy(strategy_2)

for _, row in candles.iterrows():
    row_dict = row.to_dict()
    result = manager.update(row_dict)
    if result:
        print(result)