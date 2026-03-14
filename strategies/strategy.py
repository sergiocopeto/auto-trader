from models.forming_candle import FormingCandle
from models.candles import Candle, Candles
from models.position import Position

class Strategy:
    def __init__(self, name, timeframe, max_candles=1000):
        self.name = name
        self.timeframe = timeframe
        self.max_candles = max_candles
        self.forming_candle = FormingCandle(timeframe=self.timeframe)
        self.candles = Candles(max_candles=self.max_candles)
        self.positions = []
    
    def process_new_candle(self):
        # This is where the strategy logic will go. For example:
        # - Check if certain indicators are met
        # - Open new positions
        # - Close existing positions
        position = Position(
            entry_price=self.candles.close(),
            quantity=1,  # example quantity
            stop_loss=self.candles.close() * 0.95,  # example stop loss at 5% below entry
            take_profit=self.candles.close() * 1.05,  # example take profit at 5% above entry
            entry_time = self.candles.open_time()
        )
        #self.positions.append(position)
        return position.to_dict()   
    
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