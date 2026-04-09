"""
Position Sizer
Calculate position sizes based on risk parameters and volatility
"""

import pandas as pd
from typing import Dict
from config import Config
from utils.logger import logger

class PositionSizer:
    """
    Position Sizing Methods:
    1. Fixed Risk: Risk fixed percentage per trade (1-2%)
    2. Volatility-Adjusted: Scale position based on ATR
    3. Kelly Criterion: Optimal position sizing based on win rate
    """

    def __init__(self, capital: float):
        self.capital = capital
        self.max_risk_per_trade = Config.MAX_RISK_PER_TRADE

    def calculate_position_size(
        self,
        entry_price: float,
        stop_loss: float,
        method: str = 'fixed_risk',
        df: pd.DataFrame = None,
        win_rate: float = None,
        avg_win: float = None,
        avg_loss: float = None
    ) -> Dict:
        """Calculate position size using specified method"""

        if method == 'fixed_risk':
            return self._fixed_risk_sizing(entry_price, stop_loss)
        elif method == 'volatility_adjusted':
            return self._volatility_adjusted_sizing(entry_price, stop_loss, df)
        elif method == 'kelly':
            return self._kelly_criterion_sizing(entry_price, stop_loss, win_rate, avg_win, avg_loss)
        else:
            logger.warning(f"Unknown sizing method: {method}, using fixed_risk")
            return self._fixed_risk_sizing(entry_price, stop_loss)

    def _fixed_risk_sizing(self, entry_price: float, stop_loss: float) -> Dict:
        """Fixed risk per trade (1-2% of capital)"""
        risk_amount = self.capital * self.max_risk_per_trade

        price_risk = abs(entry_price - stop_loss)

        if price_risk == 0:
            logger.error("Stop loss equals entry price")
            return {'quantity': 0, 'risk_amount': 0, 'position_value': 0}

        quantity = risk_amount / price_risk

        position_value = quantity * entry_price

        if position_value < Config.MIN_POSITION_VALUE:
            max_position_cap = self.capital * 0.30
            position_value = min(Config.MIN_POSITION_VALUE, max_position_cap)
            quantity = position_value / entry_price
            logger.info(f"Position value boosted to minimum ${Config.MIN_POSITION_VALUE} (was below minimum)")

        position_percentage = (position_value / self.capital) * 100

        return {
            'quantity': round(quantity, 8),
            'risk_amount': round(risk_amount, 2),
            'position_value': round(position_value, 2),
            'position_percentage': round(position_percentage, 2),
            'method': 'fixed_risk'
        }

    def _volatility_adjusted_sizing(self, entry_price: float, stop_loss: float, df: pd.DataFrame) -> Dict:
        """Adjust position size based on volatility (ATR)"""
        if df is None or 'atr' not in df.columns:
            logger.warning("ATR not available, using fixed risk")
            return self._fixed_risk_sizing(entry_price, stop_loss)

        atr = df['atr'].iloc[-1]
        avg_atr = df['atr'].rolling(20).mean().iloc[-1]

        volatility_ratio = atr / avg_atr

        adjusted_risk = self.max_risk_per_trade / volatility_ratio
        adjusted_risk = max(0.005, min(adjusted_risk, self.max_risk_per_trade))

        risk_amount = self.capital * adjusted_risk
        price_risk = abs(entry_price - stop_loss)
        quantity = risk_amount / price_risk

        position_value = quantity * entry_price
        position_percentage = (position_value / self.capital) * 100

        return {
            'quantity': round(quantity, 8),
            'risk_amount': round(risk_amount, 2),
            'position_value': round(position_value, 2),
            'position_percentage': round(position_percentage, 2),
            'volatility_ratio': round(volatility_ratio, 2),
            'method': 'volatility_adjusted'
        }

    def _kelly_criterion_sizing(
        self,
        entry_price: float,
        stop_loss: float,
        win_rate: float,
        avg_win: float,
        avg_loss: float
    ) -> Dict:
        """Kelly Criterion for optimal position sizing"""
        if win_rate is None or avg_win is None or avg_loss is None:
            logger.warning("Kelly criterion parameters missing, using fixed risk")
            return self._fixed_risk_sizing(entry_price, stop_loss)

        if avg_loss == 0:
            logger.warning("Average loss is zero, using fixed risk")
            return self._fixed_risk_sizing(entry_price, stop_loss)

        win_loss_ratio = avg_win / abs(avg_loss)

        kelly_percentage = (win_rate * win_loss_ratio - (1 - win_rate)) / win_loss_ratio

        kelly_percentage = max(0, min(kelly_percentage, 0.25))

        fractional_kelly = kelly_percentage * 0.5

        risk_amount = self.capital * fractional_kelly
        price_risk = abs(entry_price - stop_loss)
        quantity = risk_amount / price_risk

        position_value = quantity * entry_price
        position_percentage = (position_value / self.capital) * 100

        return {
            'quantity': round(quantity, 8),
            'risk_amount': round(risk_amount, 2),
            'position_value': round(position_value, 2),
            'position_percentage': round(position_percentage, 2),
            'kelly_percentage': round(fractional_kelly * 100, 2),
            'method': 'kelly_criterion'
        }

    def update_capital(self, new_capital: float):
        """Update capital for position sizing"""
        self.capital = new_capital
        logger.info(f"Capital updated to: ${new_capital:,.2f}")

    def validate_position_size(self, quantity: float, price: float) -> bool:
        """Validate position size against capital constraints"""
        position_value = quantity * price
        max_position_value = self.capital * 0.3

        if position_value < Config.MIN_POSITION_VALUE:
            logger.warning(f"Position value ${position_value:.2f} below minimum ${Config.MIN_POSITION_VALUE}")
            return False

        if position_value > max_position_value:
            logger.warning(f"Position value ${position_value:,.2f} exceeds 30% of capital")
            return False

        return True
