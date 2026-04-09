"""
Backtest Engine
Historical strategy testing with realistic simulation
"""

import pandas as pd
from typing import Dict, List
from datetime import datetime
from strategies.base_strategy import BaseStrategy
from backtesting.performance_metrics import PerformanceMetrics
from utils.logger import logger

class BacktestEngine:
    """
    Backtesting Features:
    - Realistic order execution (slippage, fees)
    - Position tracking
    - Risk management integration
    - Multiple timeframe support
    - Walk-forward optimization ready
    """

    def __init__(
        self,
        strategy: BaseStrategy,
        initial_capital: float = 10000,
        commission: float = 0.001,
        slippage: float = 0.0005
    ):
        self.strategy = strategy
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage

        self.capital = initial_capital
        self.trades: List[Dict] = []
        self.open_position = None
        self.equity_curve = []

    def run(self, df: pd.DataFrame, symbol: str = "BTC/USDT") -> Dict:
        """Run backtest on historical data"""
        logger.info(f"Starting backtest: {self.strategy.name} on {symbol}")
        logger.info(f"Data range: {df.index[0]} to {df.index[-1]} ({len(df)} candles)")

        self.trades = []
        self.open_position = None
        self.capital = self.initial_capital
        self.equity_curve = []

        for i in range(100, len(df)):
            current_slice = df.iloc[:i+1]
            current_bar = df.iloc[i]
            current_price = current_bar['close']
            timestamp = df.index[i]

            self.equity_curve.append({
                'timestamp': timestamp,
                'equity': self.capital
            })

            if self.open_position:
                should_exit, exit_reason = self.strategy.should_exit(current_slice, self.open_position)

                if should_exit:
                    self._close_position(current_price, timestamp, exit_reason)

            else:
                signal = self.strategy.generate_signal(current_slice)

                if signal and self.strategy.validate_signal(signal, current_slice):
                    self._open_position(signal, current_price, timestamp, symbol, current_slice)

        if self.open_position:
            final_price = df.iloc[-1]['close']
            final_timestamp = df.index[-1]
            self._close_position(final_price, final_timestamp, "backtest_end")

        metrics = PerformanceMetrics.calculate_metrics(self.trades, self.initial_capital)

        logger.info(f"Backtest complete: {metrics['total_trades']} trades, "
                   f"{metrics['win_rate']:.2f}% win rate, "
                   f"{metrics['total_return']:.2f}% return")

        return {
            'strategy_name': self.strategy.name,
            'parameters': self.strategy.get_parameters(),
            'start_date': df.index[0],
            'end_date': df.index[-1],
            'initial_capital': self.initial_capital,
            'final_capital': metrics['final_capital'],
            'metrics': metrics,
            'trades': self.trades,
            'equity_curve': self.equity_curve
        }

    def _open_position(self, signal, price: float, timestamp, symbol: str, df: pd.DataFrame):
        """Open new position"""
        execution_price = self._apply_slippage(price, signal.type.value)

        risk_amount = self.capital * 0.02
        price_risk = abs(execution_price - signal.stop_loss)
        quantity = risk_amount / price_risk if price_risk > 0 else 0

        if quantity <= 0:
            return

        position_value = quantity * execution_price
        max_position = self.capital * 0.3

        if position_value > max_position:
            quantity = max_position / execution_price

        commission_cost = position_value * self.commission

        if position_value > self.capital:
            logger.warning("Insufficient capital for trade")
            return

        self.open_position = {
            'symbol': symbol,
            'side': 'long' if signal.type.value == 'buy' else 'short',
            'entry_price': execution_price,
            'quantity': quantity,
            'entry_time': timestamp,
            'stop_loss': signal.stop_loss,
            'take_profit': signal.take_profit,
            'commission': commission_cost,
            'metadata': signal.metadata
        }

        logger.debug(f"Position opened: {signal.type.value} {quantity:.4f} @ {execution_price:.2f}")

    def _close_position(self, price: float, timestamp, reason: str):
        """Close open position"""
        if not self.open_position:
            return

        execution_price = self._apply_slippage(price, 'sell' if self.open_position['side'] == 'long' else 'buy')

        if self.open_position['side'] == 'long':
            pnl = (execution_price - self.open_position['entry_price']) * self.open_position['quantity']
        else:
            pnl = (self.open_position['entry_price'] - execution_price) * self.open_position['quantity']

        position_value = self.open_position['quantity'] * execution_price
        close_commission = position_value * self.commission
        total_commission = self.open_position['commission'] + close_commission

        net_pnl = pnl - total_commission
        self.capital += net_pnl

        pnl_percent = (net_pnl / (self.open_position['entry_price'] * self.open_position['quantity'])) * 100

        trade_record = {
            'symbol': self.open_position['symbol'],
            'side': self.open_position['side'],
            'entry_price': self.open_position['entry_price'],
            'exit_price': execution_price,
            'quantity': self.open_position['quantity'],
            'entry_time': self.open_position['entry_time'],
            'exit_time': timestamp,
            'pnl': net_pnl,
            'pnl_percent': pnl_percent,
            'fees': total_commission,
            'exit_reason': reason,
            'metadata': self.open_position['metadata']
        }

        self.trades.append(trade_record)

        logger.debug(f"Position closed: {reason} | PnL: ${net_pnl:.2f} ({pnl_percent:.2f}%)")

        self.open_position = None

    def _apply_slippage(self, price: float, side: str) -> float:
        """Apply slippage to execution price"""
        if side == 'buy':
            return price * (1 + self.slippage)
        else:
            return price * (1 - self.slippage)

    def get_trade_log(self) -> pd.DataFrame:
        """Get trade log as DataFrame"""
        if not self.trades:
            return pd.DataFrame()

        df = pd.DataFrame(self.trades)
        df['entry_time'] = pd.to_datetime(df['entry_time'])
        df['exit_time'] = pd.to_datetime(df['exit_time'])
        return df

    def get_equity_curve(self) -> pd.DataFrame:
        """Get equity curve as DataFrame"""
        if not self.equity_curve:
            return pd.DataFrame()

        df = pd.DataFrame(self.equity_curve)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df

    def optimize_parameters(self, df: pd.DataFrame, param_grid: Dict) -> List[Dict]:
        """Grid search optimization"""
        results = []

        param_combinations = self._generate_param_combinations(param_grid)

        logger.info(f"Testing {len(param_combinations)} parameter combinations")

        for params in param_combinations:
            self.strategy.update_parameters(params)

            result = self.run(df)

            results.append({
                'parameters': params.copy(),
                'sharpe_ratio': result['metrics']['sharpe_ratio'],
                'total_return': result['metrics']['total_return'],
                'win_rate': result['metrics']['win_rate'],
                'max_drawdown': result['metrics']['max_drawdown_pct'],
                'profit_factor': result['metrics']['profit_factor'],
                'total_trades': result['metrics']['total_trades']
            })

        results.sort(key=lambda x: x['sharpe_ratio'], reverse=True)

        logger.info(f"Optimization complete. Best Sharpe: {results[0]['sharpe_ratio']:.2f}")

        return results

    def _generate_param_combinations(self, param_grid: Dict) -> List[Dict]:
        """Generate all parameter combinations"""
        keys = list(param_grid.keys())
        values = list(param_grid.values())

        combinations = []

        def recurse(index, current):
            if index == len(keys):
                combinations.append(current.copy())
                return

            for value in values[index]:
                current[keys[index]] = value
                recurse(index + 1, current)

        recurse(0, {})
        return combinations
