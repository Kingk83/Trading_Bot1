"""
Initialize Strategies in Database
Creates default strategy configurations
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.database import db

async def initialize_strategies():
    """Initialize default strategies in database"""
    strategies = [
        {
            'name': 'TrendFollowing',
            'type': 'trend_following',
            'parameters': {
                'fast_ema': 12,
                'slow_ema': 26,
                'signal_ema': 9,
                'atr_period': 14,
                'atr_multiplier': 2.0,
                'adx_threshold': 25,
                'min_confidence': 0.6
            },
            'enabled': True
        },
        {
            'name': 'MeanReversion',
            'type': 'mean_reversion',
            'parameters': {
                'rsi_period': 14,
                'rsi_oversold': 30,
                'rsi_overbought': 70,
                'bb_period': 20,
                'bb_std': 2,
                'atr_period': 14,
                'adx_threshold': 25,
                'min_confidence': 0.6
            },
            'enabled': True
        },
        {
            'name': 'Breakout',
            'type': 'breakout',
            'parameters': {
                'lookback_period': 20,
                'volume_multiplier': 1.5,
                'atr_period': 14,
                'breakout_threshold': 0.02,
                'consolidation_periods': 10,
                'min_confidence': 0.6
            },
            'enabled': True
        }
    ]

    print("Initializing strategies in database...")

    for strategy in strategies:
        try:
            result = db.client.table("strategies").upsert(strategy, on_conflict='name').execute()
            print(f"✓ Initialized: {strategy['name']}")
        except Exception as e:
            print(f"✗ Error initializing {strategy['name']}: {e}")

    print("\nStrategies initialized successfully!")
    print("\nYou can now:")
    print("1. Run backtests: python trading_bot/main.py backtest")
    print("2. Start paper trading: python trading_bot/main.py")
    print("3. View dashboard: npm run dev")

if __name__ == "__main__":
    asyncio.run(initialize_strategies())
