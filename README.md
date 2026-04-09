# AlgoTrader Pro - Institutional-Grade Algorithmic Trading System

A professional, production-ready algorithmic trading bot designed for crypto markets with institutional-grade architecture, risk management, and monitoring capabilities.

## System Overview

This is a complete trading system built with:
- **Python Backend**: Core trading logic, strategies, risk management, and execution
- **React Dashboard**: Real-time monitoring and control interface
- **Supabase Database**: Trade persistence and performance analytics
- **Multi-Exchange Support**: Binance, Bybit, Coinbase via CCXT

## Key Features

### Trading Strategies
1. **Trend Following**: EMA crossover with MACD confirmation
2. **Mean Reversion**: RSI and Bollinger Bands based entries
3. **Breakout**: Volume-confirmed price breakouts

### Risk Management
- Max 1-2% risk per trade
- Daily drawdown limits (5%)
- Position size limits
- Minimum 1:2 risk/reward ratio
- Volatility-adjusted position sizing

### Advanced Features
- Multi-timeframe analysis
- Market regime detection
- Dynamic strategy activation
- Walk-forward optimization
- Monte Carlo simulation
- Real-time monitoring dashboard

## Project Structure

```
trading_bot/
├── data/                      # Data fetching and processing
│   ├── data_fetcher.py       # Exchange data retrieval
│   └── data_processor.py     # Technical indicator calculation
├── strategies/                # Trading strategies
│   ├── base_strategy.py      # Strategy base class
│   ├── trend_following.py    # Trend following strategy
│   ├── mean_reversion.py     # Mean reversion strategy
│   └── breakout.py           # Breakout strategy
├── execution/                 # Order execution
│   ├── exchange_interface.py # Exchange API wrapper
│   └── order_manager.py      # Order lifecycle management
├── risk/                      # Risk management
│   ├── risk_manager.py       # Risk controls
│   └── position_sizer.py     # Position sizing
├── backtesting/              # Backtesting engine
│   ├── backtest_engine.py    # Historical testing
│   └── performance_metrics.py # Performance calculations
├── optimization/              # Strategy optimization
│   └── optimizer.py          # Parameter optimization
├── advanced/                  # Advanced features
│   ├── regime_detector.py    # Market regime detection
│   └── multi_timeframe.py    # Multi-timeframe analysis
├── utils/                     # Utilities
│   ├── database.py           # Supabase integration
│   ├── indicators.py         # Technical indicators
│   └── logger.py             # Logging system
├── config.py                  # Configuration
└── main.py                    # Main orchestrator

src/                           # React Dashboard
├── components/                # UI components
│   ├── Dashboard.tsx         # Main dashboard
│   ├── PositionsTable.tsx    # Positions view
│   ├── TradesTable.tsx       # Trade history
│   ├── PerformanceChart.tsx  # Performance metrics
│   └── StrategyControls.tsx  # Strategy management
└── App.tsx                    # Main application
```

## Installation

### Prerequisites
- Python 3.9+
- Node.js 18+
- Supabase account (for database)
- Exchange API keys (for live trading)

### Setup Steps

1. **Install Python Dependencies**
```bash
cd trading_bot
pip install -r requirements.txt
```

2. **Configure Environment Variables**
Create a `.env` file in the project root:
```env
# Supabase Configuration (already configured)
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key

# Exchange API Keys
EXCHANGE=binance
API_KEY=your_api_key
API_SECRET=your_api_secret

# Trading Configuration
PAPER_TRADING=true
INITIAL_CAPITAL=10000
TRADING_SYMBOLS=BTC/USDT,ETH/USDT
```

3. **Install Frontend Dependencies**
```bash
npm install
```

4. **Initialize Database**
The database schema is already created in Supabase. Initialize strategies:
```bash
python trading_bot/scripts/init_strategies.py
```

## Running the System

### 1. Run Backtest
Test strategies on historical data:
```bash
python trading_bot/main.py backtest
```

### 2. Paper Trading
Test with live data but simulated execution:
```bash
# Set PAPER_TRADING=true in .env
python trading_bot/main.py
```

### 3. Live Trading
**WARNING: Only use with real capital after thorough testing**
```bash
# Set PAPER_TRADING=false in .env
python trading_bot/main.py
```

### 4. Start Monitoring Dashboard
```bash
npm run dev
```
Access dashboard at: http://localhost:5173

## Configuration

### Risk Parameters
Edit `trading_bot/config.py`:
```python
MAX_RISK_PER_TRADE = 0.02      # 2% per trade
MAX_DAILY_DRAWDOWN = 0.05      # 5% daily limit
MAX_OPEN_POSITIONS = 5
MIN_RISK_REWARD_RATIO = 2.0
```

### Strategy Parameters
Each strategy has configurable parameters in its class:

**Trend Following:**
- fast_ema: 12
- slow_ema: 26
- atr_period: 14
- adx_threshold: 25

**Mean Reversion:**
- rsi_period: 14
- bb_period: 20
- bb_std: 2

**Breakout:**
- lookback_period: 20
- volume_multiplier: 1.5
- atr_period: 14

## Strategy Details

### 1. Trend Following Strategy

**Entry (Long):**
- Fast EMA crosses above Slow EMA
- MACD line crosses above signal line
- ADX > 25 (strong trend)
- Price above both EMAs

**Exit:**
- Stop Loss: 2 x ATR below entry
- Take Profit: 4 x ATR above entry
- Signal reversal

**Best Market Conditions:** Strong trending markets

### 2. Mean Reversion Strategy

**Entry (Long):**
- RSI < 30 (oversold)
- Price touches lower Bollinger Band
- Volume confirmation
- ADX < 25 (ranging market)

**Exit:**
- Stop Loss: Below recent swing low
- Take Profit: Middle Bollinger Band or RSI > 70
- Momentum reversal

**Best Market Conditions:** Ranging, sideways markets

### 3. Breakout Strategy

**Entry (Long):**
- Price breaks above 20-period high
- Volume > 1.5x average
- ATR expanding
- Preceded by consolidation

**Exit:**
- Stop Loss: Below consolidation range
- Take Profit: 2x consolidation range
- Volume exhaustion

**Best Market Conditions:** Volatile, trending markets after consolidation

## Performance Metrics

The system tracks comprehensive metrics:

- **Sharpe Ratio**: Risk-adjusted returns
- **Sortino Ratio**: Downside risk-adjusted returns
- **Win Rate**: Percentage of profitable trades
- **Profit Factor**: Gross profit / Gross loss
- **Max Drawdown**: Largest peak-to-trough decline
- **Expectancy**: Average profit per trade

## Risk Management System

### Position Sizing
Positions are sized based on:
1. Account risk (1-2% of capital)
2. Stop loss distance
3. Volatility (ATR-based adjustment)

Example:
```
Account: $10,000
Risk: 2% = $200
Entry: $50,000
Stop Loss: $49,000
Risk per unit: $1,000
Position Size: $200 / $1,000 = 0.2 BTC
```

### Daily Limits
- Maximum 5% daily drawdown
- Trading stops if limit hit
- Resets at start of new trading day

### Correlation Control
- Prevents highly correlated positions
- Example: Won't open ETH/USDT if BTC/USDT already open

## Optimization

### Grid Search
Test all parameter combinations:
```python
from optimization.optimizer import StrategyOptimizer

optimizer = StrategyOptimizer(strategy)
results = optimizer.grid_search(df, {
    'fast_ema': [10, 12, 15],
    'slow_ema': [20, 26, 30],
    'atr_multiplier': [1.5, 2.0, 2.5]
})
```

### Walk-Forward Analysis
Out-of-sample validation:
```python
wf_results = optimizer.walk_forward_analysis(
    df,
    param_grid,
    train_size=252,  # 1 year training
    test_size=63     # 3 months testing
)
```

### Monte Carlo Simulation
Robustness testing:
```python
mc_results = optimizer.monte_carlo_simulation(
    trades,
    n_simulations=1000
)
```

## Deployment

### Local VPS
1. Use screen or tmux for persistent sessions
2. Setup systemd service for auto-restart
3. Configure log rotation
4. Monitor with dashboard

### Cloud Deployment
Recommended platforms:
- **AWS EC2**: t3.medium or larger
- **Google Cloud**: e2-medium or larger
- **DigitalOcean**: $24/month droplet

Setup:
```bash
# Install dependencies
sudo apt update
sudo apt install python3.9 python3-pip nginx

# Setup firewall
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443

# Run bot as service
sudo systemctl enable trading-bot
sudo systemctl start trading-bot
```

## Monitoring

### Dashboard Features
- Real-time P&L tracking
- Open positions monitoring
- Trade history
- Performance metrics
- Strategy controls
- Risk event alerts

### Logging
Logs are written to `trading_bot/logs/`:
- `bot.log`: General operations
- `errors.log`: Errors and exceptions
- `trades.log`: Trade executions

## Safety Guidelines

### Before Live Trading
1. ✅ Run extensive backtests (1+ years of data)
2. ✅ Paper trade for 30+ days
3. ✅ Verify all risk limits work
4. ✅ Test with minimum capital first
5. ✅ Monitor daily for first week

### Risk Warnings
- **Past performance ≠ future results**
- **Use only risk capital you can afford to lose**
- **Start small and scale gradually**
- **Monitor positions daily**
- **Have emergency stop procedures**

## Scaling to Hedge Fund Level

### Infrastructure Improvements
1. **High-Frequency Data**: WebSocket feeds, tick data
2. **Low Latency**: Co-location, direct market access
3. **Multi-Strategy**: Portfolio of uncorrelated strategies
4. **Risk System**: Real-time VAR, stress testing
5. **Compliance**: Trade surveillance, audit trails

### Operational Enhancements
1. **Team Structure**: PM, Quant, Dev, Risk, Ops
2. **Research Platform**: Jupyter, Quantopian-like environment
3. **Execution**: Smart order routing, algos
4. **Reporting**: Investor reports, performance attribution
5. **Infrastructure**: Kubernetes, microservices, monitoring

### Capital Scaling
- $100K: Retail setup (current)
- $1M: Professional setup (dedicated servers)
- $10M: Fund setup (team, infrastructure)
- $100M+: Institutional setup (full stack)

## Troubleshooting

### Common Issues

**"Insufficient data for backtest"**
- Increase LOOKBACK_PERIODS in config
- Check exchange API limits

**"Trading not allowed due to risk limits"**
- Daily drawdown limit hit
- Reset occurs at new trading day
- Check risk_events table

**"No signals generated"**
- Market regime not suitable for strategies
- Adjust strategy parameters
- Check market conditions

**"Order execution failed"**
- Verify API keys and permissions
- Check exchange status
- Verify account balance

## Support & Resources

### Documentation
- CCXT Documentation: https://docs.ccxt.com
- Supabase Docs: https://supabase.com/docs
- Technical Analysis: https://www.investopedia.com

### Community
- Join discussions on strategy improvements
- Share backtest results
- Report bugs and issues

## License

Professional/Commercial Use - Customize for your needs

## Disclaimer

This software is for educational purposes. Trading carries significant risk of loss. The developers assume no liability for trading losses. Always test thoroughly before live trading. Never trade with money you cannot afford to lose.

---

**Built with precision. Trade with discipline.**
