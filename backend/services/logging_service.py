import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path
from typing import Dict
import sys
import json

class StructuredFormatter(logging.Formatter):
    """Formatter for JSON structured logs"""
    def format(self, record):
        log_record = {
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        if record.exc_info:
            log_record['exception'] = self.formatException(record.exc_info)
        
        if hasattr(record, 'context'):
            log_record.update(record.context)
            
        return json.dumps(log_record)

DEFAULT_LOGGING_CONFIG = {
    'log_dir': 'logs',
    'log_level': 'INFO',
    'log_file': 'app.log',
    'max_bytes': 10 * 1024 * 1024,  # 10MB
    'backup_count': 5,
    'console_log': True,
    'file_log': True,
    'structured_log': False
}

class LoggingService:
    def __init__(self, config: Dict = None):
        """
        Initialize logging service.
        
        Args:
            config: Logging configuration dictionary
        """
        self.config = {**DEFAULT_LOGGING_CONFIG, **(config or {})}
        self._setup_logging()

    def _setup_logging(self) -> None:
        """Configure logging handlers."""
        try:
            # Create log directory
            Path(self.config['log_dir']).mkdir(exist_ok=True)
            
            # Get root logger
            logger = logging.getLogger()
            logger.setLevel(self.config['log_level'])
            
            # Clear existing handlers
            logger.handlers.clear()
            
            # Add console handler
            if self.config['console_log']:
                console_handler = logging.StreamHandler(sys.stdout)
                console_handler.setFormatter(self._get_formatter())
                logger.addHandler(console_handler)
            
            # Add file handler
            if self.config['file_log']:
                file_handler = self._get_file_handler()
                logger.addHandler(file_handler)
                
        except Exception as e:
            print(f"CRITICAL: Logging setup failed: {str(e)}")
            raise

    def _get_formatter(self) -> logging.Formatter:
        """Get appropriate formatter based on config."""
        if self.config['structured_log']:
            return StructuredFormatter()
        return logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    def _get_file_handler(self) -> logging.Handler:
        """Create configured file handler."""
        log_file = Path(self.config['log_dir']) / self.config['log_file']
        
        if self.config.get('rotation') == 'time':
            handler = TimedRotatingFileHandler(
                filename=log_file,
                when='midnight',
                backupCount=self.config['backup_count'],
                encoding='utf-8'
            )
        else:
            handler = RotatingFileHandler(
                filename=log_file,
                maxBytes=self.config['max_bytes'],
                backupCount=self.config['backup_count'],
                encoding='utf-8'
            )
            
        handler.setFormatter(self._get_formatter())
        return handler

    def get_logger(self, name: str = None) -> logging.Logger:
        """
        Get configured logger instance.
        
        Args:
            name: Logger name (None for root)
            
        Returns:
            Configured logger
        """
        return logging.getLogger(name)

    def log_operation(self, operation: str, context: Dict = None, 
                     level: str = 'info') -> None:
        """
        Log an operation with context.
        
        Args:
            operation: Operation description
            context: Additional context data
            level: Log level
        """
        logger = self.get_logger(__name__)
        log_method = getattr(logger, level.lower(), logger.info)
        log_method(operation, extra={'context': context or {}})