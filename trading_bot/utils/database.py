"""
Database Operations
Supabase integration for trade persistence and analytics
"""

from supabase import create_client, Client
from typing import Dict, List, Any, Optional
from datetime import datetime, date
from config import Config
from utils.logger import logger

class DatabaseManager:
    def __init__(self):
        self.client: Client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)

    async def save_trade(self, trade_data: Dict[str, Any]) -> Optional[str]:
        """Save trade to database"""
        try:
            result = self.client.table("trades").insert(trade_data).execute()
            logger.info(f"Trade saved: {result.data[0]['id']}")
            return result.data[0]['id']
        except Exception as e:
            logger.error(f"Error saving trade: {e}")
            return None

    async def update_trade(self, trade_id: str, update_data: Dict[str, Any]) -> bool:
        """Update existing trade"""
        try:
            self.client.table("trades").update(update_data).eq("id", trade_id).execute()
            logger.info(f"Trade updated: {trade_id}")
            return True
        except Exception as e:
            logger.error(f"Error updating trade: {e}")
            return False

    async def save_position(self, position_data: Dict[str, Any]) -> Optional[str]:
        """Save or update position"""
        try:
            result = self.client.table("positions").upsert(position_data).execute()
            return result.data[0]['id']
        except Exception as e:
            logger.error(f"Error saving position: {e}")
            return None

    async def get_open_positions(self, strategy_id: Optional[str] = None) -> List[Dict]:
        """Get all open positions"""
        try:
            query = self.client.table("positions").select("*")
            if strategy_id:
                query = query.eq("strategy_id", strategy_id)
            result = query.execute()
            return result.data
        except Exception as e:
            logger.error(f"Error fetching positions: {e}")
            return []

    async def close_position(self, position_id: str) -> bool:
        """Close position"""
        try:
            self.client.table("positions").delete().eq("id", position_id).execute()
            return True
        except Exception as e:
            logger.error(f"Error closing position: {e}")
            return False

    async def save_performance_metrics(self, metrics: Dict[str, Any]) -> bool:
        """Save performance metrics"""
        try:
            self.client.table("performance_metrics").upsert(metrics).execute()
            return True
        except Exception as e:
            logger.error(f"Error saving metrics: {e}")
            return False

    async def log_risk_event(self, event_type: str, severity: str, message: str, data: Dict = None) -> bool:
        """Log risk management event"""
        try:
            event_data = {
                "event_type": event_type,
                "severity": severity,
                "message": message,
                "data": data or {},
                "resolved": False
            }
            self.client.table("risk_events").insert(event_data).execute()
            logger.warning(f"Risk event: {event_type} - {message}")
            return True
        except Exception as e:
            logger.error(f"Error logging risk event: {e}")
            return False

    async def get_strategy(self, strategy_name: str) -> Optional[Dict]:
        """Get strategy configuration"""
        try:
            result = self.client.table("strategies").select("*").eq("name", strategy_name).limit(1).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error fetching strategy: {e}")
            return None

    async def get_active_strategies(self) -> List[Dict]:
        """Get all active strategies"""
        try:
            result = self.client.table("strategies").select("*").eq("enabled", True).execute()
            return result.data
        except Exception as e:
            logger.error(f"Error fetching strategies: {e}")
            return []

    async def save_backtest_result(self, result: Dict[str, Any]) -> bool:
        """Save backtest results"""
        try:
            self.client.table("backtest_results").insert(result).execute()
            logger.info(f"Backtest result saved for {result['strategy_name']}")
            return True
        except Exception as e:
            logger.error(f"Error saving backtest result: {e}")
            return False

    async def get_system_config(self, key: str) -> Any:
        """Get system configuration value"""
        try:
            result = self.client.table("system_config").select("value").eq("key", key).limit(1).execute()
            return result.data[0]['value'] if result.data else None
        except Exception as e:
            logger.error(f"Error fetching config: {e}")
            return None

    async def save_market_data(self, candles: List[Dict[str, Any]]) -> bool:
        """Save market data candles"""
        try:
            self.client.table("market_data").upsert(candles, ignore_duplicates=True).execute()
            return True
        except Exception as e:
            logger.error(f"Error saving market data: {e}")
            return False

    async def get_trades_by_date_range(self, start_date: date, end_date: date, strategy_id: Optional[str] = None) -> List[Dict]:
        """Get trades within date range"""
        try:
            query = self.client.table("trades").select("*").gte("entry_time", start_date.isoformat()).lte("entry_time", end_date.isoformat())
            if strategy_id:
                query = query.eq("strategy_id", strategy_id)
            result = query.execute()
            return result.data
        except Exception as e:
            logger.error(f"Error fetching trades: {e}")
            return []


db = DatabaseManager()
