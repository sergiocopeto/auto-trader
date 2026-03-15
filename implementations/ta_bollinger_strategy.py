from ta.volatility import BollingerBands
from strategies.strategy import Strategy
from models.position import Position


class TABollingerStrategy(Strategy):
    def __init__(self, name: str, timeframe, max_candles: int = 1000) -> None:
        super().__init__(name=name, timeframe=timeframe, max_candles=max_candles)

    def process_new_candle(self) -> dict | None:
        df = self.candles.to_dataframe()
        if len(df) < 20:
            return None

        bb = BollingerBands(close=df["close"], window=20, window_dev=2)
        latest_close = df["close"].iloc[-1]
        lower_band = bb.bollinger_lband().iloc[-1]

        if latest_close < lower_band:
            position = Position(
                entry_price=latest_close,
                quantity=1,
                stop_loss=latest_close * 0.95,
                take_profit=latest_close * 1.05,
                entry_time=self.candles.open_time(),
            )
            return position.to_dict()

        return None
