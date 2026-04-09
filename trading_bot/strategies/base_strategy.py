"""
Base Strategy Class
Abstract base class for all trading strategies
"""

from abc import ABC, abstractmethod
import pandas as pd
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class SignalType(Enum):
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
    CLOSE_LONG = "close_long"
    CLOSE_SHORT = "close_short"

@dataclass
class Signal:
    type: SignalType
    price: float
    stop_loss: float
    take_profit: float
    confidence: float
    metadata: Dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class BaseStrategy(ABC):
    def __init__(self, name: str, parameters: Dict):
        self.name = name
        self.parameters = parameters
        self.position = None

    @abstractmethod
    def generate_signal(self, df: pd.DataFrame) -> Optional[Signal]:
        """Generate trading signal based on current data"""
        pass

    @abstractmethod
    def calculate_stop_loss(self, entry_price: float, side: str, df: pd.DataFrame) -> float:
        """Calculate stop loss level"""
        pass

    @abstractmethod
    def calculate_take_profit(self, entry_price: float, side: str, df: pd.DataFrame) -> float:
        """Calculate take profit level"""
        pass

    def should_exit(self, df: pd.DataFrame, position: Dict) -> Tuple[bool, str]:
        """Check if position should be exited"""
        current_price = df['close'].iloc[-1]

        if position['side'] == 'long':
            if current_price <= position['stop_loss']:
                return True, "stop_loss"
            if current_price >= position['take_profit']:
                return True, "take_profit"
        else:
            if current_price >= position['stop_loss']:
                return True, "stop_loss"
            if current_price <= position['take_profit']:
                return True, "take_profit"

        signal = self.generate_signal(df)
        if signal and self._is_exit_signal(signal, position):
            return True, "signal_exit"

        return False, ""

    def _is_exit_signal(self, signal: Signal, position: Dict) -> bool:
        """Check if signal indicates exit"""
        if position['side'] == 'long' and signal.type == SignalType.SELL:
            return True
        if position['side'] == 'short' and signal.type == SignalType.BUY:
            return True
        return False

    def validate_signal(self, signal: Optional[Signal], df: pd.DataFrame) -> bool:
        """Validate signal before execution"""
        if signal is None:
            return False

        if signal.type == SignalType.HOLD:
            return False

        if signal.stop_loss <= 0 or signal.take_profit <= 0:
            return False

        if signal.confidence < 0.5:
            return False

        return True

    def get_parameters(self) -> Dict:
        """Get strategy parameters"""
        return self.parameters

    def update_parameters(self, new_parameters: Dict):
        """Update strategy parameters"""
        self.parameters.update(new_parameters)
