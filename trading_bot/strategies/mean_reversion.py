"""
Mean Reversion Strategy
Uses RSI and Bollinger Bands to identify overbought/oversold conditions
Enters when price deviates from mean, exits on return to mean
"""

import pandas as pd
from typing import Optional, Dict
from .base_strategy import BaseStrategy, Signal, SignalType
from ..utils.indicators import Indicators

class MeanReversionStrategy(BaseStrategy):
    """
    Strategy Logic:
    Entry (Long):
    - RSI < 30 (oversold)
    - Price touches or breaks below lower Bollinger Band
    - Volume spike (> 1.5x average)
    - Not in strong downtrend (ADX check)

    Entry (Short):
    - RSI > 70 (overbought)
    - Price touches or breaks above upper Bollinger Band
    - Volume spike (> 1.5x average)
    - Not in strong uptrend (ADX check)

    Exit:
    - Stop Loss: Beyond opposite Bollinger Band
    - Take Profit: Middle Bollinger Band (mean)
    - RSI returns to neutral (45-55)

    Best suited for ranging markets
    """

    def __init__(self, parameters: Dict = None):
        default_params = {
            'rsi_period': 14,
            'rsi_oversold': 30,
            'rsi_overbought': 70,
            'bb_period': 20,
            'bb_std': 2,
            'volume_multiplier': 1.5,
            'adx_max': 25,
            'min_confidence': 0.6
        }

        if parameters:
            default_params.update(parameters)

        super().__init__("MeanReversion", default_params)

    def generate_signal(self, df: pd.DataFrame) -> Optional[Signal]:
        """Generate mean reversion signal"""
        if len(df) < max(self.parameters['rsi_period'], self.parameters['bb_period']) + 10:
            return None

        df = self._add_indicators(df)

        current_price = df['close'].iloc[-1]
        rsi = df['rsi'].iloc[-1]
        bb_upper = df['bb_upper'].iloc[-1]
        bb_lower = df['bb_lower'].iloc[-1]
        bb_middle = df['bb_middle'].iloc[-1]
        adx = df['adx'].iloc[-1]

        avg_volume = df['volume'].rolling(20).mean().iloc[-1]
        current_volume = df['volume'].iloc[-1]
        volume_spike = current_volume > (avg_volume * self.parameters['volume_multiplier'])

        not_strong_trend = adx < self.parameters['adx_max']

        bb_position = (current_price - bb_lower) / (bb_upper - bb_lower)

        if (rsi < self.parameters['rsi_oversold'] and
            bb_position < 0.2 and
            volume_spike and
            not_strong_trend):

            confidence = self._calculate_confidence(df, 'long', rsi, bb_position)
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
                        'strategy': 'mean_reversion',
                        'rsi': rsi,
                        'bb_position': bb_position,
                        'distance_from_mean': (bb_middle - current_price) / current_price
                    }
                )

        if (rsi > self.parameters['rsi_overbought'] and
            bb_position > 0.8 and
            volume_spike and
            not_strong_trend):

            confidence = self._calculate_confidence(df, 'short', rsi, bb_position)
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
                        'strategy': 'mean_reversion',
                        'rsi': rsi,
                        'bb_position': bb_position,
                        'distance_from_mean': (current_price - bb_middle) / current_price
                    }
                )

        return None

    def _add_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add required indicators"""
        df = df.copy()

        df['rsi'] = Indicators.rsi(df['close'], self.parameters['rsi_period'])

        df['bb_upper'], df['bb_middle'], df['bb_lower'] = Indicators.bollinger_bands(
            df['close'],
            self.parameters['bb_period'],
            self.parameters['bb_std']
        )

        df['adx'] = Indicators.adx(df['high'], df['low'], df['close'], 14)

        df['atr'] = Indicators.atr(df['high'], df['low'], df['close'], 14)

        return df

    def _calculate_confidence(self, df: pd.DataFrame, side: str, rsi: float, bb_position: float) -> float:
        """Calculate signal confidence score"""
        if side == 'long':
            rsi_strength = (self.parameters['rsi_oversold'] - rsi) / self.parameters['rsi_oversold']
            rsi_strength = max(0, min(rsi_strength, 1))

            bb_strength = (0.2 - bb_position) / 0.2
            bb_strength = max(0, min(bb_strength, 1))
        else:
            rsi_strength = (rsi - self.parameters['rsi_overbought']) / (100 - self.parameters['rsi_overbought'])
            rsi_strength = max(0, min(rsi_strength, 1))

            bb_strength = (bb_position - 0.8) / 0.2
            bb_strength = max(0, min(bb_strength, 1))

        avg_volume = df['volume'].rolling(20).mean().iloc[-1]
        volume_ratio = df['volume'].iloc[-1] / avg_volume
        volume_strength = min(volume_ratio / 3, 1.0)

        confidence = (rsi_strength * 0.4 + bb_strength * 0.4 + volume_strength * 0.2)

        return round(confidence, 2)

    def calculate_stop_loss(self, entry_price: float, side: str, df: pd.DataFrame) -> float:
        """Calculate stop loss beyond opposite Bollinger Band"""
        bb_upper = df['bb_upper'].iloc[-1]
        bb_lower = df['bb_lower'].iloc[-1]
        atr = df['atr'].iloc[-1]

        if side == 'long':
            stop_loss = bb_lower - (atr * 0.5)
        else:
            stop_loss = bb_upper + (atr * 0.5)

        return round(stop_loss, 8)

    def calculate_take_profit(self, entry_price: float, side: str, df: pd.DataFrame) -> float:
        """Calculate take profit at middle Bollinger Band"""
        bb_middle = df['bb_middle'].iloc[-1]

        return round(bb_middle, 8)
