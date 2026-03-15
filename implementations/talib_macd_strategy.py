try:
    import talib
except ImportError as e:
    raise ImportError(
        "TA-Lib is not installed. Run `poetry install -E talib` to install it."
    ) from e

import numpy as np

from models.position import Position
from strategies.strategy import Strategy


class TALibMACDStrategy(Strategy):
    def __init__(self, name: str, timeframe, max_candles: int = 1000) -> None:
        super().__init__(name=name, timeframe=timeframe, max_candles=max_candles)

    def process_new_candle(self) -> dict | None:
        arrays = self.candles.to_numpy()

        if len(arrays["close"]) < 35:
            return None

        macd, signal, hist = talib.MACD(arrays["close"])

        if np.isnan(hist[-1]) or np.isnan(hist[-2]):
            return None

        # MACD histogram crossed above zero → bullish signal
        if hist[-1] > 0 and hist[-2] <= 0:
            close = float(arrays["close"][-1])
            position = Position(
                entry_price=close,
                quantity=1,
                stop_loss=close * 0.95,
                take_profit=close * 1.05,
                entry_time=arrays["open_time"][-1],
            )
            return position.to_dict()

        return None
