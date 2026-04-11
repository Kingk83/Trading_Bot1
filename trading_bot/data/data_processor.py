"""
Data Processor
Process and prepare market data for strategies
"""

import pandas as pd
import numpy as np
from typing import Dict, List
from ..utils.indicators import Indicators
from ..utils.logger import logger

class DataProcessor:
    @staticmethod
    def add_indicators(df: pd.DataFrame, indicator_config: Dict) -> pd.DataFrame:
        """Add technical indicators to dataframe"""
        try:
            df = df.copy()

            if 'ema' in indicator_config:
                for period in indicator_config['ema']:
                    df[f'ema_{period}'] = Indicators.ema(df['close'], period)

            if 'sma' in indicator_config:
                for period in indicator_config['sma']:
                    df[f'sma_{period}'] = Indicators.sma(df['close'], period)

            if 'rsi' in indicator_config:
                period = indicator_config['rsi']
                df['rsi'] = Indicators.rsi(df['close'], period)

            if 'macd' in indicator_config:
                fast, slow, signal = indicator_config['macd']
                df['macd'], df['macd_signal'], df['macd_hist'] = Indicators.macd(
                    df['close'], fast, slow, signal
                )

            if 'bollinger_bands' in indicator_config:
                period, std = indicator_config['bollinger_bands']
                df['bb_upper'], df['bb_middle'], df['bb_lower'] = Indicators.bollinger_bands(
                    df['close'], period, std
                )

            if 'atr' in indicator_config:
                period = indicator_config['atr']
                df['atr'] = Indicators.atr(df['high'], df['low'], df['close'], period)

            if 'adx' in indicator_config:
                period = indicator_config['adx']
                df['adx'] = Indicators.adx(df['high'], df['low'], df['close'], period)

            if 'stochastic' in indicator_config:
                period = indicator_config['stochastic']
                df['stoch_k'], df['stoch_d'] = Indicators.stochastic(
                    df['high'], df['low'], df['close'], period
                )

            if 'obv' in indicator_config:
                df['obv'] = Indicators.obv(df['close'], df['volume'])

            if 'vwap' in indicator_config:
                df['vwap'] = Indicators.vwap(df['high'], df['low'], df['close'], df['volume'])

            return df

        except Exception as e:
            logger.error(f"Error adding indicators: {e}")
            return df

    @staticmethod
    def detect_market_regime(df: pd.DataFrame) -> str:
        """Detect current market regime (trending vs ranging)"""
        try:
            if 'adx' not in df.columns:
                df['adx'] = Indicators.adx(df['high'], df['low'], df['close'])

            current_adx = df['adx'].iloc[-1]

            if current_adx > 25:
                return "trending"
            elif current_adx < 20:
                return "ranging"
            else:
                return "neutral"

        except Exception as e:
            logger.error(f"Error detecting market regime: {e}")
            return "unknown"

    @staticmethod
    def calculate_returns(df: pd.DataFrame) -> pd.DataFrame:
        """Calculate returns"""
        df['returns'] = df['close'].pct_change()
        df['log_returns'] = np.log(df['close'] / df['close'].shift(1))
        return df

    @staticmethod
    def resample_timeframe(df: pd.DataFrame, target_timeframe: str) -> pd.DataFrame:
        """Resample to different timeframe"""
        try:
            agg_dict = {
                'open': 'first',
                'high': 'max',
                'low': 'min',
                'close': 'last',
                'volume': 'sum'
            }

            resampled = df.resample(target_timeframe).agg(agg_dict)
            resampled.dropna(inplace=True)

            return resampled

        except Exception as e:
            logger.error(f"Error resampling timeframe: {e}")
            return df

    @staticmethod
    def clean_data(df: pd.DataFrame) -> pd.DataFrame:
        """Clean and validate data"""
        df = df.dropna()

        df = df[df['volume'] > 0]

        df = df[df['high'] >= df['low']]
        df = df[df['high'] >= df['close']]
        df = df[df['low'] <= df['close']]

        return df

    @staticmethod
    def merge_multiple_timeframes(data_dict: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """Merge data from multiple timeframes"""
        base_tf = list(data_dict.keys())[0]
        merged = data_dict[base_tf].copy()

        for tf, df in data_dict.items():
            if tf != base_tf:
                suffix = f"_{tf}"
                df_resampled = df.reindex(merged.index, method='ffill')
                merged = merged.join(df_resampled, rsuffix=suffix)

        return merged

    @staticmethod
    def calculate_volatility_metrics(df: pd.DataFrame) -> Dict:
        """Calculate volatility metrics"""
        returns = df['close'].pct_change()

        metrics = {
            'std_dev': returns.std(),
            'variance': returns.var(),
            'range': (df['high'] - df['low']).mean(),
            'avg_true_range': Indicators.atr(df['high'], df['low'], df['close']).iloc[-1]
        }

        return metrics
