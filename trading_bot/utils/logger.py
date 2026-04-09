"""
Logging Configuration
Structured logging for the trading system
"""

import logging
import os
import sys
from datetime import datetime
from typing import Optional

class TradingLogger:
    _instance: Optional[logging.Logger] = None

    @classmethod
    def get_logger(cls, name: str = "trading_bot") -> logging.Logger:
        """Get or create logger instance"""
        if cls._instance is None:
            cls._instance = cls._setup_logger(name)
        return cls._instance

    @classmethod
    def _setup_logger(cls, name: str) -> logging.Logger:
        """Setup logger with formatters and handlers"""
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)

            os.makedirs("logs", exist_ok=True)
            file_handler = logging.FileHandler(
                f"logs/trading_{datetime.now().strftime('%Y%m%d')}.log"
            )
            file_handler.setLevel(logging.DEBUG)

            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )

            console_handler.setFormatter(formatter)
            file_handler.setFormatter(formatter)

            logger.addHandler(console_handler)
            logger.addHandler(file_handler)

        return logger


logger = TradingLogger.get_logger()
