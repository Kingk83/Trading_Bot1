/*
  # Algorithmic Trading System Database Schema
  
  ## Overview
  Complete database schema for institutional-grade algorithmic trading system
  supporting multiple strategies, risk management, and performance tracking.
  
  ## Tables Created
  
  1. **strategies**
     - id (uuid, primary key)
     - name (text) - Strategy identifier
     - type (text) - Strategy type (trend_following, mean_reversion, breakout)
     - parameters (jsonb) - Strategy parameters
     - enabled (boolean) - Active status
     - created_at (timestamptz)
     - updated_at (timestamptz)
  
  2. **trades**
     - id (uuid, primary key)
     - strategy_id (uuid, foreign key)
     - symbol (text) - Trading pair (e.g., BTC/USDT)
     - side (text) - buy or sell
     - entry_price (numeric)
     - exit_price (numeric)
     - quantity (numeric)
     - entry_time (timestamptz)
     - exit_time (timestamptz)
     - pnl (numeric) - Profit/loss
     - pnl_percent (numeric)
     - fees (numeric)
     - status (text) - open, closed, cancelled
     - stop_loss (numeric)
     - take_profit (numeric)
     - exit_reason (text)
     - metadata (jsonb)
  
  3. **positions**
     - id (uuid, primary key)
     - strategy_id (uuid, foreign key)
     - symbol (text)
     - side (text)
     - entry_price (numeric)
     - current_price (numeric)
     - quantity (numeric)
     - unrealized_pnl (numeric)
     - stop_loss (numeric)
     - take_profit (numeric)
     - opened_at (timestamptz)
     - updated_at (timestamptz)
  
  4. **performance_metrics**
     - id (uuid, primary key)
     - strategy_id (uuid, foreign key)
     - date (date)
     - total_trades (integer)
     - winning_trades (integer)
     - losing_trades (integer)
     - win_rate (numeric)
     - total_pnl (numeric)
     - sharpe_ratio (numeric)
     - max_drawdown (numeric)
     - profit_factor (numeric)
     - avg_win (numeric)
     - avg_loss (numeric)
     - largest_win (numeric)
     - largest_loss (numeric)
     - total_fees (numeric)
     - created_at (timestamptz)
  
  5. **risk_events**
     - id (uuid, primary key)
     - event_type (text) - drawdown_limit, position_limit, etc.
     - severity (text) - warning, critical
     - message (text)
     - data (jsonb)
     - resolved (boolean)
     - created_at (timestamptz)
  
  6. **market_data**
     - id (uuid, primary key)
     - symbol (text)
     - timeframe (text) - 1m, 5m, 15m, 1h, 4h, 1d
     - timestamp (timestamptz)
     - open (numeric)
     - high (numeric)
     - low (numeric)
     - close (numeric)
     - volume (numeric)
     - UNIQUE(symbol, timeframe, timestamp)
  
  7. **backtest_results**
     - id (uuid, primary key)
     - strategy_name (text)
     - parameters (jsonb)
     - start_date (timestamptz)
     - end_date (timestamptz)
     - initial_capital (numeric)
     - final_capital (numeric)
     - total_return (numeric)
     - sharpe_ratio (numeric)
     - max_drawdown (numeric)
     - win_rate (numeric)
     - profit_factor (numeric)
     - total_trades (integer)
     - metrics (jsonb)
     - created_at (timestamptz)
  
  8. **system_config**
     - id (uuid, primary key)
     - key (text, unique)
     - value (jsonb)
     - description (text)
     - updated_at (timestamptz)
  
  ## Security
  - RLS enabled on all tables
  - Policies for authenticated access
  
  ## Indexes
  - Performance indexes on frequently queried columns
  - Composite indexes for common query patterns
*/

-- Create strategies table
CREATE TABLE IF NOT EXISTS strategies (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text UNIQUE NOT NULL,
  type text NOT NULL CHECK (type IN ('trend_following', 'mean_reversion', 'breakout')),
  parameters jsonb NOT NULL DEFAULT '{}',
  enabled boolean DEFAULT true,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Create trades table
CREATE TABLE IF NOT EXISTS trades (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  strategy_id uuid REFERENCES strategies(id) ON DELETE SET NULL,
  symbol text NOT NULL,
  side text NOT NULL CHECK (side IN ('buy', 'sell')),
  entry_price numeric NOT NULL,
  exit_price numeric,
  quantity numeric NOT NULL,
  entry_time timestamptz DEFAULT now(),
  exit_time timestamptz,
  pnl numeric,
  pnl_percent numeric,
  fees numeric DEFAULT 0,
  status text NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'closed', 'cancelled')),
  stop_loss numeric,
  take_profit numeric,
  exit_reason text,
  metadata jsonb DEFAULT '{}'
);

-- Create positions table
CREATE TABLE IF NOT EXISTS positions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  strategy_id uuid REFERENCES strategies(id) ON DELETE CASCADE,
  symbol text NOT NULL,
  side text NOT NULL CHECK (side IN ('long', 'short')),
  entry_price numeric NOT NULL,
  current_price numeric NOT NULL,
  quantity numeric NOT NULL,
  unrealized_pnl numeric DEFAULT 0,
  stop_loss numeric,
  take_profit numeric,
  opened_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now(),
  UNIQUE(strategy_id, symbol)
);

-- Create performance_metrics table
CREATE TABLE IF NOT EXISTS performance_metrics (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  strategy_id uuid REFERENCES strategies(id) ON DELETE CASCADE,
  date date NOT NULL,
  total_trades integer DEFAULT 0,
  winning_trades integer DEFAULT 0,
  losing_trades integer DEFAULT 0,
  win_rate numeric,
  total_pnl numeric DEFAULT 0,
  sharpe_ratio numeric,
  max_drawdown numeric,
  profit_factor numeric,
  avg_win numeric,
  avg_loss numeric,
  largest_win numeric,
  largest_loss numeric,
  total_fees numeric DEFAULT 0,
  created_at timestamptz DEFAULT now(),
  UNIQUE(strategy_id, date)
);

-- Create risk_events table
CREATE TABLE IF NOT EXISTS risk_events (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  event_type text NOT NULL,
  severity text NOT NULL CHECK (severity IN ('info', 'warning', 'critical')),
  message text NOT NULL,
  data jsonb DEFAULT '{}',
  resolved boolean DEFAULT false,
  created_at timestamptz DEFAULT now()
);

-- Create market_data table
CREATE TABLE IF NOT EXISTS market_data (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  symbol text NOT NULL,
  timeframe text NOT NULL,
  timestamp timestamptz NOT NULL,
  open numeric NOT NULL,
  high numeric NOT NULL,
  low numeric NOT NULL,
  close numeric NOT NULL,
  volume numeric NOT NULL,
  UNIQUE(symbol, timeframe, timestamp)
);

-- Create backtest_results table
CREATE TABLE IF NOT EXISTS backtest_results (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  strategy_name text NOT NULL,
  parameters jsonb NOT NULL,
  start_date timestamptz NOT NULL,
  end_date timestamptz NOT NULL,
  initial_capital numeric NOT NULL,
  final_capital numeric NOT NULL,
  total_return numeric NOT NULL,
  sharpe_ratio numeric,
  max_drawdown numeric,
  win_rate numeric,
  profit_factor numeric,
  total_trades integer,
  metrics jsonb DEFAULT '{}',
  created_at timestamptz DEFAULT now()
);

-- Create system_config table
CREATE TABLE IF NOT EXISTS system_config (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  key text UNIQUE NOT NULL,
  value jsonb NOT NULL,
  description text,
  updated_at timestamptz DEFAULT now()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_trades_strategy_id ON trades(strategy_id);
CREATE INDEX IF NOT EXISTS idx_trades_symbol ON trades(symbol);
CREATE INDEX IF NOT EXISTS idx_trades_entry_time ON trades(entry_time);
CREATE INDEX IF NOT EXISTS idx_trades_status ON trades(status);
CREATE INDEX IF NOT EXISTS idx_positions_strategy_id ON positions(strategy_id);
CREATE INDEX IF NOT EXISTS idx_positions_symbol ON positions(symbol);
CREATE INDEX IF NOT EXISTS idx_market_data_symbol_timeframe ON market_data(symbol, timeframe);
CREATE INDEX IF NOT EXISTS idx_market_data_timestamp ON market_data(timestamp);
CREATE INDEX IF NOT EXISTS idx_performance_metrics_strategy_date ON performance_metrics(strategy_id, date);
CREATE INDEX IF NOT EXISTS idx_risk_events_created_at ON risk_events(created_at);
CREATE INDEX IF NOT EXISTS idx_risk_events_severity ON risk_events(severity);

-- Enable RLS on all tables
ALTER TABLE strategies ENABLE ROW LEVEL SECURITY;
ALTER TABLE trades ENABLE ROW LEVEL SECURITY;
ALTER TABLE positions ENABLE ROW LEVEL SECURITY;
ALTER TABLE performance_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE risk_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE market_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE backtest_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE system_config ENABLE ROW LEVEL SECURITY;

-- Create RLS policies for authenticated access
CREATE POLICY "Allow read access to strategies"
  ON strategies FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "Allow insert access to strategies"
  ON strategies FOR INSERT
  TO authenticated
  WITH CHECK (true);

CREATE POLICY "Allow update access to strategies"
  ON strategies FOR UPDATE
  TO authenticated
  USING (true)
  WITH CHECK (true);

CREATE POLICY "Allow read access to trades"
  ON trades FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "Allow insert access to trades"
  ON trades FOR INSERT
  TO authenticated
  WITH CHECK (true);

CREATE POLICY "Allow update access to trades"
  ON trades FOR UPDATE
  TO authenticated
  USING (true)
  WITH CHECK (true);

CREATE POLICY "Allow read access to positions"
  ON positions FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "Allow insert access to positions"
  ON positions FOR INSERT
  TO authenticated
  WITH CHECK (true);

CREATE POLICY "Allow update access to positions"
  ON positions FOR UPDATE
  TO authenticated
  USING (true)
  WITH CHECK (true);

CREATE POLICY "Allow delete access to positions"
  ON positions FOR DELETE
  TO authenticated
  USING (true);

CREATE POLICY "Allow read access to performance_metrics"
  ON performance_metrics FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "Allow insert access to performance_metrics"
  ON performance_metrics FOR INSERT
  TO authenticated
  WITH CHECK (true);

CREATE POLICY "Allow read access to risk_events"
  ON risk_events FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "Allow insert access to risk_events"
  ON risk_events FOR INSERT
  TO authenticated
  WITH CHECK (true);

CREATE POLICY "Allow update access to risk_events"
  ON risk_events FOR UPDATE
  TO authenticated
  USING (true)
  WITH CHECK (true);

CREATE POLICY "Allow read access to market_data"
  ON market_data FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "Allow insert access to market_data"
  ON market_data FOR INSERT
  TO authenticated
  WITH CHECK (true);

CREATE POLICY "Allow read access to backtest_results"
  ON backtest_results FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "Allow insert access to backtest_results"
  ON backtest_results FOR INSERT
  TO authenticated
  WITH CHECK (true);

CREATE POLICY "Allow read access to system_config"
  ON system_config FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "Allow update access to system_config"
  ON system_config FOR UPDATE
  TO authenticated
  USING (true)
  WITH CHECK (true);

CREATE POLICY "Allow insert access to system_config"
  ON system_config FOR INSERT
  TO authenticated
  WITH CHECK (true);

-- Insert default system configuration
INSERT INTO system_config (key, value, description) VALUES
  ('max_risk_per_trade', '0.02', 'Maximum risk per trade as decimal (2%)'),
  ('max_daily_drawdown', '0.05', 'Maximum daily drawdown limit (5%)'),
  ('max_open_positions', '5', 'Maximum number of open positions'),
  ('min_risk_reward_ratio', '2.0', 'Minimum risk/reward ratio'),
  ('trading_enabled', 'false', 'Master switch for live trading'),
  ('paper_trading', 'true', 'Paper trading mode flag')
ON CONFLICT (key) DO NOTHING;