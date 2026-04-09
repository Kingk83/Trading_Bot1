# Quick Start Guide

Get your algorithmic trading bot running in 10 minutes.

## Prerequisites

- Python 3.9+ installed
- Node.js 18+ installed
- Supabase account (database already configured)
- Exchange API keys (optional for backtesting)

## Step 1: Install Dependencies

```bash
# Install Python packages
cd trading_bot
pip install -r requirements.txt

# Install Node packages
cd ..
npm install
```

## Step 2: Configure Environment

The `.env` file is already set up with Supabase credentials. For live/paper trading, add:

```env
# Exchange Configuration (optional - not needed for backtesting)
EXCHANGE=binance
API_KEY=your_api_key
API_SECRET=your_api_secret
PAPER_TRADING=true
```

## Step 3: Initialize Database

```bash
python trading_bot/scripts/init_strategies.py
```

This creates the three default strategies in your database.

## Step 4: Run Your First Backtest

```bash
python trading_bot/scripts/run_backtest.py
```

This will:
- Download historical BTC/USDT data
- Test all 3 strategies
- Show performance metrics
- Run parameter optimization
- Perform walk-forward analysis

Expected output:
```
Testing: Trend Following
📊 Performance Summary:
   Total Trades:    45
   Win Rate:        58.00%
   Total Return:    23.50%
   Sharpe Ratio:    1.85
   Max Drawdown:    8.30%
```

## Step 5: Start the Dashboard

```bash
npm run dev
```

Open your browser to: http://localhost:5173

You'll see:
- Real-time P&L tracking
- Open positions
- Trade history
- Performance metrics
- Strategy controls

## Step 6: Paper Trading (Optional)

```bash
python trading_bot/main.py
```

The bot will:
- Connect to the exchange in paper trading mode
- Monitor configured symbols (BTC/USDT, ETH/USDT)
- Generate signals based on market conditions
- Execute simulated trades
- Track performance in real-time

## Understanding the Output

### Signal Detection
```
==================================================
SIGNAL DETECTED: TrendFollowing
Symbol: BTC/USDT
Type: BUY
Price: $42,350.00
Stop Loss: $41,850.00
Take Profit: $43,350.00
Confidence: 0.75
==================================================
```

### Trade Execution
```
Position opened: buy 0.2354 @ 42350.00
Risk: $200.00 (2.00% of capital)
Position value: $9,970.38
Stop Loss: $41,850.00 (-$117.70)
Take Profit: $43,350.00 (+$235.40)
```

### Position Management
```
Position closed: BTC/USDT | PnL: $187.25 (1.88%) | Reason: take_profit
```

## Key Metrics Explained

- **Sharpe Ratio**: Risk-adjusted returns. >1.0 is good, >2.0 is excellent
- **Win Rate**: Percentage of winning trades. 50%+ with good risk/reward is profitable
- **Profit Factor**: Gross profit / Gross loss. >1.5 is good
- **Max Drawdown**: Largest peak-to-trough decline. <15% is acceptable

## Safety Checklist

Before going live:

- [ ] Backtest shows consistent profitability (1+ year)
- [ ] Walk-forward analysis is positive
- [ ] Paper trading profitable for 30+ days
- [ ] Risk limits are working (check risk_events table)
- [ ] You understand each strategy's logic
- [ ] You're using capital you can afford to lose
- [ ] You'll monitor positions daily

## Common Commands

```bash
# Run backtest
python trading_bot/scripts/run_backtest.py

# Start paper trading
python trading_bot/main.py

# Start live trading (after testing!)
# Set PAPER_TRADING=false in .env
python trading_bot/main.py

# Start dashboard
npm run dev

# Initialize strategies
python trading_bot/scripts/init_strategies.py

# View logs
tail -f trading_bot/logs/bot.log
```

## Dashboard Features

### Main Dashboard Tab
- Total P&L
- Win rate
- Open positions count
- Sharpe ratio
- Recent trades
- Active positions

### Positions Tab
- All open positions
- Entry/current prices
- Unrealized P&L
- Stop loss and take profit levels

### Trades Tab
- Complete trade history
- Filter by status (open/closed)
- P&L breakdown
- Entry/exit details

### Performance Tab
- Comprehensive metrics
- Win/loss statistics
- Average trade analysis
- Profit factor

### Strategies Tab
- Enable/disable strategies
- View parameters
- System configuration
- Risk limits

## Troubleshooting

### "Module not found" error
```bash
pip install -r trading_bot/requirements.txt
```

### Dashboard won't load
```bash
npm install
npm run dev
```

### No signals generated
- Markets may not be suitable for strategies
- Check logs: `tail -f trading_bot/logs/bot.log`
- Verify strategies are enabled in database

### API connection failed
- Check API keys in `.env`
- Verify exchange API permissions
- Try paper trading mode first

## Next Steps

1. **Study the Strategies**: Review code in `trading_bot/strategies/`
2. **Optimize Parameters**: Use the optimizer to find best settings
3. **Test Different Timeframes**: Try 15m, 1h, 4h timeframes
4. **Add New Symbols**: Edit TRADING_SYMBOLS in config.py
5. **Create Custom Strategies**: Extend BaseStrategy class

## Learning Resources

- **Technical Analysis**: Study EMA, RSI, MACD, Bollinger Bands
- **Risk Management**: Understanding position sizing and drawdowns
- **Backtesting**: Avoiding overfitting and curve-fitting
- **Market Regimes**: Trending vs ranging market identification

## Support

- Check README.md for detailed documentation
- Review strategy code for implementation details
- Test thoroughly before live trading
- Start with small capital

---

**Remember: Trading is risky. Start small. Test thoroughly. Never risk money you can't afford to lose.**
