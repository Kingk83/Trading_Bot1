"""
Order Manager
Manage order lifecycle and execution
"""

from typing import Dict, Optional
from datetime import datetime
from .exchange_interface import ExchangeInterface
from ..risk.risk_manager import RiskManager
from ..risk.position_sizer import PositionSizer
from ..strategies.base_strategy import Signal
from ..utils.logger import logger
from ..utils.database import db

class OrderManager:
    def __init__(self, risk_manager: RiskManager, position_sizer: PositionSizer):
        self.exchange = ExchangeInterface()
        self.risk_manager = risk_manager
        self.position_sizer = position_sizer

    async def execute_signal(self, signal: Signal, strategy_id: str, df) -> Optional[str]:
        """Execute trading signal"""
        try:
            entry_price = signal.price
            stop_loss = signal.stop_loss

            position_size = self.position_sizer.calculate_position_size(
                entry_price=entry_price,
                stop_loss=stop_loss,
                method='volatility_adjusted',
                df=df
            )

            approved, message = await self.risk_manager.check_trade_approval(signal, position_size)
            if not approved:
                logger.warning(f"Trade rejected: {message}")
                return None

            side = 'buy' if signal.type.value == 'buy' else 'sell'
            symbol = signal.metadata.get('symbol', '')
            order = await self.exchange.place_market_order(
                symbol=symbol,
                side=side,
                quantity=position_size['quantity']
            )

            if not order:
                logger.error("Order execution failed")
                return None

            actual_entry_price = order['average'] if order.get('average') else entry_price

            if stop_loss:
                stop_order = await self.exchange.place_stop_loss_order(
                    symbol=symbol,
                    side='long' if side == 'buy' else 'short',
                    quantity=position_size['quantity'],
                    stop_price=stop_loss
                )
                if not stop_order:
                    logger.error(f"Stop loss order failed for {symbol} after entry filled - attempting to close entry position")
                    close_side = 'sell' if side == 'buy' else 'buy'
                    await self.exchange.place_market_order(
                        symbol=symbol,
                        side=close_side,
                        quantity=position_size['quantity']
                    )
                    return None
                logger.info(f"Stop loss order confirmed: {stop_order['id']} @ {stop_loss}")

            trade_data = {
                'strategy_id': strategy_id,
                'symbol': order['symbol'],
                'side': side,
                'entry_price': actual_entry_price,
                'quantity': position_size['quantity'],
                'entry_time': datetime.now().isoformat(),
                'status': 'open',
                'stop_loss': stop_loss,
                'take_profit': signal.take_profit,
                'fees': order.get('fee', {}).get('cost', 0) if order.get('fee') else 0,
                'metadata': {
                    **signal.metadata,
                    'position_size': position_size,
                    'order_id': order['id']
                }
            }

            trade_id = await db.save_trade(trade_data)

            position_data = {
                'strategy_id': strategy_id,
                'symbol': order['symbol'],
                'side': 'long' if side == 'buy' else 'short',
                'entry_price': trade_data['entry_price'],
                'current_price': trade_data['entry_price'],
                'quantity': position_size['quantity'],
                'stop_loss': stop_loss,
                'take_profit': signal.take_profit,
                'opened_at': datetime.now().isoformat()
            }

            await db.save_position(position_data)
            await self.risk_manager.register_position({
                'id': trade_id,
                'symbol': order['symbol'],
                'side': position_data['side'],
                'entry_price': trade_data['entry_price'],
                'quantity': position_size['quantity'],
                'position_value': position_size['position_value']
            })

            logger.info(f"Trade executed: {order['symbol']} | Size: {position_size['quantity']} | Value: ${position_size['position_value']}")
            return trade_id

        except Exception as e:
            logger.error(f"Error executing signal: {e}")
            return None

    async def close_position(self, trade_id: str, exit_price: float, exit_reason: str):
        """Close open position"""
        try:
            positions = await db.get_open_positions()
            position = next((p for p in positions if p['id'] == trade_id), None)

            if not position:
                logger.error(f"Position {trade_id} not found")
                return

            side = 'sell' if position['side'] == 'long' else 'buy'
            order = await self.exchange.place_market_order(
                symbol=position['symbol'],
                side=side,
                quantity=position['quantity']
            )

            if not order:
                logger.error("Close order execution failed")
                return

            actual_exit_price = order['average'] if order.get('average') else exit_price

            if position['side'] == 'long':
                pnl = (actual_exit_price - position['entry_price']) * position['quantity']
            else:
                pnl = (position['entry_price'] - actual_exit_price) * position['quantity']

            pnl_percent = (pnl / (position['entry_price'] * position['quantity'])) * 100

            fees = order.get('fee', {}).get('cost', 0) if order.get('fee') else 0
            pnl -= fees

            update_data = {
                'exit_price': actual_exit_price,
                'exit_time': datetime.now().isoformat(),
                'pnl': pnl,
                'pnl_percent': pnl_percent,
                'fees': fees,
                'status': 'closed',
                'exit_reason': exit_reason
            }

            await db.update_trade(trade_id, update_data)
            await db.close_position(trade_id)
            await self.risk_manager.close_position(trade_id, actual_exit_price, exit_reason)

            logger.info(f"Position closed: {position['symbol']} | PnL: ${pnl:.2f} ({pnl_percent:.2f}%) | Reason: {exit_reason}")

        except Exception as e:
            logger.error(f"Error closing position: {e}")

    async def update_stop_loss(self, trade_id: str, new_stop_loss: float):
        """Update stop loss for open position (trailing stop)"""
        try:
            await db.update_trade(trade_id, {'stop_loss': new_stop_loss})
            logger.info(f"Stop loss updated for trade {trade_id}: {new_stop_loss}")
        except Exception as e:
            logger.error(f"Error updating stop loss: {e}")

    async def monitor_positions(self, current_prices: Dict[str, float]):
        """Monitor open positions for exit conditions"""
        try:
            positions = await db.get_open_positions()

            for position in positions:
                symbol = position['symbol']
                if symbol not in current_prices:
                    continue

                current_price = current_prices[symbol]

                await db.save_position({
                    **position,
                    'current_price': current_price,
                    'unrealized_pnl': self._calculate_unrealized_pnl(position, current_price),
                    'updated_at': datetime.now().isoformat()
                })

                if self._should_exit(position, current_price):
                    exit_reason = self._get_exit_reason(position, current_price)
                    await self.close_position(position['id'], current_price, exit_reason)

        except Exception as e:
            logger.error(f"Error monitoring positions: {e}")

    def _calculate_unrealized_pnl(self, position: Dict, current_price: float) -> float:
        """Calculate unrealized PnL"""
        if position['side'] == 'long':
            return (current_price - position['entry_price']) * position['quantity']
        else:
            return (position['entry_price'] - current_price) * position['quantity']

    def _should_exit(self, position: Dict, current_price: float) -> bool:
        """Check if position should be exited"""
        if position['side'] == 'long':
            if current_price <= position['stop_loss']:
                return True
            if current_price >= position['take_profit']:
                return True
        else:
            if current_price >= position['stop_loss']:
                return True
            if current_price <= position['take_profit']:
                return True

        return False

    def _get_exit_reason(self, position: Dict, current_price: float) -> str:
        """Determine exit reason"""
        if position['side'] == 'long':
            if current_price <= position['stop_loss']:
                return "stop_loss"
            if current_price >= position['take_profit']:
                return "take_profit"
        else:
            if current_price >= position['stop_loss']:
                return "stop_loss"
            if current_price <= position['take_profit']:
                return "take_profit"

        return "unknown"
