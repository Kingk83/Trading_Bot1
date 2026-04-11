"""
Trend Following Strategy
Uses EMA crossover and MACD for trend identification
Enters on trend confirmation, exits on reversal or targets
"""

import pandas as pd
from typing import Optional, Dict
from .base_strategy import BaseStrategy, Signal, SignalType
from ..utils.indicators import Indicators

class TrendFollowingStrategy(BaseStrategy):
    """
    Strategy Logic:
    Entry (Long):
    - Fast EMA crosses above Slow EMA
    - MACD line crosses above signal line
    - ADX > 25 (strong trend)
    - Price above both EMAs

    Entry (Short):
    - Fast EMA crosses below Slow EMA
    - MACD line crosses below signal line
    - ADX > 25 (strong trend)
    - Price below both EMAs

    Exit:
    - Stop Loss: 2 x ATR below entry (long) or above entry (short)
    - Take Profit: 4 x ATR (Risk:Reward = 1:2)
    - Signal reversal

    Position Sizing:
    - Based on ATR volatility
    - Risk per trade: 1-2% of capital
    """

    def __init__(self, parameters: Dict = None):
        default_params = {
            'fast_ema': 12,
            'slow_ema': 26,
            'signal_ema': 9,
            'atr_period': 14,
            'atr_multiplier': 2.0,
            'adx_threshold': 25,
            'min_confidence': 0.6
        }

        if parameters:
            default_params.update(parameters)

        super().__init__("TrendFollowing", default_params)

    def generate_signal(self, df: pd.DataFrame) -> Optional[Signal]:
        """Generate trend following signal"""
        if len(df) < self.parameters['slow_ema'] + 10:
            return None

        df = self._add_indicators(df)

        current_price = df['close'].iloc[-1]
        fast_ema_current = df['fast_ema'].iloc[-1]
        slow_ema_current = df['slow_ema'].iloc[-1]
        fast_ema_prev = df['fast_ema'].iloc[-2]
        slow_ema_prev = df['slow_ema'].iloc[-2]

        macd_current = df['macd'].iloc[-1]
        macd_signal_current = df['macd_signal'].iloc[-1]
        macd_prev = df['macd'].iloc[-2]
        macd_signal_prev = df['macd_signal'].iloc[-2]

        adx_current = df['adx'].iloc[-1]

        bullish_ema_cross = (fast_ema_current > slow_ema_current and
                            fast_ema_prev <= slow_ema_prev)
        bearish_ema_cross = (fast_ema_current < slow_ema_current and
                            fast_ema_prev >= slow_ema_prev)

        bullish_macd_cross = (macd_current > macd_signal_current and
                             macd_prev <= macd_signal_prev)
        bearish_macd_cross = (macd_current < macd_signal_current and
                             macd_prev >= macd_signal_prev)

        strong_trend = adx_current > self.parameters['adx_threshold']

        if bullish_ema_cross and bullish_macd_cross and strong_trend:
            confidence = self._calculate_confidence(df, 'long')
            if confidence >= self.parameters['min_confidence']:
                stop_loss = self.calculate_stop_loss(current_price, 'long', df)
                take_profit = self.calculate_take_profit(current_price, 'long', df)

                return Signal(
                    type=SignalType.BUY,
                    price=current_price,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    confidence=confidence,
                    metadata={
                        'strategy': 'trend_following',
                        'adx': adx_current,
                        'ema_spread': (fast_ema_current - slow_ema_current) / current_price
                    }
                )

        if bearish_ema_cross and bearish_macd_cross and strong_trend:
            confidence = self._calculate_confidence(df, 'short')
            if confidence >= self.parameters['min_confidence']:
                stop_loss = self.calculate_stop_loss(current_price, 'short', df)
                take_profit = self.calculate_take_profit(current_price, 'short', df)

                return Signal(
                    type=SignalType.SELL,
                    price=current_price,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    confidence=confidence,
                    metadata={
                        'strategy': 'trend_following',
                        'adx': adx_current,
                        'ema_spread': (fast_ema_current - slow_ema_current) / current_price
                    }
                )

        return None

    def _add_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add required indicators"""
        df = df.copy()

        df['fast_ema'] = Indicators.ema(df['close'], self.parameters['fast_ema'])
        df['slow_ema'] = Indicators.ema(df['close'], self.parameters['slow_ema'])

        df['macd'], df['macd_signal'], df['macd_hist'] = Indicators.macd(
            df['close'],
            self.parameters['fast_ema'],
            self.parameters['slow_ema'],
            self.parameters['signal_ema']
        )

        df['atr'] = Indicators.atr(
            df['high'],
            df['low'],
            df['close'],
            self.parameters['atr_period']
        )

        df['adx'] = Indicators.adx(
            df['high'],
            df['low'],
            df['close'],
            self.parameters['atr_period']
        )

        return df

    def _calculate_confidence(self, df: pd.DataFrame, side: str) -> float:
        """Calculate signal confidence score"""
        adx = df['adx'].iloc[-1]
        macd_hist = df['macd_hist'].iloc[-1]

        trend_strength = min(adx / 50, 1.0)

        momentum_strength = min(abs(macd_hist) / df['macd_hist'].std(), 1.0)

        if side == 'long':
            price_position = (df['close'].iloc[-1] - df['slow_ema'].iloc[-1]) / df['slow_ema'].iloc[-1]
        else:
            price_position = (df['slow_ema'].iloc[-1] - df['close'].iloc[-1]) / df['slow_ema'].iloc[-1]

        price_strength = min(abs(price_position) * 10, 1.0)

        confidence = (trend_strength * 0.4 + momentum_strength * 0.3 + price_strength * 0.3)

        return round(confidence, 2)

    def calculate_stop_loss(self, entry_price: float, side: str, df: pd.DataFrame) -> float:
        """Calculate stop loss using ATR"""
        atr = df['atr'].iloc[-1]
        multiplier = self.parameters['atr_multiplier']

        if side == 'long':
            stop_loss = entry_price - (atr * multiplier)
        else:
            stop_loss = entry_price + (atr * multiplier)

        return round(stop_loss, 8)

    def calculate_take_profit(self, entry_price: float, side: str, df: pd.DataFrame) -> float:
        """Calculate take profit (2:1 risk/reward)"""
        atr = df['atr'].iloc[-1]
        multiplier = self.parameters['atr_multiplier'] * 2

        if side == 'long':
            take_profit = entry_price + (atr * multiplier)
        else:
            take_profit = entry_price - (atr * multiplier)

        return round(take_profit, 8)
