from talipp.indicators import RSI

from models.position import Position
from strategies.strategy import Strategy


class TalippRSIStrategy(Strategy):
    """RSI strategy using talipp's streaming indicator. Demonstrates the
    tick-by-tick talipp integration pattern — no DataFrame or numpy needed."""

    def __init__(self, name: str, timeframe, max_candles: int = 1000) -> None:
        super().__init__(name, timeframe, max_candles)
        self.rsi: RSI = RSI(period=14)

    def process_new_candle(self) -> dict | None:
        self.rsi.add(self.candles.close())

        if self.rsi[-1] is None:
            return None

        if self.rsi[-1] < 30:
            position = Position(
                entry_price=self.candles.close(),
                quantity=1,
                stop_loss=self.candles.close() * 0.95,
                take_profit=self.candles.close() * 1.05,
                entry_time=self.candles.open_time(),
            )
            return position.to_dict()

        return None
