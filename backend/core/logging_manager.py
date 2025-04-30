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
from pathlib import Path

class LogLevel(Enum):
    TRACE = logging.DEBUG - 5
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    NOTICE = logging.INFO + 5
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL
    EMERGENCY = logging.CRITICAL + 5

class LogOutputFormat(Enum):
    TEXT = auto()
    JSON = auto()
    GELF = auto()
    SYSLOG = auto()

class LogRecordEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, set, timedelta)):
            return str(obj)
        if isinstance(obj, Enum):
            return obj.value
        try:
            return super().default(obj)
        except TypeError:
            return str(obj)

class AdvancedLogFormatter:
    EXCLUDED_FIELDS = {'msg', 'args', 'levelname', 'exc_text', 'exc_info', 'message', 
                      'created', 'msecs', 'relativeCreated', 'levelno', 'pathname', 
                      'filename', 'module', 'lineno', 'funcName', 'name'}

    @staticmethod
    def text_format(record: logging.LogRecord) -> str:
        timestamp = datetime.fromtimestamp(record.created).isoformat()
        extra_info = ' | '.join(f"{k}={v}" for k, v in record.__dict__.items() 
                               if k not in AdvancedLogFormatter.EXCLUDED_FIELDS)
        
        log_message = record.getMessage()
        if record.exc_info:
            log_message += '\n' + ''.join(traceback.format_exception(*record.exc_info))
            
        return f"{timestamp} | {record.levelname:<8} | {record.name:<20} | {log_message}{' | ' + extra_info if extra_info else ''}"

    @staticmethod 
    def json_format(record: logging.LogRecord) -> str:
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

        if record.exc_info:
            log_data['exception'] = {
                'type': record.exc_info[0].__name__ if record.exc_info[0] else None,
                'message': str(record.exc_info[1]) if record.exc_info[1] else None,
                'traceback': traceback.format_tb(record.exc_info[2]) if record.exc_info[2] else None
            }

        extra_fields = {k: v for k, v in record.__dict__.items() 
                       if k not in log_data and not k.startswith('_') 
                       and k not in AdvancedLogFormatter.EXCLUDED_FIELDS}
        log_data.update(extra_fields)

        return json.dumps(log_data, cls=LogRecordEncoder)

    @staticmethod
    def gelf_format(record: logging.LogRecord) -> str:
        log_data = {
            'version': '1.1',
            'host': platform.node(),
            'short_message': record.getMessage()[:1024],
            'full_message': record.getMessage(),
            'timestamp': record.created,
            'level': min(7, (record.levelno // 10) + 1),
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

        if record.exc_info:
            log_data['_exception'] = ''.join(traceback.format_exception(*record.exc_info))

        extra_fields = {f"_{k}": v for k, v in record.__dict__.items() 
                       if k not in log_data and not k.startswith('_')
                       and k not in AdvancedLogFormatter.EXCLUDED_FIELDS}
        log_data.update(extra_fields)

        return json.dumps(log_data, cls=LogRecordEncoder)

class LogFilter(logging.Filter):
    def __init__(self, min_level: Optional[LogLevel] = None,
                 max_level: Optional[LogLevel] = None,
                 logger_name_pattern: Optional[str] = None, 
                 message_pattern: Optional[str] = None,
                 exclude_patterns: Optional[List[str]] = None):
        super().__init__()
        self.min_level = min_level.value if min_level else None
        self.max_level = max_level.value if max_level else None
        self.logger_name_regex = re.compile(logger_name_pattern) if logger_name_pattern else None
        self.message_regex = re.compile(message_pattern) if message_pattern else None
        self.exclude_regexes = [re.compile(pattern) for pattern in (exclude_patterns or [])]

    def filter(self, record: logging.LogRecord) -> bool:
        if self.min_level is not None and record.levelno < self.min_level:
            return False
        if self.max_level is not None and record.levelno > self.max_level:
            return False
        if self.logger_name_regex and not self.logger_name_regex.search(record.name):
            return False
            
        message = record.getMessage()
        if self.message_regex and not self.message_regex.search(message):
            return False
        
        return not any(regex.search(message) for regex in self.exclude_regexes)

class LogDestination:
    SUPPORTED_OUTPUTS = {'file', 'console', 'syslog'}

    def __init__(self, output_type: str = 'file',
                 path: Optional[Union[str, Path]] = None,
                 format: LogOutputFormat = LogOutputFormat.TEXT,
                 level: LogLevel = LogLevel.INFO,
                 max_bytes: int = 10 * 1024 * 1024,
                 backup_count: int = 5,
                 filters: Optional[List[LogFilter]] = None,
                 host: Optional[str] = None,
                 port: Optional[int] = None,
                 compression: bool = False):
        if output_type not in self.SUPPORTED_OUTPUTS:
            raise ValueError(f"Unsupported output type: {output_type}")
        if output_type == 'file' and not path:
            raise ValueError("Path must be specified for file output type")
            
        self.output_type = output_type
        self.path = Path(path) if path else None
        self.format = format
        self.level = level
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        self.filters = filters or []
        self.host = host
        self.port = port
        self.compression = compression
        self._handler = None

    def _create_handler(self):
        formatter = logging.Formatter(fmt=getattr(AdvancedLogFormatter, f"{self.format.name.lower()}_format"))

        if self.output_type == 'file':
            self.path.parent.mkdir(parents=True, exist_ok=True)
            handler = RotatingFileHandler(
                str(self.path),
                maxBytes=self.max_bytes,
                backupCount=self.backup_count,
                encoding='utf-8'
            )
        elif self.output_type == 'console':
            handler = logging.StreamHandler(sys.stdout)
        else:  # syslog
            handler = SysLogHandler(address=(self.host or 'localhost', self.port or 514))

        handler.setFormatter(formatter)
        for log_filter in self.filters:
            handler.addFilter(log_filter)

        return handler

    def get_handler(self):
        if not self._handler:
            self._handler = self._create_handler()
        return self._handler

class LoggingManager:
    def __init__(self):
        self._destinations = []
        self._root_logger = logging.getLogger()
        self._root_logger.setLevel(logging.DEBUG)

    def add_destination(self, destination: LogDestination, apply_to_root: bool = True):
        self._destinations.append(destination)
        handler = destination.get_handler()
        handler.setLevel(destination.level.value)
        if apply_to_root:
            self._root_logger.addHandler(handler)

    def configure_global_logging(self, level: LogLevel = LogLevel.INFO,
                               log_format: LogOutputFormat = LogOutputFormat.TEXT):
        self._root_logger.setLevel(level.value)
        for handler in self._root_logger.handlers[:]:
            self._root_logger.removeHandler(handler)
            handler.close()
        
        console_dest = LogDestination(
            output_type='console',
            format=log_format,
            level=level
        )
        self.add_destination(console_dest)

    def create_logger(self, name: str,
                     level: Optional[LogLevel] = None,
                     additional_destinations: Optional[List[LogDestination]] = None) -> logging.Logger:
        logger = logging.getLogger(name)
        if level:
            logger.setLevel(level.value)
        if additional_destinations:
            for dest in additional_destinations:
                logger.addHandler(dest.get_handler())
        return logger

    def shutdown(self):
        for handler in self._root_logger.handlers[:]:
            self._root_logger.removeHandler(handler)
            handler.close()
        self._destinations.clear()

logging_manager = LoggingManager()

__all__ = ['LoggingManager', 'LogDestination', 'LogFilter', 'LogLevel', 'LogOutputFormat', 'logging_manager']