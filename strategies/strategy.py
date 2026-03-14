from models.forming_candle import FormingCandle
from models.candles import Candle, Candles

class Strategy:
    def __init__(self, name, timeframe, max_candles=1000):
        self.name = name
        self.timeframe = timeframe
        self.max_candles = max_candles
        self.forming_candle = FormingCandle(timeframe=self.timeframe)
        self.candles = Candles(max_candles=self.max_candles)
        self.positions = []
    
    def process_new_candle(self):
        raise NotImplementedError("Subclasses must implement process_new_candle()")
    
    def update_positions(self):
        # This is where you would update the status of open positions based on the latest candle data
        return {}

    def update(self, new_candle_data):
        formed_candle = self.forming_candle.update(
            open_time=new_candle_data["open_time"],
            open_price=new_candle_data["open"],
            high_price=new_candle_data["high"],
            low_price=new_candle_data["low"],
            close_price=new_candle_data["close"],
            volume=new_candle_data["volume"],
        )
        if formed_candle is not None:
            self.candles.add_candle(formed_candle)
            return self.process_new_candle()
        else:
            return self.update_positions()