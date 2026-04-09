/*
  # Fix RLS policies to allow anon key access
  
  ## Overview
  The trading bot and dashboard both use the Supabase anon key.
  Current policies only allow 'authenticated' role, blocking all access.
  This migration opens read/write to the anon role so the bot and dashboard can function.
  
  ## Changes
  - Drop all existing policies
  - Re-create with anon role access for all operations needed by the bot and dashboard
  - SELECT policies allow anon (dashboard reads)
  - INSERT/UPDATE/DELETE policies allow anon (bot writes)
*/

-- STRATEGIES
DROP POLICY IF EXISTS "Allow read access to strategies" ON strategies;
DROP POLICY IF EXISTS "Authenticated users can insert strategies" ON strategies;
DROP POLICY IF EXISTS "Authenticated users can update strategies" ON strategies;

CREATE POLICY "Allow read strategies"
  ON strategies FOR SELECT TO anon, authenticated
  USING (true);

CREATE POLICY "Allow insert strategies"
  ON strategies FOR INSERT TO anon, authenticated
  WITH CHECK (true);

CREATE POLICY "Allow update strategies"
  ON strategies FOR UPDATE TO anon, authenticated
  USING (true)
  WITH CHECK (true);

-- TRADES
DROP POLICY IF EXISTS "Allow read access to trades" ON trades;
DROP POLICY IF EXISTS "Authenticated users can insert trades" ON trades;
DROP POLICY IF EXISTS "Authenticated users can update trades" ON trades;

CREATE POLICY "Allow read trades"
  ON trades FOR SELECT TO anon, authenticated
  USING (true);

CREATE POLICY "Allow insert trades"
  ON trades FOR INSERT TO anon, authenticated
  WITH CHECK (true);

CREATE POLICY "Allow update trades"
  ON trades FOR UPDATE TO anon, authenticated
  USING (true)
  WITH CHECK (true);

-- POSITIONS
DROP POLICY IF EXISTS "Allow read access to positions" ON positions;
DROP POLICY IF EXISTS "Authenticated users can insert positions" ON positions;
DROP POLICY IF EXISTS "Authenticated users can update positions" ON positions;
DROP POLICY IF EXISTS "Authenticated users can delete positions" ON positions;

CREATE POLICY "Allow read positions"
  ON positions FOR SELECT TO anon, authenticated
  USING (true);

CREATE POLICY "Allow insert positions"
  ON positions FOR INSERT TO anon, authenticated
  WITH CHECK (true);

CREATE POLICY "Allow update positions"
  ON positions FOR UPDATE TO anon, authenticated
  USING (true)
  WITH CHECK (true);

CREATE POLICY "Allow delete positions"
  ON positions FOR DELETE TO anon, authenticated
  USING (true);

-- PERFORMANCE_METRICS
DROP POLICY IF EXISTS "Allow read access to performance_metrics" ON performance_metrics;
DROP POLICY IF EXISTS "Authenticated users can insert performance metrics" ON performance_metrics;

CREATE POLICY "Allow read performance_metrics"
  ON performance_metrics FOR SELECT TO anon, authenticated
  USING (true);

CREATE POLICY "Allow insert performance_metrics"
  ON performance_metrics FOR INSERT TO anon, authenticated
  WITH CHECK (true);

CREATE POLICY "Allow update performance_metrics"
  ON performance_metrics FOR UPDATE TO anon, authenticated
  USING (true)
  WITH CHECK (true);

-- RISK_EVENTS
DROP POLICY IF EXISTS "Allow read access to risk_events" ON risk_events;
DROP POLICY IF EXISTS "Authenticated users can insert risk events" ON risk_events;
DROP POLICY IF EXISTS "Authenticated users can update risk events" ON risk_events;

CREATE POLICY "Allow read risk_events"
  ON risk_events FOR SELECT TO anon, authenticated
  USING (true);

CREATE POLICY "Allow insert risk_events"
  ON risk_events FOR INSERT TO anon, authenticated
  WITH CHECK (true);

CREATE POLICY "Allow update risk_events"
  ON risk_events FOR UPDATE TO anon, authenticated
  USING (true)
  WITH CHECK (true);

-- MARKET_DATA
DROP POLICY IF EXISTS "Allow read access to market_data" ON market_data;
DROP POLICY IF EXISTS "Authenticated users can insert market data" ON market_data;

CREATE POLICY "Allow read market_data"
  ON market_data FOR SELECT TO anon, authenticated
  USING (true);

CREATE POLICY "Allow insert market_data"
  ON market_data FOR INSERT TO anon, authenticated
  WITH CHECK (true);

CREATE POLICY "Allow update market_data"
  ON market_data FOR UPDATE TO anon, authenticated
  USING (true)
  WITH CHECK (true);

-- BACKTEST_RESULTS
DROP POLICY IF EXISTS "Allow read access to backtest_results" ON backtest_results;
DROP POLICY IF EXISTS "Authenticated users can insert backtest results" ON backtest_results;

CREATE POLICY "Allow read backtest_results"
  ON backtest_results FOR SELECT TO anon, authenticated
  USING (true);

CREATE POLICY "Allow insert backtest_results"
  ON backtest_results FOR INSERT TO anon, authenticated
  WITH CHECK (true);

-- SYSTEM_CONFIG
DROP POLICY IF EXISTS "Allow read access to system_config" ON system_config;
DROP POLICY IF EXISTS "Authenticated users can insert system config" ON system_config;
DROP POLICY IF EXISTS "Authenticated users can update system config" ON system_config;

CREATE POLICY "Allow read system_config"
  ON system_config FOR SELECT TO anon, authenticated
  USING (true);

CREATE POLICY "Allow insert system_config"
  ON system_config FOR INSERT TO anon, authenticated
  WITH CHECK (true);

CREATE POLICY "Allow update system_config"
  ON system_config FOR UPDATE TO anon, authenticated
  USING (true)
  WITH CHECK (true);
