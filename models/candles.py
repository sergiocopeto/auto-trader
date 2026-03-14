from collections import deque

class Candle:
    def __init__(self, open_time, open_price, high_price, low_price, close_price, volume):
        self.open_time = open_time
        self.open_price = open_price
        self.high_price = high_price
        self.low_price = low_price
        self.close_price = close_price
        self.volume = volume
    
    def to_dict(self):
        return {
            "open_time": self.open_time,
            "open": self.open_price,
            "high": self.high_price,
            "low": self.low_price,
            "close": self.close_price,
            "volume": self.volume,
        }

class Candles:
    def __init__(self, candles = None, max_candles=1000):
        self.candles = deque()
        if candles is not None:
            for c in candles:
                self.candles.append(c)
        self.max_candles = max_candles

    def add_candle(self, candle):
        if len(self.candles) == self.max_candles:
            self.candles.popleft()
        self.candles.append(candle)
    
    def open_price(self):
        return self.candles[-1].open_price if len(self.candles) > 0 else None
    def open_time(self):
        return self.candles[-1].open_time if len(self.candles) > 0 else None
    def close(self):
        return self.candles[-1].close_price if len(self.candles) > 0 else None
    def high(self):
        return self.candles[-1].high_price if len(self.candles) > 0 else None
    def low(self):
        return self.candles[-1].low_price if len(self.candles) > 0 else None
    def volume(self):
        return self.candles[-1].volume if len(self.candles) > 0 else None
    
    def opens(self):
        return [c.open_price for c in self.candles]
    def closes(self):
        return [c.close_price for c in self.candles]
    def highs(self):
        return [c.high_price for c in self.candles]
    def lows(self):
        return [c.low_price for c in self.candles]
    def volumes(self):
        return [c.volume for c in self.candles] 
    
