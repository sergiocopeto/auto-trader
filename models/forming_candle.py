from datetime import timedelta
from models.timeframe import Timeframe, timedelta_mapping
from models.candles import Candle

class FormingCandle:
    def __init__(self, timeframe=Timeframe.HOUR_1):
        self.open_time = None
        self.open_price = None
        self.high_price = None
        self.low_price = None
        self.close_price = None
        self.volume = None
        self.timeframe = timeframe

    def is_new_timeframe_candle(self, open_time):
        time_delta: timedelta = open_time - self.open_time
        if time_delta.total_seconds() >= timedelta_mapping[self.timeframe].total_seconds():
            return True
        return False

    

    def update(self, open_time, open_price, high_price, low_price, close_price, volume):
        # check if it's a new timeframe candle or an update to the existing one 
        if self.open_time != None and self.is_new_timeframe_candle(open_time):
            to_return = Candle(
                open_time=self.open_time,
                open_price=self.open_price,
                high_price=self.high_price,
                low_price=self.low_price,
                close_price=self.close_price,
                volume=self.volume,
            )
            # new candle, reset values
            self.open_time = open_time
            self.open_price = open_price
            self.high_price = high_price
            self.low_price = low_price
            self.close_price = close_price
            self.volume = volume
            return to_return
        else:
            self.open_time = open_time if self.open_time is None else self.open_time
            self.high_price = high_price if self.high_price is None else max(self.high_price, high_price)
            self.low_price = low_price if self.low_price is None else min(self.low_price, low_price)
            self.close_price = close_price
            self.volume = volume if self.volume is None else self.volume + volume
            return None