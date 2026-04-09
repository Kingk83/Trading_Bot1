"""
Run Backtest Example
Comprehensive backtesting with optimization
"""

import asyncio
import sys
import os
import pandas as pd
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from strategies.trend_following import TrendFollowingStrategy
from strategies.mean_reversion import MeanReversionStrategy
from strategies.breakout import BreakoutStrategy
from backtesting.backtest_engine import BacktestEngine
from optimization.optimizer import StrategyOptimizer
from data.data_fetcher import DataFetcher
from config import Config

async def run_comprehensive_backtest():
    """Run comprehensive backtest with optimization"""
    print("=" * 70)
    print("AlgoTrader Pro - Comprehensive Backtest")
    print("=" * 70)

    symbol = 'BTC/USDT'
    timeframe = '1h'
    start_date = '2024-01-01'
    end_date = '2024-12-31'

    print(f"\nFetching data for {symbol} ({timeframe})...")
    data_fetcher = DataFetcher()
    from datetime import datetime as dt
    df = await data_fetcher.fetch_historical_data(symbol, timeframe, dt.fromisoformat(start_date), dt.fromisoformat(end_date))

    if df is None or len(df) < 100:
        print("Error: Insufficient data for backtest")
        return

    print(f"Data loaded: {len(df)} candles from {df.index[0]} to {df.index[-1]}")

    strategies = [
        ('Trend Following', TrendFollowingStrategy()),
        ('Mean Reversion', MeanReversionStrategy()),
        ('Breakout', BreakoutStrategy())
    ]

    results = []

    for name, strategy in strategies:
        print(f"\n{'='*70}")
        print(f"Testing: {name}")
        print('='*70)

        backtest = BacktestEngine(
            strategy=strategy,
            initial_capital=Config.INITIAL_CAPITAL,
            commission=Config.COMMISSION,
            slippage=Config.SLIPPAGE
        )

        result = backtest.run(df, symbol)
        metrics = result['metrics']

        print(f"\n📊 Performance Summary:")
        print(f"   Total Trades:    {metrics['total_trades']}")
        print(f"   Win Rate:        {metrics['win_rate']:.2f}%")
        print(f"   Total Return:    {metrics['total_return']:.2f}%")
        print(f"   Sharpe Ratio:    {metrics['sharpe_ratio']:.2f}")
        print(f"   Sortino Ratio:   {metrics['sortino_ratio']:.2f}")
        print(f"   Max Drawdown:    {metrics['max_drawdown_pct']:.2f}%")
        print(f"   Profit Factor:   {metrics['profit_factor']:.2f}")
        print(f"   Average Win:     ${metrics['avg_win']:.2f}")
        print(f"   Average Loss:    ${metrics['avg_loss']:.2f}")
        print(f"   Expectancy:      ${metrics['expectancy']:.2f}")

        results.append({
            'strategy': name,
            'metrics': metrics,
            'result': result
        })

        if metrics['total_trades'] > 0:
            print(f"\n🎯 Best Trade:    ${metrics['largest_win']:.2f}")
            print(f"   Worst Trade:   ${metrics['largest_loss']:.2f}")

    print(f"\n{'='*70}")
    print("Strategy Comparison")
    print('='*70)
    print(f"{'Strategy':<20} {'Return':<12} {'Sharpe':<10} {'Win Rate':<12} {'Trades':<10}")
    print('-'*70)

    for r in results:
        m = r['metrics']
        print(f"{r['strategy']:<20} {m['total_return']:>10.2f}% {m['sharpe_ratio']:>9.2f} {m['win_rate']:>10.2f}% {m['total_trades']:>9}")

    best_strategy = max(results, key=lambda x: x['metrics']['sharpe_ratio'])
    print(f"\n🏆 Best Strategy (by Sharpe): {best_strategy['strategy']}")

    print(f"\n{'='*70}")
    print("Optimization (Grid Search)")
    print('='*70)

    optimizer = StrategyOptimizer(TrendFollowingStrategy(), Config.INITIAL_CAPITAL)

    param_grid = {
        'fast_ema': [10, 12, 15],
        'slow_ema': [20, 26, 30],
        'atr_multiplier': [1.5, 2.0, 2.5]
    }

    print("\nTesting parameter combinations...")
    optimization_results = optimizer.grid_search(df, param_grid)

    print(f"\nTop 3 Parameter Sets:")
    for i, res in enumerate(optimization_results[:3], 1):
        print(f"\n{i}. Sharpe: {res['sharpe_ratio']:.2f} | Return: {res['total_return']:.2f}%")
        print(f"   Parameters: {res['parameters']}")

    print(f"\n{'='*70}")
    print("Walk-Forward Analysis")
    print('='*70)

    wf_results = optimizer.walk_forward_analysis(
        df,
        param_grid,
        train_size=180,
        test_size=30,
        anchored=False
    )

    print(f"\nWalk-Forward Results:")
    print(f"   Total Return:     {wf_results['total_return']:.2f}%")
    print(f"   Average Return:   {wf_results['avg_return']:.2f}%")
    print(f"   Std Deviation:    {wf_results['std_return']:.2f}%")
    print(f"   Avg Win Rate:     {wf_results['win_rate']:.2f}%")
    print(f"   Avg Sharpe:       {wf_results['avg_sharpe']:.2f}")

    print(f"\n{'='*70}")
    print("Backtest Complete!")
    print('='*70)
    print("\nNext Steps:")
    print("1. Review results and adjust parameters if needed")
    print("2. Run paper trading: python trading_bot/main.py")
    print("3. Monitor performance on dashboard")

if __name__ == "__main__":
    asyncio.run(run_comprehensive_backtest())
