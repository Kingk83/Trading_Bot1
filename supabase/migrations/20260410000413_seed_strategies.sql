/*
  # Seed default trading strategies

  Inserts the three default strategies (TrendFollowing, MeanReversion, Breakout)
  into the strategies table so the bot can find and execute them.
  Uses INSERT ... ON CONFLICT DO NOTHING to be safe on re-runs.
*/

INSERT INTO strategies (name, type, parameters, enabled)
VALUES
  (
    'TrendFollowing',
    'trend_following',
    '{"fast_ema": 12, "slow_ema": 26, "signal_ema": 9, "atr_period": 14, "atr_multiplier": 2.0, "adx_threshold": 25, "min_confidence": 0.6}'::jsonb,
    true
  ),
  (
    'MeanReversion',
    'mean_reversion',
    '{"rsi_period": 14, "rsi_oversold": 30, "rsi_overbought": 70, "bb_period": 20, "bb_std": 2, "atr_period": 14, "adx_threshold": 25, "min_confidence": 0.6}'::jsonb,
    true
  ),
  (
    'Breakout',
    'breakout',
    '{"lookback_period": 20, "volume_multiplier": 1.5, "atr_period": 14, "breakout_threshold": 0.02, "consolidation_periods": 10, "min_confidence": 0.6}'::jsonb,
    true
  )
ON CONFLICT (name) DO NOTHING;
