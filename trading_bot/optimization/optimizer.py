"""
Strategy Optimizer
Parameter optimization with walk-forward testing
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
from ..backtesting.backtest_engine import BacktestEngine
from ..strategies.base_strategy import BaseStrategy
from ..utils.logger import logger

class StrategyOptimizer:
    """
    Optimization Methods:
    1. Grid Search - Test all parameter combinations
    2. Walk-Forward Analysis - Out-of-sample validation
    3. Monte Carlo Simulation - Robustness testing
    """

    def __init__(self, strategy: BaseStrategy, initial_capital: float = 10000):
        self.strategy = strategy
        self.initial_capital = initial_capital

    def grid_search(self, df: pd.DataFrame, param_grid: Dict) -> List[Dict]:
        """Perform grid search optimization"""
        logger.info(f"Starting grid search optimization for {self.strategy.name}")
        logger.info(f"Parameter grid: {param_grid}")

        backtest = BacktestEngine(self.strategy, self.initial_capital)
        results = backtest.optimize_parameters(df, param_grid)

        top_10 = results[:10]
        logger.info(f"\nTop 10 Parameter Sets:")
        for i, result in enumerate(top_10, 1):
            logger.info(f"{i}. Sharpe: {result['sharpe_ratio']:.2f}, "
                       f"Return: {result['total_return']:.2f}%, "
                       f"Win Rate: {result['win_rate']:.2f}%")
            logger.info(f"   Parameters: {result['parameters']}")

        return results

    def walk_forward_analysis(
        self,
        df: pd.DataFrame,
        param_grid: Dict,
        train_size: int = 252,
        test_size: int = 63,
        anchored: bool = False
    ) -> Dict:
        """
        Walk-forward optimization

        Args:
            df: Historical data
            param_grid: Parameters to optimize
            train_size: Training period length (trading days)
            test_size: Testing period length (trading days)
            anchored: If True, always start from beginning; if False, rolling window
        """
        logger.info(f"Starting walk-forward analysis")
        logger.info(f"Train size: {train_size} days, Test size: {test_size} days")
        logger.info(f"Anchored: {anchored}")

        results = []
        total_return = 1.0
        all_trades = []

        start_idx = train_size
        end_idx = len(df)

        while start_idx + test_size <= end_idx:
            if anchored:
                train_start = 0
            else:
                train_start = start_idx - train_size

            train_end = start_idx
            test_start = start_idx
            test_end = start_idx + test_size

            train_data = df.iloc[train_start:train_end]
            test_data = df.iloc[test_start:test_end]

            logger.info(f"\nOptimizing on: {train_data.index[0]} to {train_data.index[-1]}")

            backtest = BacktestEngine(self.strategy, self.initial_capital)
            optimization_results = backtest.optimize_parameters(train_data, param_grid)

            best_params = optimization_results[0]['parameters']
            logger.info(f"Best parameters: {best_params}")

            self.strategy.update_parameters(best_params)

            logger.info(f"Testing on: {test_data.index[0]} to {test_data.index[-1]}")
            test_backtest = BacktestEngine(self.strategy, self.initial_capital)
            test_result = test_backtest.run(test_data)

            period_return = (test_result['metrics']['final_capital'] / self.initial_capital) - 1
            total_return *= (1 + period_return)

            results.append({
                'train_start': train_data.index[0],
                'train_end': train_data.index[-1],
                'test_start': test_data.index[0],
                'test_end': test_data.index[-1],
                'best_params': best_params,
                'test_return': period_return * 100,
                'test_trades': test_result['metrics']['total_trades'],
                'test_win_rate': test_result['metrics']['win_rate'],
                'test_sharpe': test_result['metrics']['sharpe_ratio']
            })

            all_trades.extend(test_result['trades'])

            start_idx += test_size

        total_return_pct = (total_return - 1) * 100

        logger.info(f"\n=== Walk-Forward Analysis Complete ===")
        logger.info(f"Total Periods: {len(results)}")
        logger.info(f"Total Return: {total_return_pct:.2f}%")
        logger.info(f"Average Period Return: {np.mean([r['test_return'] for r in results]):.2f}%")

        return {
            'periods': results,
            'total_return': total_return_pct,
            'avg_return': np.mean([r['test_return'] for r in results]),
            'std_return': np.std([r['test_return'] for r in results]),
            'all_trades': all_trades,
            'win_rate': np.mean([r['test_win_rate'] for r in results]),
            'avg_sharpe': np.mean([r['test_sharpe'] for r in results])
        }

    def monte_carlo_simulation(
        self,
        trades: List[Dict],
        n_simulations: int = 1000,
        n_trades: int = None
    ) -> Dict:
        """
        Monte Carlo simulation for robustness testing
        Randomly resample trades to test consistency
        """
        logger.info(f"Running Monte Carlo simulation ({n_simulations} iterations)")

        if not trades:
            return {}

        if n_trades is None:
            n_trades = len(trades)

        pnl_values = [t['pnl'] for t in trades]

        simulation_results = []

        for i in range(n_simulations):
            sampled_pnl = np.random.choice(pnl_values, size=n_trades, replace=True)

            cumulative_pnl = np.cumsum(sampled_pnl)
            final_pnl = cumulative_pnl[-1]

            running_max = np.maximum.accumulate(cumulative_pnl)
            drawdowns = cumulative_pnl - running_max
            max_drawdown = np.min(drawdowns)

            simulation_results.append({
                'final_pnl': final_pnl,
                'max_drawdown': max_drawdown
            })

        final_pnls = [r['final_pnl'] for r in simulation_results]
        max_drawdowns = [r['max_drawdown'] for r in simulation_results]

        percentile_5 = np.percentile(final_pnls, 5)
        percentile_50 = np.percentile(final_pnls, 50)
        percentile_95 = np.percentile(final_pnls, 95)

        prob_profit = sum(1 for pnl in final_pnls if pnl > 0) / n_simulations

        logger.info(f"\n=== Monte Carlo Results ===")
        logger.info(f"5th Percentile PnL: ${percentile_5:.2f}")
        logger.info(f"50th Percentile PnL: ${percentile_50:.2f}")
        logger.info(f"95th Percentile PnL: ${percentile_95:.2f}")
        logger.info(f"Probability of Profit: {prob_profit*100:.2f}%")

        return {
            'simulations': n_simulations,
            'final_pnl_5th': percentile_5,
            'final_pnl_50th': percentile_50,
            'final_pnl_95th': percentile_95,
            'max_drawdown_5th': np.percentile(max_drawdowns, 5),
            'max_drawdown_50th': np.percentile(max_drawdowns, 50),
            'max_drawdown_95th': np.percentile(max_drawdowns, 95),
            'probability_of_profit': prob_profit,
            'all_results': simulation_results
        }

    def calculate_stability_score(self, results: List[Dict]) -> float:
        """Calculate strategy stability score"""
        if not results:
            return 0.0

        returns = [r.get('total_return', 0) for r in results]
        sharpe_ratios = [r.get('sharpe_ratio', 0) for r in results]
        win_rates = [r.get('win_rate', 0) for r in results]

        return_consistency = 1 - (np.std(returns) / np.mean(returns)) if np.mean(returns) != 0 else 0
        sharpe_consistency = 1 - (np.std(sharpe_ratios) / np.mean(sharpe_ratios)) if np.mean(sharpe_ratios) != 0 else 0
        win_rate_consistency = 1 - (np.std(win_rates) / np.mean(win_rates)) if np.mean(win_rates) != 0 else 0

        stability = (return_consistency * 0.4 + sharpe_consistency * 0.3 + win_rate_consistency * 0.3)

        return max(0, min(stability, 1))
