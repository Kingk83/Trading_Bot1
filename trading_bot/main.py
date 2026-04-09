"""
Main Trading Bot Orchestrator
Entry point for running the algorithmic trading system
"""

import asyncio
import pandas as pd
from datetime import datetime
from typing import List, Dict

from config import Config
from data.data_fetcher import DataFetcher
from data.data_processor import DataProcessor
from strategies.trend_following import TrendFollowingStrategy
from strategies.mean_reversion import MeanReversionStrategy
from strategies.breakout import BreakoutStrategy
from execution.order_manager import OrderManager
from risk.risk_manager import RiskManager
from risk.position_sizer import PositionSizer
from advanced.regime_detector import RegimeDetector
from advanced.multi_timeframe import MultiTimeframeAnalyzer
from utils.database import db
from utils.logger import logger

class TradingBot:
    """
    Main trading bot orchestrator
    Coordinates all system components
    """

    def __init__(self):
        logger.info("=" * 50)
        logger.info("Initializing AlgoTrader Pro")
        logger.info("=" * 50)

        self.data_fetcher = DataFetcher()
        self.risk_manager = RiskManager(Config.INITIAL_CAPITAL)
        self.position_sizer = PositionSizer(Config.INITIAL_CAPITAL)
        self.order_manager = OrderManager(self.risk_manager, self.position_sizer)

        self.strategies = self._initialize_strategies()
        self.strategy_type_map = {
            'TrendFollowing': 'trend_following',
            'MeanReversion': 'mean_reversion',
            'Breakout': 'breakout',
        }
        self.regime_detector = RegimeDetector()
        self.mtf_analyzer = MultiTimeframeAnalyzer(['15m', '1h', '4h'])

        self.symbols = Config.TRADING_SYMBOLS
        self.running = False

        logger.info(f"Trading Mode: {'PAPER TRADING' if Config.PAPER_TRADING else 'LIVE TRADING'}")
        logger.info(f"Initial Capital: ${Config.INITIAL_CAPITAL:,.2f}")
        logger.info(f"Trading Symbols: {', '.join(self.symbols)}")
        logger.info(f"Active Strategies: {len(self.strategies)}")

    def _initialize_strategies(self) -> List:
        """Initialize trading strategies"""
        strategies = [
            TrendFollowingStrategy(),
            MeanReversionStrategy(),
            BreakoutStrategy()
        ]

        for strategy in strategies:
            logger.info(f"Loaded strategy: {strategy.name}")

        return strategies

    async def start(self):
        """Start the trading bot"""
        logger.info("\n" + "=" * 50)
        logger.info("Starting Trading Bot")
        logger.info("=" * 50 + "\n")

        self.running = True

        try:
            await self._main_loop()
        except KeyboardInterrupt:
            logger.info("Shutdown signal received")
            await self.stop()
        except Exception as e:
            logger.error(f"Critical error: {e}")
            await self.stop()

    async def _main_loop(self):
        """Main trading loop"""
        while self.running:
            try:
                for symbol in self.symbols:
                    await self._process_symbol(symbol)

                await self._monitor_positions()

                await asyncio.sleep(Config.SCAN_INTERVAL)

            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                await asyncio.sleep(60)

    async def _process_symbol(self, symbol: str):
        """Process trading signals for a symbol"""
        try:
            logger.info(f"Scanning {symbol} on {Config.TIMEFRAME}...")
            df = await asyncio.wait_for(
                self.data_fetcher.fetch_ohlcv(symbol, Config.TIMEFRAME, Config.LOOKBACK_PERIODS),
                timeout=15
            )

            if df is None or len(df) < 100:
                return

            df = DataProcessor.clean_data(df)

            regime = self.regime_detector.detect_regime(df)
            regime_chars = self.regime_detector.get_regime_characteristics(regime)

            logger.info(f"{symbol} | Regime: {regime} | Best strategies: {regime_chars['best_strategies']}")

            for strategy in self.strategies:
                if not await self._is_strategy_enabled(strategy.name):
                    continue

                strategy_type = self.strategy_type_map.get(strategy.name, strategy.name.lower())
                if not self.regime_detector.should_trade_in_regime(regime, strategy_type):
                    logger.info(f"Skipping {strategy.name} ({strategy_type}) - not suitable for {regime} regime")
                    continue

                if not self.risk_manager.is_trading_allowed():
                    logger.warning("Trading not allowed due to risk limits")
                    break

                signal = strategy.generate_signal(df)

                if signal and strategy.validate_signal(signal, df):
                    logger.info(f"\n{'='*50}")
                    logger.info(f"SIGNAL DETECTED: {strategy.name}")
                    logger.info(f"Symbol: {symbol}")
                    logger.info(f"Type: {signal.type.value.upper()}")
                    logger.info(f"Price: ${signal.price:.2f}")
                    logger.info(f"Stop Loss: ${signal.stop_loss:.2f}")
                    logger.info(f"Take Profit: ${signal.take_profit:.2f}")
                    logger.info(f"Confidence: {signal.confidence:.2%}")
                    logger.info(f"{'='*50}\n")

                    strategy_db = await db.get_strategy(strategy.name)
                    if strategy_db:
                        signal.metadata['symbol'] = symbol
                        await self.order_manager.execute_signal(signal, strategy_db['id'], df)

        except Exception as e:
            logger.error(f"Error processing {symbol}: {e}")

    async def _monitor_positions(self):
        """Monitor and manage open positions"""
        try:
            current_prices = {}
            for symbol in self.symbols:
                ticker = await self.data_fetcher.fetch_ticker(symbol)
                if ticker:
                    current_prices[symbol] = ticker['last']

            await self.order_manager.monitor_positions(current_prices)

        except Exception as e:
            logger.error(f"Error monitoring positions: {e}")

    async def _is_strategy_enabled(self, strategy_name: str) -> bool:
        """Check if strategy is enabled in database"""
        strategy = await db.get_strategy(strategy_name)
        return strategy and strategy.get('enabled', False)

    async def stop(self):
        """Stop the trading bot"""
        logger.info("\n" + "=" * 50)
        logger.info("Stopping Trading Bot")
        logger.info("=" * 50)

        self.running = False

        risk_metrics = self.risk_manager.get_risk_metrics()
        logger.info(f"\nFinal Statistics:")
        logger.info(f"Final Capital: ${risk_metrics['current_capital']:,.2f}")
        logger.info(f"Total Return: {risk_metrics['total_return']:.2f}%")
        logger.info(f"Open Positions: {risk_metrics['open_positions']}")

        logger.info("\nBot stopped successfully")

    async def run_backtest(self, symbol: str, start_date: str, end_date: str):
        """Run backtest on historical data"""
        from backtesting.backtest_engine import BacktestEngine

        logger.info(f"\nRunning backtest: {symbol} from {start_date} to {end_date}")

        from datetime import datetime as dt
        df = await self.data_fetcher.fetch_historical_data(symbol, Config.TIMEFRAME, dt.fromisoformat(start_date), dt.fromisoformat(end_date))

        if df is None or len(df) < 100:
            logger.error("Insufficient data for backtest")
            return

        for strategy in self.strategies:
            logger.info(f"\n{'='*50}")
            logger.info(f"Backtesting: {strategy.name}")
            logger.info(f"{'='*50}")

            backtest = BacktestEngine(
                strategy=strategy,
                initial_capital=Config.INITIAL_CAPITAL,
                commission=Config.COMMISSION,
                slippage=Config.SLIPPAGE
            )

            result = backtest.run(df, symbol)

            logger.info(f"\nResults:")
            logger.info(f"Total Trades: {result['metrics']['total_trades']}")
            logger.info(f"Win Rate: {result['metrics']['win_rate']:.2f}%")
            logger.info(f"Total Return: {result['metrics']['total_return']:.2f}%")
            logger.info(f"Sharpe Ratio: {result['metrics']['sharpe_ratio']:.2f}")
            logger.info(f"Max Drawdown: {result['metrics']['max_drawdown_pct']:.2f}%")
            logger.info(f"Profit Factor: {result['metrics']['profit_factor']:.2f}")

            await db.save_backtest_result({
                'strategy_name': strategy.name,
                'parameters': strategy.get_parameters(),
                'start_date': start_date,
                'end_date': end_date,
                'initial_capital': Config.INITIAL_CAPITAL,
                'final_capital': result['metrics']['final_capital'],
                'total_return': result['metrics']['total_return'],
                'sharpe_ratio': result['metrics']['sharpe_ratio'],
                'max_drawdown': result['metrics']['max_drawdown_pct'],
                'win_rate': result['metrics']['win_rate'],
                'profit_factor': result['metrics']['profit_factor'],
                'total_trades': result['metrics']['total_trades'],
                'metrics': result['metrics']
            })

async def main():
    """Main entry point"""
    bot = TradingBot()

    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'backtest':
        await bot.run_backtest(
            symbol='BTC/USDT',
            start_date='2024-01-01',
            end_date='2024-12-31'
        )
    else:
        await bot.start()

if __name__ == "__main__":
    asyncio.run(main())
