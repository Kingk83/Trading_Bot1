"""
Multi-Timeframe Analysis
Analyze multiple timeframes for confluence
"""

import pandas as pd
from typing import Dict, List
from ..utils.indicators import Indicators
from ..utils.logger import logger

class MultiTimeframeAnalyzer:
    """
    Timeframe Hierarchy:
    - Higher timeframe: Trend direction
    - Medium timeframe: Entry timing
    - Lower timeframe: Precise entry
    """

    def __init__(self, timeframes: List[str] = None):
        self.timeframes = timeframes or ['15m', '1h', '4h']

    def analyze_confluence(self, data_dict: Dict[str, pd.DataFrame]) -> Dict:
        """Analyze multiple timeframes for signal confluence"""
        analysis = {}

        for timeframe, df in data_dict.items():
            if len(df) < 50:
                continue

            ema_20 = Indicators.ema(df['close'], 20)
            ema_50 = Indicators.ema(df['close'], 50)
            rsi = Indicators.rsi(df['close'], 14)
            macd, macd_signal, _ = Indicators.macd(df['close'])
            adx = Indicators.adx(df['high'], df['low'], df['close'])

            current_price = df['close'].iloc[-1]

            trend = "bullish" if ema_20.iloc[-1] > ema_50.iloc[-1] else "bearish"

            momentum = "bullish" if macd.iloc[-1] > macd_signal.iloc[-1] else "bearish"

            strength = "strong" if adx.iloc[-1] > 25 else "weak"

            rsi_value = rsi.iloc[-1]
            rsi_state = "overbought" if rsi_value > 70 else "oversold" if rsi_value < 30 else "neutral"

            analysis[timeframe] = {
                'trend': trend,
                'momentum': momentum,
                'strength': strength,
                'rsi': rsi_value,
                'rsi_state': rsi_state,
                'adx': adx.iloc[-1],
                'price_vs_ema20': (current_price - ema_20.iloc[-1]) / ema_20.iloc[-1] * 100
            }

        confluence_score = self._calculate_confluence_score(analysis)

        return {
            'analysis': analysis,
            'confluence_score': confluence_score,
            'recommendation': self._get_recommendation(analysis, confluence_score)
        }

    def _calculate_confluence_score(self, analysis: Dict) -> float:
        """Calculate confluence score across timeframes"""
        if not analysis:
            return 0.0

        trend_scores = []
        for tf, data in analysis.items():
            score = 1.0 if data['trend'] == 'bullish' else -1.0
            if data['momentum'] == data['trend']:
                score *= 1.2
            if data['strength'] == 'strong':
                score *= 1.1

            trend_scores.append(score)

        avg_score = sum(trend_scores) / len(trend_scores)

        consistency = 1 - (len(set([d['trend'] for d in analysis.values()])) - 1) / max(len(analysis) - 1, 1)

        final_score = (abs(avg_score) * 0.7 + consistency * 0.3)

        return round(final_score, 2)

    def _get_recommendation(self, analysis: Dict, confluence_score: float) -> str:
        """Get trading recommendation based on analysis"""
        if confluence_score > 0.7:
            dominant_trend = max(set([d['trend'] for d in analysis.values()]),
                                key=lambda x: sum(1 for d in analysis.values() if d['trend'] == x))
            return f"strong_{dominant_trend}_signal"
        elif confluence_score > 0.5:
            return "moderate_signal"
        else:
            return "no_clear_signal"

    def check_higher_timeframe_alignment(
        self,
        signal_timeframe: str,
        data_dict: Dict[str, pd.DataFrame]
    ) -> bool:
        """Check if signal aligns with higher timeframe trend"""
        timeframe_hierarchy = {'5m': 1, '15m': 2, '1h': 3, '4h': 4, '1d': 5}

        signal_level = timeframe_hierarchy.get(signal_timeframe, 2)

        higher_timeframes = {tf: df for tf, df in data_dict.items()
                           if timeframe_hierarchy.get(tf, 0) > signal_level}

        if not higher_timeframes:
            return True

        signal_df = data_dict.get(signal_timeframe)
        if signal_df is None:
            return False

        signal_trend = self._get_trend(signal_df)

        for tf, df in higher_timeframes.items():
            htf_trend = self._get_trend(df)
            if htf_trend != signal_trend:
                logger.info(f"Higher timeframe {tf} trend ({htf_trend}) conflicts with signal trend ({signal_trend})")
                return False

        return True

    def _get_trend(self, df: pd.DataFrame) -> str:
        """Determine trend direction"""
        ema_20 = Indicators.ema(df['close'], 20).iloc[-1]
        ema_50 = Indicators.ema(df['close'], 50).iloc[-1]

        return "bullish" if ema_20 > ema_50 else "bearish"

    def get_entry_timeframe_signal(
        self,
        higher_tf_trend: str,
        entry_tf_data: pd.DataFrame
    ) -> Dict:
        """Get precise entry signal on lower timeframe"""
        rsi = Indicators.rsi(entry_tf_data['close'], 14).iloc[-1]

        if higher_tf_trend == "bullish":
            if 30 < rsi < 50:
                return {
                    'signal': 'buy',
                    'quality': 'high',
                    'reason': 'Higher TF bullish, entry TF pullback'
                }
        elif higher_tf_trend == "bearish":
            if 50 < rsi < 70:
                return {
                    'signal': 'sell',
                    'quality': 'high',
                    'reason': 'Higher TF bearish, entry TF bounce'
                }

        return {
            'signal': 'wait',
            'quality': 'low',
            'reason': 'No quality entry setup'
        }
