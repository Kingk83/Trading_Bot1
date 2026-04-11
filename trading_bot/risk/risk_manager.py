"""
Risk Manager
Enforce risk limits and protect capital
"""

from typing import Dict, List, Optional, Union, Tuple
from datetime import datetime, date, timedelta
from ..config import Config
from ..utils.logger import logger
from ..utils.database import db

class RiskManager:
    """
    Risk Management Controls:
    1. Max risk per trade: 1-2%
    2. Max daily drawdown: 5%
    3. Max open positions: 5
    4. Min risk/reward ratio: 1:2
    5. Correlation limits
    6. Exposure limits
    """

    def __init__(self, initial_capital: float):
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.daily_starting_capital = initial_capital
        self.max_daily_drawdown = Config.MAX_DAILY_DRAWDOWN
        self.max_open_positions = Config.MAX_OPEN_POSITIONS
        self.min_risk_reward_ratio = Config.MIN_RISK_REWARD_RATIO

        self.open_positions: List[Dict] = []
        self.daily_trades: List[Dict] = []
        self.risk_events: List[Dict] = []

    async def check_trade_approval(self, signal, position_size: Dict) -> Tuple[bool, str]:
        """Comprehensive risk check before trade execution"""

        if len(self.open_positions) >= self.max_open_positions:
            await self._log_risk_event("position_limit", "warning", "Max open positions reached")
            return False, "Max open positions reached"

        if not self._check_risk_reward(signal):
            return False, "Risk/reward ratio too low"

        if not await self._check_daily_drawdown():
            await self._log_risk_event("daily_drawdown", "critical", "Daily drawdown limit reached")
            return False, "Daily drawdown limit reached"

        symbol = signal.metadata.get('symbol', '') if hasattr(signal, 'metadata') else signal.get('symbol', '')
        if not self._check_position_correlation(symbol):
            return False, "High correlation with existing positions"

        if not self._check_capital_adequacy(position_size):
            return False, "Insufficient capital for position"

        return True, "Trade approved"

    def _check_risk_reward(self, signal) -> bool:
        """Check risk/reward ratio"""
        if hasattr(signal, 'price'):
            entry_price = signal.price
            stop_loss = signal.stop_loss
            take_profit = signal.take_profit
        else:
            entry_price = signal['price']
            stop_loss = signal['stop_loss']
            take_profit = signal['take_profit']

        risk = abs(entry_price - stop_loss)
        reward = abs(take_profit - entry_price)

        if risk == 0:
            return False

        risk_reward_ratio = reward / risk

        if risk_reward_ratio < self.min_risk_reward_ratio:
            logger.warning(f"Risk/reward ratio {risk_reward_ratio:.2f} below minimum {self.min_risk_reward_ratio}")
            return False

        return True

    async def _check_daily_drawdown(self) -> bool:
        """Check if daily drawdown limit is breached"""
        current_drawdown = (self.daily_starting_capital - self.current_capital) / self.daily_starting_capital

        if current_drawdown >= self.max_daily_drawdown:
            logger.critical(f"Daily drawdown {current_drawdown*100:.2f}% exceeds limit {self.max_daily_drawdown*100:.2f}%")
            return False

        return True

    def _check_position_correlation(self, symbol: str) -> bool:
        """Check correlation with existing positions"""
        correlated_symbols = {
            'BTC/USDT': ['ETH/USDT'],
            'ETH/USDT': ['BTC/USDT'],
        }

        if symbol in correlated_symbols:
            for pos in self.open_positions:
                if pos['symbol'] in correlated_symbols[symbol]:
                    logger.warning(f"High correlation between {symbol} and {pos['symbol']}")
                    return False

        return True

    def _check_capital_adequacy(self, position_size: Dict) -> bool:
        """Check if adequate capital for position"""
        position_value = position_size['position_value']
        available_capital = self.current_capital

        open_positions_value = sum(pos['position_value'] for pos in self.open_positions)
        remaining_capital = available_capital - open_positions_value

        if position_value > remaining_capital:
            logger.warning(f"Insufficient capital. Required: ${position_value:,.2f}, Available: ${remaining_capital:,.2f}")
            return False

        return True

    async def register_position(self, position: Dict):
        """Register new open position"""
        self.open_positions.append(position)
        logger.info(f"Position registered: {position['symbol']} - {len(self.open_positions)}/{self.max_open_positions} positions")

    async def close_position(self, position_id: str, exit_price: float, exit_reason: str):
        """Close position and update capital"""
        position = next((p for p in self.open_positions if p['id'] == position_id), None)

        if not position:
            logger.error(f"Position {position_id} not found")
            return

        entry_price = position['entry_price']
        quantity = position['quantity']

        if position['side'] == 'long':
            pnl = (exit_price - entry_price) * quantity
        else:
            pnl = (entry_price - exit_price) * quantity

        pnl_percent = (pnl / (entry_price * quantity)) * 100

        self.current_capital += pnl

        trade_record = {
            'position_id': position_id,
            'symbol': position['symbol'],
            'pnl': pnl,
            'pnl_percent': pnl_percent,
            'exit_reason': exit_reason,
            'exit_time': datetime.now()
        }
        self.daily_trades.append(trade_record)

        self.open_positions = [p for p in self.open_positions if p['id'] != position_id]

        logger.info(f"Position closed: {position['symbol']} | PnL: ${pnl:.2f} ({pnl_percent:.2f}%)")

    def calculate_max_position_size(self, entry_price: float, stop_loss: float) -> float:
        """Calculate maximum position size based on risk"""
        risk_amount = self.current_capital * Config.MAX_RISK_PER_TRADE
        price_risk = abs(entry_price - stop_loss)

        if price_risk == 0:
            return 0

        max_quantity = risk_amount / price_risk
        return max_quantity

    async def reset_daily_metrics(self):
        """Reset daily tracking metrics"""
        self.daily_starting_capital = self.current_capital
        self.daily_trades = []
        logger.info(f"Daily metrics reset. Starting capital: ${self.current_capital:,.2f}")

    async def _log_risk_event(self, event_type: str, severity: str, message: str):
        """Log risk event to database"""
        await db.log_risk_event(
            event_type=event_type,
            severity=severity,
            message=message,
            data={
                'capital': self.current_capital,
                'open_positions': len(self.open_positions),
                'timestamp': datetime.now().isoformat()
            }
        )

    def get_risk_metrics(self) -> Dict:
        """Get current risk metrics"""
        open_positions_value = sum(pos['position_value'] for pos in self.open_positions)
        exposure_percentage = (open_positions_value / self.current_capital) * 100

        daily_pnl = sum(trade['pnl'] for trade in self.daily_trades)
        daily_return = (daily_pnl / self.daily_starting_capital) * 100

        current_drawdown = (self.daily_starting_capital - self.current_capital) / self.daily_starting_capital * 100

        return {
            'current_capital': round(self.current_capital, 2),
            'daily_starting_capital': round(self.daily_starting_capital, 2),
            'open_positions': len(self.open_positions),
            'max_positions': self.max_open_positions,
            'exposure_percentage': round(exposure_percentage, 2),
            'daily_pnl': round(daily_pnl, 2),
            'daily_return': round(daily_return, 2),
            'current_drawdown': round(current_drawdown, 2),
            'max_drawdown_limit': self.max_daily_drawdown * 100,
            'total_return': round(((self.current_capital - self.initial_capital) / self.initial_capital) * 100, 2)
        }

    def is_trading_allowed(self) -> bool:
        """Check if trading is allowed based on risk limits"""
        current_drawdown = (self.daily_starting_capital - self.current_capital) / self.daily_starting_capital

        if current_drawdown >= self.max_daily_drawdown:
            return False

        if len(self.open_positions) >= self.max_open_positions:
            return False

        return True
