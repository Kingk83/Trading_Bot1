"""
Market Regime Detector
Identify market conditions (trending vs ranging)
"""

import pandas as pd
import numpy as np
from typing import Dict
from ..utils.indicators import Indicators
from ..utils.logger import logger

class RegimeDetector:
    """
    Market Regimes:
    1. Strong Uptrend
    2. Weak Uptrend
    3. Ranging/Sideways
    4. Weak Downtrend
    5. Strong Downtrend
    """

    @staticmethod
    def detect_regime(df: pd.DataFrame) -> str:
        """Detect current market regime"""
        adx_value = Indicators.adx(df['high'], df['low'], df['close']).iloc[-1]

        ema_20 = Indicators.ema(df['close'], 20).iloc[-1]
        ema_50 = Indicators.ema(df['close'], 50).iloc[-1]
        current_price = df['close'].iloc[-1]

        trend_strength = "ranging"
        trend_direction = "neutral"

        if adx_value > 25:
            trend_strength = "trending"
        elif adx_value > 20:
            trend_strength = "weak_trend"

        if current_price > ema_20 > ema_50:
            trend_direction = "bullish"
        elif current_price < ema_20 < ema_50:
            trend_direction = "bearish"

        if trend_strength == "trending" and trend_direction == "bullish":
            return "strong_uptrend"
        elif trend_strength == "weak_trend" and trend_direction == "bullish":
            return "weak_uptrend"
        elif trend_strength == "trending" and trend_direction == "bearish":
            return "strong_downtrend"
        elif trend_strength == "weak_trend" and trend_direction == "bearish":
            return "weak_downtrend"
        else:
            return "ranging"

    @staticmethod
    def get_regime_characteristics(regime: str) -> Dict:
        """Get characteristics of market regime"""
        characteristics = {
            "strong_uptrend": {
                "best_strategies": ["trend_following"],
                "risk_multiplier": 1.2,
                "position_size_multiplier": 1.1,
                "description": "Strong bullish momentum, high ADX"
            },
            "weak_uptrend": {
                "best_strategies": ["trend_following", "breakout"],
                "risk_multiplier": 1.0,
                "position_size_multiplier": 1.0,
                "description": "Moderate bullish momentum"
            },
            "ranging": {
                "best_strategies": ["mean_reversion"],
                "risk_multiplier": 0.8,
                "position_size_multiplier": 0.9,
                "description": "Sideways movement, low ADX"
            },
            "weak_downtrend": {
                "best_strategies": ["mean_reversion"],
                "risk_multiplier": 0.8,
                "position_size_multiplier": 0.8,
                "description": "Moderate bearish momentum"
            },
            "strong_downtrend": {
                "best_strategies": [],
                "risk_multiplier": 0.5,
                "position_size_multiplier": 0.5,
                "description": "Strong bearish momentum, avoid longs"
            }
        }

        return characteristics.get(regime, characteristics["ranging"])

    @staticmethod
    def analyze_volatility_regime(df: pd.DataFrame) -> str:
        """Analyze volatility regime"""
        atr = Indicators.atr(df['high'], df['low'], df['close'], 14)
        current_atr = atr.iloc[-1]
        avg_atr = atr.rolling(50).mean().iloc[-1]

        volatility_ratio = current_atr / avg_atr if avg_atr > 0 else 1

        if volatility_ratio > 1.5:
            return "high_volatility"
        elif volatility_ratio > 1.2:
            return "elevated_volatility"
        elif volatility_ratio < 0.8:
            return "low_volatility"
        else:
            return "normal_volatility"

    @staticmethod
    def get_market_phase(df: pd.DataFrame) -> str:
        """Identify market phase using cycle analysis"""
        returns = df['close'].pct_change()

        recent_returns = returns.iloc[-20:]

        avg_return = recent_returns.mean()
        volatility = recent_returns.std()

        if avg_return > 0.002 and volatility < 0.02:
            return "accumulation"
        elif avg_return > 0.002 and volatility > 0.02:
            return "markup"
        elif avg_return < -0.002 and volatility < 0.02:
            return "distribution"
        elif avg_return < -0.002 and volatility > 0.02:
            return "markdown"
        else:
            return "neutral"

    @staticmethod
    def should_trade_in_regime(regime: str, strategy_type: str) -> bool:
        """Determine if strategy should trade in current regime"""
        regime_strategy_map = {
            "strong_uptrend": ["trend_following", "breakout", "mean_reversion"],
            "weak_uptrend": ["trend_following", "breakout", "mean_reversion"],
            "ranging": ["mean_reversion", "breakout"],
            "weak_downtrend": ["mean_reversion", "trend_following"],
            "strong_downtrend": ["mean_reversion"]
        }

        allowed_strategies = regime_strategy_map.get(regime, [])
        return strategy_type in allowed_strategies
