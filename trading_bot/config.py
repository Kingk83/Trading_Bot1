"""
Configuration Management
Centralized configuration for the trading system
"""

import os
from dotenv import load_dotenv
from typing import Dict, Any

load_dotenv()

class Config:
    SUPABASE_URL = os.getenv("VITE_SUPABASE_URL", "")
    SUPABASE_KEY = os.getenv("VITE_SUPABASE_ANON_KEY", "")

    EXCHANGE = os.getenv("EXCHANGE", "binance")
    API_KEY = os.getenv("EXCHANGE_API_KEY", "")
    API_SECRET = os.getenv("EXCHANGE_API_SECRET", "")

    PAPER_TRADING = os.getenv("PAPER_TRADING", "true").lower() == "true"

    MAX_RISK_PER_TRADE = float(os.getenv("MAX_RISK_PER_TRADE", "0.02"))
    MAX_DAILY_DRAWDOWN = float(os.getenv("MAX_DAILY_DRAWDOWN", "0.05"))
    MAX_OPEN_POSITIONS = int(os.getenv("MAX_OPEN_POSITIONS", "5"))
    MIN_RISK_REWARD_RATIO = float(os.getenv("MIN_RISK_REWARD_RATIO", "2.0"))

    INITIAL_CAPITAL = float(os.getenv("INITIAL_CAPITAL", "10000"))
    MIN_POSITION_VALUE = float(os.getenv("MIN_POSITION_VALUE", "5.0"))

    DEFAULT_SYMBOLS = [
        "XRP/USDC",
        "SOL/USDC",
        "XLM/USDC",
        "ADA/USDC",
        "DOGE/USDC",
    ]
    TRADING_SYMBOLS = os.getenv("TRADING_SYMBOLS", "XRP/USDC,SOL/USDC,XLM/USDC,ADA/USDC,DOGE/USDC").split(",")

    TIMEFRAMES = ["1m", "5m", "15m", "1h", "4h", "1d"]
    PRIMARY_TIMEFRAME = "15m"
    TIMEFRAME = os.getenv("TIMEFRAME", "15m")
    LOOKBACK_PERIODS = int(os.getenv("LOOKBACK_PERIODS", "500"))

    SCAN_INTERVAL = int(os.getenv("SCAN_INTERVAL", "60"))

    COMMISSION = float(os.getenv("COMMISSION", "0.001"))
    SLIPPAGE = float(os.getenv("SLIPPAGE", "0.0005"))

    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    @classmethod
    def get_strategy_config(cls, strategy_name: str) -> Dict[str, Any]:
        """Get configuration for specific strategy"""
        configs = {
            "trend_following": {
                "fast_ema": 12,
                "slow_ema": 26,
                "signal_ema": 9,
                "atr_period": 14,
                "atr_multiplier": 2.0,
            },
            "mean_reversion": {
                "rsi_period": 14,
                "rsi_oversold": 30,
                "rsi_overbought": 70,
                "bb_period": 20,
                "bb_std": 2,
            },
            "breakout": {
                "lookback_period": 20,
                "volume_multiplier": 1.5,
                "atr_period": 14,
                "breakout_threshold": 0.02,
            }
        }
        return configs.get(strategy_name, {})

    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if not cls.SUPABASE_URL or not cls.SUPABASE_KEY:
            raise ValueError("Supabase credentials not configured")

        if not cls.PAPER_TRADING and (not cls.API_KEY or not cls.API_SECRET):
            raise ValueError("Exchange API credentials required for live trading")

        return True


Config.validate()
