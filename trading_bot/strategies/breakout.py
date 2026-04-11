"""
Breakout Strategy
Identifies price breakouts from consolidation with volume confirmation
Enters on breakout, exits on exhaustion or reversal
"""

import pandas as pd
from typing import Optional, Dict
from .base_strategy import BaseStrategy, Signal, SignalType
from ..utils.indicators import Indicators

class BreakoutStrategy(BaseStrategy):
    """
    Strategy Logic:
    Entry (Long):
    - Price breaks above resistance (20-period high)
    - Volume > 1.5x average volume (confirmation)
    - ATR expanding (volatility increase)
    - Consolidation before breakout (low volatility period)

    Entry (Short):
    - Price breaks below support (20-period low)
    - Volume > 1.5x average volume (confirmation)
    - ATR expanding (volatility increase)
    - Consolidation before breakdown

    Exit:
    - Stop Loss: Below/above the consolidation range
    - Take Profit: 2x the consolidation range
    - Momentum exhaustion (declining volume, bearish divergence)

    Best suited for volatile, trending markets
    """

    def __init__(self, parameters: Dict = None):
        default_params = {
            'lookback_period': 20,
            'volume_multiplier': 1.5,
            'atr_period': 14,
            'breakout_threshold': 0.02,
            'consolidation_periods': 10,
            'min_confidence': 0.6
        }

        if parameters:
            default_params.update(parameters)

        super().__init__("Breakout", default_params)

    def generate_signal(self, df: pd.DataFrame) -> Optional[Signal]:
        """Generate breakout signal"""
        if len(df) < self.parameters['lookback_period'] + 20:
            return None

        df = self._add_indicators(df)

        current_price = df['close'].iloc[-1]
        high_level = df['high'].rolling(self.parameters['lookback_period']).max().iloc[-2]
        low_level = df['low'].rolling(self.parameters['lookback_period']).min().iloc[-2]

        avg_volume = df['volume'].rolling(20).mean().iloc[-1]
        current_volume = df['volume'].iloc[-1]
        volume_confirmed = current_volume > (avg_volume * self.parameters['volume_multiplier'])

        atr_current = df['atr'].iloc[-1]
        atr_prev = df['atr'].iloc[-5]
        volatility_expanding = atr_current > atr_prev

        was_consolidating = self._check_consolidation(df)

        breakout_percentage = (current_price - high_level) / high_level

        if (current_price > high_level and
            breakout_percentage > self.parameters['breakout_threshold'] and
            volume_confirmed and
            volatility_expanding and
            was_consolidating):

            confidence = self._calculate_confidence(df, 'long', breakout_percentage, current_volume / avg_volume)
            if confidence >= self.parameters['min_confidence']:
                stop_loss = self.calculate_stop_loss(current_price, 'long', df, low_level)
                take_profit = self.calculate_take_profit(current_price, 'long', df, high_level, low_level)

                return Signal(
                    type=SignalType.BUY,
                    price=current_price,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    confidence=confidence,
                    metadata={
                        'strategy': 'breakout',
                        'breakout_level': high_level,
                        'breakout_strength': breakout_percentage,
                        'volume_ratio': current_volume / avg_volume
                    }
                )

        breakdown_percentage = (low_level - current_price) / low_level

        if (current_price < low_level and
            breakdown_percentage > self.parameters['breakout_threshold'] and
            volume_confirmed and
            volatility_expanding and
            was_consolidating):

            confidence = self._calculate_confidence(df, 'short', breakdown_percentage, current_volume / avg_volume)
            if confidence >= self.parameters['min_confidence']:
                stop_loss = self.calculate_stop_loss(current_price, 'short', df, high_level)
                take_profit = self.calculate_take_profit(current_price, 'short', df, high_level, low_level)

                return Signal(
                    type=SignalType.SELL,
                    price=current_price,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    confidence=confidence,
                    metadata={
                        'strategy': 'breakout',
                        'breakout_level': low_level,
                        'breakout_strength': breakdown_percentage,
                        'volume_ratio': current_volume / avg_volume
                    }
                )

        return None

    def _add_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add required indicators"""
        df = df.copy()

        df['atr'] = Indicators.atr(
            df['high'],
            df['low'],
            df['close'],
            self.parameters['atr_period']
        )

        df['sma_20'] = Indicators.sma(df['close'], 20)
        df['sma_50'] = Indicators.sma(df['close'], 50)

        return df

    def _check_consolidation(self, df: pd.DataFrame) -> bool:
        """Check if price was in consolidation before breakout"""
        lookback = self.parameters['consolidation_periods']
        recent_data = df.iloc[-lookback-1:-1]

        price_range = recent_data['high'].max() - recent_data['low'].min()
        avg_price = recent_data['close'].mean()
        range_percentage = price_range / avg_price

        atr_mean = recent_data['atr'].mean()
        atr_std = recent_data['atr'].std()
        low_volatility = atr_std < (atr_mean * 0.2)

        return range_percentage < 0.05 and low_volatility

    def _calculate_confidence(self, df: pd.DataFrame, side: str, breakout_strength: float, volume_ratio: float) -> float:
        """Calculate signal confidence score"""
        strength_score = min(breakout_strength / 0.05, 1.0)

        volume_score = min(volume_ratio / 3, 1.0)

        atr_current = df['atr'].iloc[-1]
        atr_avg = df['atr'].rolling(20).mean().iloc[-1]
        volatility_score = min(atr_current / atr_avg, 1.5) - 0.5
        volatility_score = max(0, min(volatility_score, 1))

        confidence = (strength_score * 0.4 + volume_score * 0.35 + volatility_score * 0.25)

        return round(confidence, 2)

    def calculate_stop_loss(self, entry_price: float, side: str, df: pd.DataFrame, level: float) -> float:
        """Calculate stop loss below/above consolidation"""
        atr = df['atr'].iloc[-1]

        if side == 'long':
            stop_loss = level - (atr * 1.5)
        else:
            stop_loss = level + (atr * 1.5)

        return round(stop_loss, 8)

    def calculate_take_profit(self, entry_price: float, side: str, df: pd.DataFrame, high_level: float, low_level: float) -> float:
        """Calculate take profit based on range projection"""
        range_size = high_level - low_level

        if side == 'long':
            take_profit = entry_price + (range_size * 2)
        else:
            take_profit = entry_price - (range_size * 2)

        return round(take_profit, 8)
