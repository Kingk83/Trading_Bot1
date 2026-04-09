"""
Database Operations
Supabase integration for trade persistence and analytics
"""

import requests
from supabase import create_client, Client
from typing import Dict, List, Any, Optional
from datetime import datetime, date
from config import Config
from utils.logger import logger


class DatabaseManager:
    def __init__(self):
        self.client: Client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
        self._headers = {
            "apikey": Config.SUPABASE_KEY,
            "Authorization": f"Bearer {Config.SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        }
        self._base_url = Config.SUPABASE_URL.rstrip("/") + "/rest/v1"

    def _get(self, table: str, params: Dict = None) -> List[Dict]:
        resp = requests.get(f"{self._base_url}/{table}", headers=self._headers, params=params)
        resp.raise_for_status()
        return resp.json()

    def _post(self, table: str, data: Any, upsert: bool = False, ignore_duplicates: bool = False, on_conflict: str = None) -> List[Dict]:
        headers = dict(self._headers)
        params = {}
        if upsert:
            prefer = "return=representation,resolution=merge-duplicates"
            if ignore_duplicates:
                prefer = "return=representation,resolution=ignore-duplicates"
            headers["Prefer"] = prefer
            if on_conflict:
                params["on_conflict"] = on_conflict
        resp = requests.post(f"{self._base_url}/{table}", headers=headers, json=data, params=params if params else None)
        if resp.status_code == 409 and ignore_duplicates:
            return []
        resp.raise_for_status()
        return resp.json() if resp.text else []

    def _patch(self, table: str, data: Dict, params: Dict) -> List[Dict]:
        resp = requests.patch(f"{self._base_url}/{table}", headers=self._headers, json=data, params=params)
        resp.raise_for_status()
        return resp.json() if resp.text else []

    def _delete(self, table: str, params: Dict) -> bool:
        resp = requests.delete(f"{self._base_url}/{table}", headers=self._headers, params=params)
        resp.raise_for_status()
        return True

    async def save_trade(self, trade_data: Dict[str, Any]) -> Optional[str]:
        try:
            result = self._post("trades", trade_data)
            if result:
                logger.info(f"Trade saved: {result[0]['id']}")
                return result[0]['id']
            return None
        except Exception as e:
            logger.error(f"Error saving trade: {e}")
            return None

    async def update_trade(self, trade_id: str, update_data: Dict[str, Any]) -> bool:
        try:
            self._patch("trades", update_data, {"id": f"eq.{trade_id}"})
            logger.info(f"Trade updated: {trade_id}")
            return True
        except Exception as e:
            logger.error(f"Error updating trade: {e}")
            return False

    async def save_position(self, position_data: Dict[str, Any]) -> Optional[str]:
        try:
            result = self._post("positions", position_data, upsert=True)
            return result[0]['id'] if result else None
        except Exception as e:
            logger.error(f"Error saving position: {e}")
            return None

    async def get_open_positions(self, strategy_id: Optional[str] = None) -> List[Dict]:
        try:
            params = {"select": "*"}
            if strategy_id:
                params["strategy_id"] = f"eq.{strategy_id}"
            return self._get("positions", params)
        except Exception as e:
            logger.error(f"Error fetching positions: {e}")
            return []

    async def close_position(self, position_id: str) -> bool:
        try:
            self._delete("positions", {"id": f"eq.{position_id}"})
            return True
        except Exception as e:
            logger.error(f"Error closing position: {e}")
            return False

    async def save_performance_metrics(self, metrics: Dict[str, Any]) -> bool:
        try:
            self._post("performance_metrics", metrics, upsert=True)
            return True
        except Exception as e:
            logger.error(f"Error saving metrics: {e}")
            return False

    async def log_risk_event(self, event_type: str, severity: str, message: str, data: Dict = None) -> bool:
        try:
            event_data = {
                "event_type": event_type,
                "severity": severity,
                "message": message,
                "data": data or {},
                "resolved": False
            }
            self._post("risk_events", event_data)
            logger.warning(f"Risk event: {event_type} - {message}")
            return True
        except Exception as e:
            logger.error(f"Error logging risk event: {e}")
            return False

    async def get_strategy(self, strategy_name: str) -> Optional[Dict]:
        try:
            result = self._get("strategies", {"name": f"eq.{strategy_name}", "limit": "1"})
            return result[0] if result else None
        except Exception as e:
            logger.error(f"Error fetching strategy: {e}")
            return None

    async def get_active_strategies(self) -> List[Dict]:
        try:
            return self._get("strategies", {"enabled": "eq.true"})
        except Exception as e:
            logger.error(f"Error fetching strategies: {e}")
            return []

    async def save_backtest_result(self, result: Dict[str, Any]) -> bool:
        try:
            self._post("backtest_results", result)
            logger.info(f"Backtest result saved for {result['strategy_name']}")
            return True
        except Exception as e:
            logger.error(f"Error saving backtest result: {e}")
            return False

    async def get_system_config(self, key: str) -> Any:
        try:
            result = self._get("system_config", {"key": f"eq.{key}", "select": "value", "limit": "1"})
            return result[0]['value'] if result else None
        except Exception as e:
            logger.error(f"Error fetching config: {e}")
            return None

    async def save_market_data(self, candles: List[Dict[str, Any]]) -> bool:
        try:
            self._post("market_data", candles, upsert=True, ignore_duplicates=True, on_conflict="symbol,timeframe,timestamp")
            return True
        except Exception as e:
            logger.error(f"Error saving market data: {e}")
            return False

    async def get_trades_by_date_range(self, start_date: date, end_date: date, strategy_id: Optional[str] = None) -> List[Dict]:
        try:
            params = {
                "select": "*",
                "entry_time": f"gte.{start_date.isoformat()}",
                "entry_time": f"lte.{end_date.isoformat()}",
            }
            if strategy_id:
                params["strategy_id"] = f"eq.{strategy_id}"
            return self._get("trades", params)
        except Exception as e:
            logger.error(f"Error fetching trades: {e}")
            return []


db = DatabaseManager()
