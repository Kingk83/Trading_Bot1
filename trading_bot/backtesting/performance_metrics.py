"""
Performance Metrics
Calculate trading performance statistics
"""

import pandas as pd
import numpy as np
from typing import List, Dict
from datetime import datetime

class PerformanceMetrics:
    @staticmethod
    def calculate_metrics(trades: List[Dict], initial_capital: float) -> Dict:
        """Calculate comprehensive performance metrics"""
        if not trades:
            return PerformanceMetrics._empty_metrics()

        df = pd.DataFrame(trades)

        total_trades = len(df)
        winning_trades = len(df[df['pnl'] > 0])
        losing_trades = len(df[df['pnl'] < 0])
        win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0

        total_pnl = df['pnl'].sum()
        total_fees = df.get('fees', pd.Series([0])).sum()
        net_pnl = total_pnl - total_fees

        avg_win = df[df['pnl'] > 0]['pnl'].mean() if winning_trades > 0 else 0
        avg_loss = df[df['pnl'] < 0]['pnl'].mean() if losing_trades > 0 else 0
        largest_win = df['pnl'].max()
        largest_loss = df['pnl'].min()

        gross_profit = df[df['pnl'] > 0]['pnl'].sum()
        gross_loss = abs(df[df['pnl'] < 0]['pnl'].sum())
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')

        df['cumulative_pnl'] = df['pnl'].cumsum()
        df['equity'] = initial_capital + df['cumulative_pnl']

        sharpe_ratio = PerformanceMetrics._calculate_sharpe_ratio(df['pnl'])
        sortino_ratio = PerformanceMetrics._calculate_sortino_ratio(df['pnl'])

        max_drawdown, max_drawdown_pct = PerformanceMetrics._calculate_max_drawdown(df['equity'])

        total_return = (net_pnl / initial_capital) * 100

        if 'entry_time' in df.columns and 'exit_time' in df.columns:
            df['entry_time'] = pd.to_datetime(df['entry_time'])
            df['exit_time'] = pd.to_datetime(df['exit_time'])
            df['hold_time'] = (df['exit_time'] - df['entry_time']).dt.total_seconds() / 3600
            avg_hold_time = df['hold_time'].mean()
        else:
            avg_hold_time = 0

        expectancy = (win_rate/100 * avg_win) - ((100-win_rate)/100 * abs(avg_loss))

        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': round(win_rate, 2),
            'total_pnl': round(total_pnl, 2),
            'net_pnl': round(net_pnl, 2),
            'total_fees': round(total_fees, 2),
            'total_return': round(total_return, 2),
            'avg_win': round(avg_win, 2),
            'avg_loss': round(avg_loss, 2),
            'largest_win': round(largest_win, 2),
            'largest_loss': round(largest_loss, 2),
            'profit_factor': round(profit_factor, 2),
            'sharpe_ratio': round(sharpe_ratio, 2),
            'sortino_ratio': round(sortino_ratio, 2),
            'max_drawdown': round(max_drawdown, 2),
            'max_drawdown_pct': round(max_drawdown_pct, 2),
            'avg_hold_time_hours': round(avg_hold_time, 2),
            'expectancy': round(expectancy, 2),
            'final_capital': round(initial_capital + net_pnl, 2)
        }

    @staticmethod
    def _calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.0) -> float:
        """Calculate Sharpe Ratio"""
        if len(returns) == 0 or returns.std() == 0:
            return 0.0

        excess_returns = returns - risk_free_rate
        sharpe = excess_returns.mean() / returns.std()

        return sharpe * np.sqrt(252)

    @staticmethod
    def _calculate_sortino_ratio(returns: pd.Series, risk_free_rate: float = 0.0) -> float:
        """Calculate Sortino Ratio"""
        if len(returns) == 0:
            return 0.0

        excess_returns = returns - risk_free_rate
        downside_returns = returns[returns < 0]

        if len(downside_returns) == 0 or downside_returns.std() == 0:
            return 0.0

        sortino = excess_returns.mean() / downside_returns.std()

        return sortino * np.sqrt(252)

    @staticmethod
    def _calculate_max_drawdown(equity: pd.Series) -> tuple:
        """Calculate Maximum Drawdown"""
        if len(equity) == 0:
            return 0.0, 0.0

        running_max = equity.expanding().max()
        drawdown = equity - running_max
        max_drawdown = drawdown.min()
        max_drawdown_pct = (max_drawdown / running_max[drawdown.idxmin()]) * 100

        return abs(max_drawdown), abs(max_drawdown_pct)

    @staticmethod
    def _empty_metrics() -> Dict:
        """Return empty metrics structure"""
        return {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'win_rate': 0,
            'total_pnl': 0,
            'net_pnl': 0,
            'total_fees': 0,
            'total_return': 0,
            'avg_win': 0,
            'avg_loss': 0,
            'largest_win': 0,
            'largest_loss': 0,
            'profit_factor': 0,
            'sharpe_ratio': 0,
            'sortino_ratio': 0,
            'max_drawdown': 0,
            'max_drawdown_pct': 0,
            'avg_hold_time_hours': 0,
            'expectancy': 0,
            'final_capital': 0
        }

    @staticmethod
    def calculate_monthly_returns(trades: List[Dict], initial_capital: float) -> pd.DataFrame:
        """Calculate monthly returns"""
        if not trades:
            return pd.DataFrame()

        df = pd.DataFrame(trades)
        df['exit_time'] = pd.to_datetime(df['exit_time'])
        df['month'] = df['exit_time'].dt.to_period('M')

        monthly = df.groupby('month').agg({
            'pnl': 'sum',
        }).reset_index()

        monthly['return_pct'] = (monthly['pnl'] / initial_capital) * 100
        monthly['month'] = monthly['month'].astype(str)

        return monthly
