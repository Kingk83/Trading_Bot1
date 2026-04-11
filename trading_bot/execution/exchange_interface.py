"""
Exchange Interface
Handle exchange communication for order execution
"""

import asyncio
import uuid
import ccxt
from typing import Dict, Optional
from ..config import Config
from ..utils.logger import logger

class ExchangeInterface:
    def __init__(self):
        self.exchange = self._initialize_exchange()
        self._paper_orders: Dict[str, Dict] = {}

    def _initialize_exchange(self) -> ccxt.Exchange:
        """Initialize exchange connection"""
        try:
            exchange_class = getattr(ccxt, Config.EXCHANGE)
            params = {
                'enableRateLimit': True,
                'options': {'defaultType': 'spot'}
            }
            if not Config.PAPER_TRADING:
                params['apiKey'] = Config.API_KEY
                params['secret'] = Config.API_SECRET
            exchange = exchange_class(params)

            if Config.PAPER_TRADING:
                logger.info("Exchange initialized in PAPER TRADING mode (simulated execution)")

            return exchange
        except Exception as e:
            logger.error(f"Failed to initialize exchange: {e}")
            raise

    def _simulate_order(self, symbol: str, side: str, quantity: float, price: float = None) -> Dict:
        """Simulate an order fill for paper trading"""
        order_id = str(uuid.uuid4())
        order = {
            'id': order_id,
            'symbol': symbol,
            'side': side,
            'type': 'market',
            'quantity': quantity,
            'amount': quantity,
            'average': price,
            'price': price,
            'status': 'closed',
            'filled': quantity,
            'fee': {'cost': quantity * (price or 0) * Config.COMMISSION, 'currency': 'USDT'}
        }
        self._paper_orders[order_id] = order
        return order

    _API_TIMEOUT = 30

    async def _with_timeout(self, coro):
        return await asyncio.wait_for(coro, timeout=self._API_TIMEOUT)

    async def _get_current_price(self, symbol: str) -> Optional[float]:
        """Get current market price"""
        try:
            ticker = await self._with_timeout(asyncio.to_thread(self.exchange.fetch_ticker, symbol))
            price = ticker.get('last') or ticker.get('close')
            if not price or price <= 0:
                logger.error(f"Invalid price received for {symbol}: {price}")
                return None
            return float(price)
        except asyncio.TimeoutError:
            logger.error(f"Timeout fetching price for {symbol}")
            return None
        except Exception as e:
            logger.error(f"Error fetching price for {symbol}: {e}")
            return None

    async def place_market_order(self, symbol: str, side: str, quantity: float) -> Optional[Dict]:
        """Place market order"""
        try:
            logger.info(f"Placing {side} market order: {quantity} {symbol}")

            if Config.PAPER_TRADING:
                current_price = await self._get_current_price(symbol)
                if current_price is None:
                    logger.error(f"Cannot place paper order for {symbol}: price unavailable")
                    return None
                order = self._simulate_order(symbol, side, quantity, current_price)
                logger.info(f"Paper order simulated: {order['id']} @ ${current_price:.4f}")
                return order

            order = await self._with_timeout(asyncio.to_thread(
                self.exchange.create_market_order,
                symbol, side, quantity
            ))
            logger.info(f"Order executed: {order['id']}")
            return order

        except asyncio.TimeoutError:
            logger.error(f"Timeout placing market order for {symbol}")
            return None
        except Exception as e:
            logger.error(f"Error placing market order: {e}")
            return None

    async def place_limit_order(self, symbol: str, side: str, quantity: float, price: float) -> Optional[Dict]:
        """Place limit order"""
        try:
            logger.info(f"Placing {side} limit order: {quantity} {symbol} @ {price}")

            if Config.PAPER_TRADING:
                order = self._simulate_order(symbol, side, quantity, price)
                return order

            order = await self._with_timeout(asyncio.to_thread(
                self.exchange.create_limit_order,
                symbol, side, quantity, price
            ))
            logger.info(f"Limit order placed: {order['id']}")
            return order

        except asyncio.TimeoutError:
            logger.error(f"Timeout placing limit order for {symbol}")
            return None
        except Exception as e:
            logger.error(f"Error placing limit order: {e}")
            return None

    async def place_stop_loss_order(self, symbol: str, side: str, quantity: float, stop_price: float) -> Optional[Dict]:
        """Place stop loss order"""
        try:
            order_side = 'sell' if side == 'long' else 'buy'

            if Config.PAPER_TRADING:
                order = self._simulate_order(symbol, order_side, quantity, stop_price)
                return order

            order = await self._with_timeout(asyncio.to_thread(
                self.exchange.create_order,
                symbol, 'stop_market', order_side, quantity,
                None, {'stopPrice': stop_price}
            ))
            logger.info(f"Stop loss order placed: {order['id']}")
            return order

        except asyncio.TimeoutError:
            logger.error(f"Timeout placing stop loss order for {symbol}")
            return None
        except Exception as e:
            logger.error(f"Error placing stop loss order: {e}")
            return None

    async def cancel_order(self, order_id: str, symbol: str) -> bool:
        """Cancel order"""
        try:
            if Config.PAPER_TRADING:
                self._paper_orders.pop(order_id, None)
                return True

            await self._with_timeout(asyncio.to_thread(self.exchange.cancel_order, order_id, symbol))
            logger.info(f"Order cancelled: {order_id}")
            return True
        except asyncio.TimeoutError:
            logger.error(f"Timeout cancelling order {order_id}")
            return False
        except Exception as e:
            logger.error(f"Error cancelling order: {e}")
            return False

    async def get_order_status(self, order_id: str, symbol: str) -> Optional[Dict]:
        """Get order status"""
        try:
            if Config.PAPER_TRADING:
                return self._paper_orders.get(order_id)

            order = await self._with_timeout(asyncio.to_thread(self.exchange.fetch_order, order_id, symbol))
            return order
        except asyncio.TimeoutError:
            logger.error(f"Timeout fetching order status for {order_id}")
            return None
        except Exception as e:
            logger.error(f"Error fetching order status: {e}")
            return None

    async def get_balance(self) -> Optional[Dict]:
        """Get account balance"""
        try:
            if Config.PAPER_TRADING:
                return {'USDT': {'free': Config.INITIAL_CAPITAL, 'total': Config.INITIAL_CAPITAL}}

            balance = await self._with_timeout(asyncio.to_thread(self.exchange.fetch_balance))
            return balance
        except asyncio.TimeoutError:
            logger.error("Timeout fetching account balance")
            return None
        except Exception as e:
            logger.error(f"Error fetching balance: {e}")
            return None

    async def get_positions(self) -> Optional[list]:
        """Get open positions"""
        try:
            if Config.PAPER_TRADING:
                return []

            positions = await self._with_timeout(asyncio.to_thread(self.exchange.fetch_positions))
            return [p for p in positions if float(p.get('contracts', 0)) > 0]
        except asyncio.TimeoutError:
            logger.error("Timeout fetching positions")
            return None
        except Exception as e:
            logger.error(f"Error fetching positions: {e}")
            return None
