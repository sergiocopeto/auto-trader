from models.position import Position


class VirtualBroker:
    def __init__(self, starting_capital: float) -> None:
        self.starting_capital = starting_capital
        self.current_capital = starting_capital
        self._open_positions: list = []
        self._closed_positions: list = []
        self._pending_signals: list = []

    def submit_signal(self, signal: dict, strategy_name: str) -> None:
        if signal is None or not isinstance(signal, dict):
            return
        if signal.get("action") not in {"open", "close", "close_all"}:
            return
        signal = {**signal, "strategy_name": strategy_name}
        self._pending_signals.append(signal)

    def close_position(self, position: Position, exit_price: float, exit_time, reason: str) -> None:
        position.exit_price = exit_price
        position.exit_time = exit_time
        position.exit_reason = reason
        position.is_open = False

        if position.side == "short":
            pnl = (position.entry_price - exit_price) * position.quantity
        else:
            pnl = (exit_price - position.entry_price) * position.quantity

        position.pnl = pnl
        self.current_capital += pnl
        self._open_positions.remove(position)
        self._closed_positions.append(position)

    def fill_pending(self, open_price: float, open_time) -> None:
        signals = list(self._pending_signals)
        self._pending_signals.clear()

        for signal in signals:
            action = signal.get("action")

            if action == "open":
                side = signal.get("side")
                quantity = signal.get("quantity")
                stop_loss = signal.get("stop_loss")
                take_profit = signal.get("take_profit")
                strategy_name = signal.get("strategy_name")

                if open_price * quantity > self.current_capital:
                    continue

                position = Position(
                    entry_price=open_price,
                    quantity=quantity,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    entry_time=open_time,
                )
                position.side = side
                position.strategy_name = strategy_name
                self.current_capital -= open_price * quantity
                self._open_positions.append(position)

            elif action == "close":
                position_id = signal.get("position_id")
                for pos in self._open_positions:
                    if str(pos.id) == position_id:
                        self.close_position(pos, open_price, open_time, "close")
                        break

            elif action == "close_all":
                self.close_all(open_price, open_time)

    def check_sl_tp(self, candle: dict) -> None:
        candle_high = candle["high"]
        candle_low = candle["low"]
        candle_time = candle["open_time"]

        for position in list(self._open_positions):
            if position.side == "short":
                sl_hit = position.stop_loss is not None and candle_high >= position.stop_loss
                tp_hit = position.take_profit is not None and candle_low <= position.take_profit
            else:
                sl_hit = position.stop_loss is not None and candle_low <= position.stop_loss
                tp_hit = position.take_profit is not None and candle_high >= position.take_profit

            if sl_hit:
                self.close_position(position, position.stop_loss, candle_time, "sl")
            elif tp_hit:
                self.close_position(position, position.take_profit, candle_time, "tp")

    def close_all(self, exit_price: float, exit_time) -> None:
        for position in list(self._open_positions):
            self.close_position(position, exit_price, exit_time, "close_all")

    @property
    def open_positions(self) -> list:
        return self._open_positions

    @property
    def closed_positions(self) -> list:
        return self._closed_positions

    @property
    def equity(self) -> float:
        """Returns current capital. Exact only after close_all since no live price feed is available."""
        return self.current_capital
