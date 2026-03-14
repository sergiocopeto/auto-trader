import math
import statistics


class MetricsEngine:
    @classmethod
    def compute(cls, closed_positions: list, starting_capital: float) -> dict:
        total_trades = len(closed_positions)
        if total_trades == 0:
            return {
                "total_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "win_rate": 0,
                "total_pnl": 0,
                "total_pnl_pct": 0,
                "avg_win": 0,
                "avg_loss": 0,
                "profit_factor": 0,
                "max_drawdown": 0,
                "sharpe_ratio": 0,
            }

        pnls = [p.pnl for p in closed_positions]
        winners = [p for p in closed_positions if p.pnl > 0]
        losers = [p for p in closed_positions if p.pnl <= 0]

        winning_trades = len(winners)
        losing_trades = len(losers)
        win_rate = winning_trades / total_trades * 100
        total_pnl = sum(pnls)
        total_pnl_pct = total_pnl / starting_capital * 100
        avg_win = statistics.mean([p.pnl for p in winners]) if winners else 0.0
        avg_loss = statistics.mean([p.pnl for p in losers]) if losers else 0.0
        gross_profit = sum(p.pnl for p in winners)
        gross_loss = abs(sum(p.pnl for p in losers))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float("inf")

        # Max drawdown via equity curve sorted by exit_time
        sorted_positions = sorted(closed_positions, key=lambda p: p.exit_time)
        equity = starting_capital
        peak = starting_capital
        max_drawdown = 0.0
        for p in sorted_positions:
            equity += p.pnl
            peak = max(peak, equity)
            dd = (peak - equity) / peak * 100
            max_drawdown = max(max_drawdown, dd)

        # Sharpe ratio (annualised, per-trade returns)
        returns = [p.pnl / starting_capital for p in closed_positions]
        if len(returns) < 2:
            sharpe = 0.0
        else:
            try:
                sharpe = statistics.mean(returns) / statistics.stdev(returns) * math.sqrt(252)
            except statistics.StatisticsError:
                sharpe = 0.0

        return {
            "total_trades": total_trades,
            "winning_trades": winning_trades,
            "losing_trades": losing_trades,
            "win_rate": win_rate,
            "total_pnl": total_pnl,
            "total_pnl_pct": total_pnl_pct,
            "avg_win": avg_win,
            "avg_loss": avg_loss,
            "profit_factor": profit_factor,
            "max_drawdown": max_drawdown,
            "sharpe_ratio": sharpe,
        }
