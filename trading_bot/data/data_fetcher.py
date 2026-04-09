"""
Data Fetcher
Real-time and historical market data retrieval
"""

import asyncio
import ccxt
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from config import Config
from utils.logger import logger
from utils.database import db

class DataFetcher:
    def __init__(self):
        self.exchange = self._initialize_exchange()
        self.cache: Dict[str, pd.DataFrame] = {}

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
                logger.info("Running in PAPER TRADING mode (spot market data)")

            return exchange
        except Exception as e:
            logger.error(f"Failed to initialize exchange: {e}")
            raise

    async def fetch_ohlcv(self, symbol: str, timeframe: str = '15m', limit: int = 500) -> pd.DataFrame:
        """Fetch OHLCV data from exchange"""
        try:
            cache_key = f"{symbol}_{timeframe}"

            ohlcv = await asyncio.to_thread(
                self.exchange.fetch_ohlcv, symbol, timeframe, None, limit
            )

            df = pd.DataFrame(
                ohlcv,
                columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
            )
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)

            self.cache[cache_key] = df

            await self._save_to_database(symbol, timeframe, df)

            logger.debug(f"Fetched {len(df)} candles for {symbol} {timeframe}")
            return df

        except Exception as e:
            logger.error(f"Error fetching OHLCV data for {symbol}: {e}")
            return pd.DataFrame()

    async def _save_to_database(self, symbol: str, timeframe: str, df: pd.DataFrame):
        """Save candle data to database"""
        try:
            records = []
            for timestamp, row in df.iterrows():
                records.append({
                    'symbol': symbol,
                    'timeframe': timeframe,
                    'timestamp': timestamp.isoformat(),
                    'open': float(row['open']),
                    'high': float(row['high']),
                    'low': float(row['low']),
                    'close': float(row['close']),
                    'volume': float(row['volume'])
                })

            if records:
                await db.save_market_data(records)

        except Exception as e:
            logger.error(f"Error saving market data: {e}")

    async def fetch_ticker(self, symbol: str) -> Optional[Dict]:
        """Fetch current ticker data"""
        try:
            ticker = await asyncio.to_thread(self.exchange.fetch_ticker, symbol)
            return ticker
        except Exception as e:
            logger.error(f"Error fetching ticker for {symbol}: {e}")
            return None

    async def fetch_orderbook(self, symbol: str, limit: int = 20) -> Optional[Dict]:
        """Fetch order book"""
        try:
            orderbook = await asyncio.to_thread(self.exchange.fetch_order_book, symbol, limit)
            return orderbook
        except Exception as e:
            logger.error(f"Error fetching orderbook for {symbol}: {e}")
            return None

    async def fetch_account_balance(self) -> Optional[Dict]:
        """Fetch account balance"""
        try:
            balance = await asyncio.to_thread(self.exchange.fetch_balance)
            return balance
        except Exception as e:
            logger.error(f"Error fetching balance: {e}")
            return None

    def get_cached_data(self, symbol: str, timeframe: str) -> Optional[pd.DataFrame]:
        """Get cached OHLCV data"""
        cache_key = f"{symbol}_{timeframe}"
        return self.cache.get(cache_key)

    async def fetch_multiple_timeframes(self, symbol: str, timeframes: List[str]) -> Dict[str, pd.DataFrame]:
        """Fetch data for multiple timeframes"""
        data = {}
        for tf in timeframes:
            df = await self.fetch_ohlcv(symbol, tf)
            if not df.empty:
                data[tf] = df
        return data

    def calculate_volatility(self, df: pd.DataFrame, period: int = 20) -> float:
        """Calculate historical volatility"""
        returns = df['close'].pct_change()
        volatility = returns.rolling(window=period).std().iloc[-1]
        return volatility * 100

    async def fetch_historical_data(self, symbol: str, timeframe: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Fetch historical data for backtesting"""
        try:
            all_data = []
            current = start_date

            while current < end_date:
                since = int(current.timestamp() * 1000)
                ohlcv = await asyncio.to_thread(
                    self.exchange.fetch_ohlcv, symbol, timeframe, since, 1000
                )

                if not ohlcv:
                    break

                all_data.extend(ohlcv)
                current = datetime.fromtimestamp(ohlcv[-1][0] / 1000) + timedelta(minutes=1)

            df = pd.DataFrame(
                all_data,
                columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
            )
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            df = df[~df.index.duplicated(keep='first')]

            logger.info(f"Fetched {len(df)} historical candles for {symbol}")
            return df

        except Exception as e:
            logger.error(f"Error fetching historical data: {e}")
            return pd.DataFrame()
