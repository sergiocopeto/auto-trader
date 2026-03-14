from strategies.strategy import Strategy
from models.position import Position


class ExampleStrategy(Strategy):
    def process_new_candle(self):
        position = Position(
            entry_price=self.candles.close(),
            quantity=1,
            stop_loss=self.candles.close() * 0.95,
            take_profit=self.candles.close() * 1.05,
            entry_time=self.candles.open_time(),
        )
        return position.to_dict()
