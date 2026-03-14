from strategies.strategy import Strategy

class StrategyManager:
    def __init__(self):
        self.strategies: list[Strategy] = []
    
    def add_strategy(self, strategy: Strategy):
        self.strategies.append(strategy)
    
    def remove_strategy(self, strategy: Strategy):
        self.strategies.remove(strategy)
    
    def update(self, candle):
        update_dict = {}
        for strategy in self.strategies:
            new_orders = strategy.update(candle)
            if new_orders:
                update_dict[strategy.name] = new_orders
        return update_dict