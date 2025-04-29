"""
Advanced Logging Management Module

Provides comprehensive logging capabilities with multiple
output formats, filters, and advanced routing.
"""

import os
import sys
import logging
import json
import gzip
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler, SysLogHandler
from typing import Dict, Any, Optional, List, Union, Callable
from enum import Enum, auto
from datetime import datetime, timedelta
import platform
import traceback
import socket
import re
import uuid

class LogLevel(Enum):
    """
    Enhanced log levels with granular control
    """
    TRACE = logging.DEBUG - 5  # Most granular logging
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    NOTICE = logging.INFO + 5  # Between INFO and WARNING
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL
    EMERGENCY = logging.CRITICAL + 5  # Most severe logging

class LogOutputFormat(Enum):
    """
    Supported log output formats
    """
    TEXT = auto()
    JSON = auto()
    GELF = auto()  # Graylog Extended Log Format
    SYSLOG = auto()

class LogRecordEncoder(json.JSONEncoder):
    """
    Custom JSON encoder for log records
    """
    def default(self, obj):
        if isinstance(obj, (datetime, set)):
            return str(obj)
        
        try:
            return super().default(obj)
        except TypeError:
            return str(obj)

class AdvancedLogFormatter:
    """
    Flexible log formatting with multiple output styles
    """
    
    @staticmethod
    def text_format(record: logging.LogRecord) -> str:
        """
        Standard text log formatting
        """
        timestamp = datetime.fromtimestamp(record.created).isoformat()
        extra_info = ' | '.join(f"{k}={v}" for k, v in record.__dict__.items() 
                                if k not in ['msg', 'args', 'levelname', 'exc_text', 'exc_info'])
        
        log_message = record.getMessage()
        
        # Include exception information if present
        if record.exc_info:
            log_message += '\n' + ''.join(traceback.format_exception(*record.exc_info))
        
        return (
            f"{timestamp} | {record.levelname} | "
            f"{record.name} | {log_message} | {extra_info}"
        )
    
    @staticmethod
    def json_format(record: logging.LogRecord) -> str:
        """
        JSON log formatting
        """
        log_data = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'filename': record.filename,
            'line_number': record.lineno,
            'process_id': record.process,
            'process_name': record.processName,
            'thread_id': record.thread,
            'thread_name': record.threadName,
            'host': platform.node(),
            'log_id': str(uuid.uuid4())
        }
        
        # Add exception information if present
        if record.exc_info:
            log_data['exception'] = {
                'type': record.exc_info[0].__name__ if record.exc_info[0] else None,
                'message': str(record.exc_info[1]) if record.exc_info[1] else None,
                'traceback': traceback.format_tb(record.exc_info[2]) if record.exc_info[2] else None
            }
        
        # Include custom extra attributes
        for key, value in record.__dict__.items():
            if key not in log_data and not key.startswith('_'):
                log_data[key] = value
        
        return json.dumps(log_data, cls=LogRecordEncoder)
    
    @staticmethod
    def gelf_format(record: logging.LogRecord) -> str:
        """
        Graylog Extended Log Format (GELF) formatting
        """
        # GELF specification requires specific field names
        log_data = {
            'version': '1.1',
            'host': platform.node(),
            'short_message': record.getMessage(),
            'timestamp': record.created,
            'level': getattr(record, 'gelf_level', record.levelno),
            'line': record.lineno,
            'file': record.pathname,
            '_logger_name': record.name,
            '_module': record.module,
            '_process_id': record.process,
            '_process_name': record.processName,
            '_thread_id': record.thread,
            '_thread_name': record.threadName,
            '_log_id': str(uuid.uuid4())
        }
        
        # Add exception information if present
        if record.exc_info:
            log_data['full_message'] = ''.join(traceback.format_exception(*record.exc_info))
        
        # Add any custom fields
        for key, value in record.__dict__.items():
            if key not in log_data and not key.startswith('_'):
                log_data[f'_{key}'] = value
        
        return json.dumps(log_data, cls=LogRecordEncoder)

class LogFilter(logging.Filter):
    """
    Advanced log filtering with multiple criteria
    """
    def __init__(
        self, 
        min_level: Optional[LogLevel] = None,
        max_level: Optional[LogLevel] = None,
        logger_name_pattern: Optional[str] = None,
        message_pattern: Optional[str] = None,
        exclude_patterns: Optional[List[str]] = None
    ):
        """
        Initialize log filter with multiple filtering options
        
        Args:
            min_level: Minimum log level to allow
            max_level: Maximum log level to allow
            logger_name_pattern: Regex pattern to match logger names
            message_pattern: Regex pattern to match log messages
            exclude_patterns: List of regex patterns to exclude
        """
        super().__init__()
        self.min_level = min_level.value if min_level else None
        self.max_level = max_level.value if max_level else None
        
        # Compile regex patterns
        self.logger_name_regex = re.compile(logger_name_pattern) if logger_name_pattern else None
        self.message_regex = re.compile(message_pattern) if message_pattern else None
        
        # Compile exclude patterns
        self.exclude_regexes = [
            re.compile(pattern) for pattern in (exclude_patterns or [])
        ]
    
    def filter(self, record: logging.LogRecord) -> bool:
        """
        Apply filtering logic to log record
        
        Args:
            record: Log record to filter
        
        Returns:
            Boolean indicating whether to log the record
        """
        # Level filtering
        if self.min_level is not None and record.levelno < self.min_level:
            return False
        
        if self.max_level is not None and record.levelno > self.max_level:
            return False
        
        # Logger name filtering
        if self.logger_name_regex and not self.logger_name_regex.search(record.name):
            return False
        
        # Message filtering
        message = record.getMessage()
        if self.message_regex and not self.message_regex.search(message):
            return False
        
        # Exclusion filtering
        for exclude_regex in self.exclude_regexes:
            if exclude_regex.search(message):
                return False
        
        return True

class LogDestination:
    """
    Configurable log destination with multiple output options
    """
    def __init__(
        self, 
        output_type: str = 'file',  # file, console, syslog, network
        path: Optional[str] = None,
        format: LogOutputFormat = LogOutputFormat.TEXT,
        level: LogLevel = LogLevel.INFO,
        max_bytes: int = 10 * 1024 * 1024,  # 10 MB
        backup_count: int = 5,
        filters: Optional[List[LogFilter]] = None,
        host: Optional[str] = None,
        port: Optional[int] = None
    ):
        """
        Initialize log destination
        
        Args:
            output_type: Type of log output (file, console, syslog, network)
            path: Path for file-based logging
            format: Log output format
            level: Minimum log level
            max_bytes: Maximum log file size before rotation
            backup_count: Number of backup log files to keep
            filters: Optional list of log filters
            host: Hostname for network logging
            port: Port for network logging
        """
        self.output_type = output_type
        self.path = path
        self.format = format
        self.level = level
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        self.filters = filters or []
        self.host = host
        self.port = port
        
        # Handler will be created lazily
        self._handler = None
    
    def _create_handler(self):
        """
        Create appropriate log handler based on output type
        """
        # Determine formatter
        if self.format == LogOutputFormat.JSON:
            formatter = logging.Formatter(fmt=AdvancedLogFormatter.json_format)
        elif self.format == LogOutputFormat.GELF:
            formatter = logging.Formatter(fmt=AdvancedLogFormatter.gelf_format)
        else:
            formatter = logging.Formatter(fmt=AdvancedLogFormatter.text_format)
        
        # Create handler based on output type
        if self.output_type == 'file':
            # Ensure log directory exists
            os.makedirs(os.path.dirname(self.path), exist_ok=True)
            
            # Use rotating file handler
            handler = RotatingFileHandler(
                self.path, 
                maxBytes=self.max_bytes, 
                backupCount=self.backup_count
            )
        elif self.output_type == 'console':
            handler = logging.StreamHandler(sys.stdout)
        elif self.output_type == 'syslog':
            handler = SysLogHandler(
                address=(self.host or 'localhost', self.port or 514)
            )
        else:
            raise ValueError(f"Unsupported log output type: {self.output_type}")
        
        # Set formatter
        handler.setFormatter(formatter)
        
        # Add filters
        for log_filter in self.filters:
            handler.addFilter(log_filter)
        
        return handler
    
    def get_handler(self):
        """
        Get or create log handler
        """
        if not self._handler:
            self._handler = self._create_handler()
        return self._handler

class LoggingManager:
    """
    Comprehensive logging management system
    """
    
    def __init__(self):
        """
        Initialize logging system
        """
        # Logger configuration
        self._destinations: List[LogDestination] = []
        
        # Root logger configuration
        self._root_logger = logging.getLogger()
        self._root_logger.setLevel(logging.DEBUG)
    
    def add_destination(
        self, 
        destination: LogDestination,
        apply_to_root: bool = True
    ):
        """
        Add a log destination
        
        Args:
            destination: LogDestination to add
            apply_to_root: Whether to add handler to root logger
        """
        # Store destination
        self._destinations.append(destination)
        
        # Get handler
        handler = destination.get_handler()
        
        # Set log level for the handler
        handler.setLevel(destination.level.value)
        
        # Add to root logger if specified
        if apply_to_root:
            self._root_logger.addHandler(handler)
    
    def configure_global_logging(
        self, 
        level: LogLevel = LogLevel.INFO,
        log_format: LogOutputFormat = LogOutputFormat.TEXT
    ):
        """
        Configure global logging settings
        
        Args:
            level: Global minimum log level
            log_format: Global log output format
        """
        # Update root logger level
        self._root_logger.setLevel(level.value)
        
        # Remove existing handlers
        for handler in self._root_logger.handlers[:]:
            self._root_logger.removeHandler(handler)
        
        # Default console destination
        console_dest = LogDestination(
            output_type='console',
            format=log_format,
            level=level
        )
        self.add_destination(console_dest)
    
    def create_logger(
        self, 
        name: str, 
        level: Optional[LogLevel] = None,
        additional_destinations: Optional[List[LogDestination]] = None
    ) -> logging.Logger:
        """
        Create a logger with optional custom configuration
        
        Args:
            name: Logger name
            level: Optional log level
            additional_destinations: Optional additional log destinations
        
        Returns:
            Configured logger
        """
        logger = logging.getLogger(name)
        
        # Set level if specified
        if level:
            logger.setLevel(level.value)
        
        # Add additional destinations
        if additional_destinations:
            for dest in additional_destinations:
                logger.addHandler(dest.get_handler())
        
        return logger

# Global logging manager instance
logging_manager = LoggingManager()

# Expose key functions and types
__all__ = [
    'LoggingManager', 
    'LogDestination', 
    'LogFilter',
    'LogLevel', 
    'LogOutputFormat',
    'logging_manager'
]