import uuid

class Position:
    def __init__(self, entry_price, quantity, stop_loss = None, take_profit = None, entry_time = None):
        self.id = uuid.uuid4()
        self.entry_price = entry_price
        self.quantity = quantity
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.entry_time = entry_time
        self.is_open = True
        self.exit_time = None
        self.exit_price = None
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "entry_price": self.entry_price,
            "quantity": self.quantity,
            "stop_loss": self.stop_loss,
            "take_profit": self.take_profit,
            "is_open": self.is_open,
            "entry_time": self.entry_time,
            "exit_time": self.exit_time,
            "exit_price": self.exit_price,
        }
    