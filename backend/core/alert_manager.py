"""
Advanced System Alerts Management Module

Provides comprehensive alert generation, routing, and management
capabilities for ModHub Central.
"""

import asyncio
import logging
import smtplib
import requests
import platform
from typing import Dict, Any, List, Optional, Callable, Coroutine, Union
from enum import Enum, auto
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import json

from core.events import EventType, SystemEvent

logger = logging.getLogger(__name__)

class AlertSeverity(Enum):
    """
    Alert severity levels
    """
    INFO = 1
    WARNING = 2
    CRITICAL = 3
    EMERGENCY = 4

class AlertType(Enum):
    """
    Predefined alert types
    """
    SYSTEM_RESOURCE = auto()
    PERFORMANCE_DEGRADATION = auto()
    SECURITY_EVENT = auto()
    MOD_RELATED = auto()
    PROCESS_RELATED = auto()
    AUTOMATION_EVENT = auto()
    PLUGIN_EVENT = auto()

@dataclass
class SystemAlert:
    """
    Comprehensive system alert representation
    """
    alert_type: AlertType
    severity: AlertSeverity
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    source: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert alert to dictionary representation"""
        return {
            "type": self.alert_type.name,
            "severity": self.severity.name,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "details": self.details
        }

class AlertNotificationChannel:
    """
    Base class for alert notification channels
    """
    async def send_alert(self, alert: SystemAlert):
        """
        Send an alert through the specific channel
        
        Args:
            alert: SystemAlert to send
        """
        raise NotImplementedError("Subclasses must implement send_alert method")

class EmailNotificationChannel(AlertNotificationChannel):
    """
    Email notification channel for system alerts
    """
    def __init__(
        self, 
        smtp_host: str, 
        smtp_port: int,
        sender_email: str,
        sender_password: Optional[str] = None,
        recipients: List[str] = [],
        use_tls: bool = True
    ):
        """
        Initialize email notification channel
        
        Args:
            smtp_host: SMTP server host
            smtp_port: SMTP server port
            sender_email: Email address sending the alert
            sender_password: Optional password for authentication
            recipients: List of recipient email addresses
            use_tls: Whether to use TLS encryption
        """
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.recipients = recipients
        self.use_tls = use_tls
    
    async def send_alert(self, alert: SystemAlert):
        """
        Send alert via email
        
        Args:
            alert: SystemAlert to send
        """
        try:
            # Create email message
            subject = f"[{alert.severity.name}] {alert.alert_type.name} Alert"
            body = json.dumps(alert.to_dict(), indent=2)
            
            # Construct email content
            email_content = f"""Subject: {subject}
From: {self.sender_email}
To: {', '.join(self.recipients)}

{body}
"""
            
            # Establish SMTP connection
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                
                # Authenticate if password provided
                if self.sender_password:
                    server.login(self.sender_email, self.sender_password)
                
                # Send email
                server.sendmail(
                    self.sender_email, 
                    self.recipients, 
                    email_content
                )
            
            logger.info(f"Email alert sent: {subject}")
        
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")

class WebhookNotificationChannel(AlertNotificationChannel):
    """
    Webhook notification channel for system alerts
    """
    def __init__(
        self, 
        webhook_url: str,
        headers: Optional[Dict[str, str]] = None
    ):
        """
        Initialize webhook notification channel
        
        Args:
            webhook_url: URL to send webhook alerts
            headers: Optional custom headers
        """
        self.webhook_url = webhook_url
        self.headers = headers or {
            'Content-Type': 'application/json'
        }
    
    async def send_alert(self, alert: SystemAlert):
        """
        Send alert via webhook
        
        Args:
            alert: SystemAlert to send
        """
        try:
            # Send alert as JSON payload
            response = requests.post(
                self.webhook_url,
                headers=self.headers,
                json=alert.to_dict()
            )
            
            # Check response
            response.raise_for_status()
            
            logger.info(f"Webhook alert sent: {alert.alert_type.name}")
        
        except Exception as e:
            logger.error(f"Failed to send webhook alert: {e}")

class SystemAlertsManager:
    """
    Comprehensive system alerts management and routing
    """
    
    def __init__(
        self, 
        max_alert_history: int = 1000,
        default_channels: Optional[List[AlertNotificationChannel]] = None
    ):
        """
        Initialize alerts manager
        
        Args:
            max_alert_history: Maximum number of alerts to keep in history
            default_channels: Default notification channels
        """
        # Alert history management
        self._alert_history: List[SystemAlert] = []
        self._max_alert_history = max_alert_history
        
        # Notification channels
        self._notification_channels: List[AlertNotificationChannel] = default_channels or []
        
        # Alert routing based on severity and type
        self._alert_routing: Dict[
            AlertType, 
            Dict[AlertSeverity, List[AlertNotificationChannel]]
        ] = {}
        
        # Asynchronous processing queue
        self._alert_queue = asyncio.Queue()
        self._processing_task: Optional[asyncio.Task] = None
    
    def add_notification_channel(
        self, 
        channel: AlertNotificationChannel, 
        alert_types: Optional[List[AlertType]] = None,
        severity_threshold: AlertSeverity = AlertSeverity.WARNING
    ):
        """
        Add a notification channel with optional routing rules
        
        Args:
            channel: Notification channel to add
            alert_types: Optional list of alert types to route through this channel
            severity_threshold: Minimum severity to trigger this channel
        """
        # Add to global channels
        self._notification_channels.append(channel)
        
        # Configure routing if alert types specified
        if alert_types:
            for alert_type in alert_types:
                if alert_type not in self._alert_routing:
                    self._alert_routing[alert_type] = {}
                
                # Create severity-based routing
                for severity in AlertSeverity:
                    if severity.value >= severity_threshold.value:
                        if severity not in self._alert_routing[alert_type]:
                            self._alert_routing[alert_type] = {}
                        
                        if severity not in self._alert_routing[alert_type]:
                            self._alert_routing[alert_type][severity] = []
                        
                        self._alert_routing[alert_type][severity].append(channel)
    
    async def _process_alerts(self):
        """
        Background task to process alerts from the queue
        """
        while True:
            try:
                # Wait for an alert
                alert = await self._alert_queue.get()
                
                # Determine routing channels
                channels_to_notify = self._notification_channels
                
                # Apply specific routing if configured
                if alert.alert_type in self._alert_routing:
                    type_routes = self._alert_routing[alert.alert_type]
                    if alert.severity in type_routes:
                        channels_to_notify = type_routes[alert.severity]
                
                # Send alert to routed channels
                for channel in channels_to_notify:
                    try:
                        await channel.send_alert(alert)
                    except Exception as e:
                        logger.error(f"Error sending alert through channel: {e}")
                
                # Mark queue task as done
                self._alert_queue.task_done()
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Unexpected error in alert processing: {e}")
    
    async def generate_alert(
        self, 
        alert_type: AlertType, 
        message: str,
        severity: AlertSeverity = AlertSeverity.WARNING,
        source: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Generate and queue a system alert
        
        Args:
            alert_type: Type of alert
            message: Alert message
            severity: Alert severity level
            source: Source of the alert
            details: Additional alert details
        """
        # Create alert instance
        alert = SystemAlert(
            alert_type=alert_type,
            severity=severity,
            message=message,
            source=source or platform.node(),
            details=details or {}
        )
        
        # Add to alert history
        self._alert_history.append(alert)
        
        # Trim history if exceeds max
        if len(self._alert_history) > self._max_alert_history:
            self._alert_history = self._alert_history[-self._max_alert_history:]
        
        # Queue alert for processing
        await self._alert_queue.put(alert)
    
    def start_processing(self):
        """
        Start background alert processing
        """
        if self._processing_task is None or self._processing_task.done():
            self._processing_task = asyncio.create_task(self._process_alerts())
            logger.info("Alert processing started")
    
    def stop_processing(self):
        """
        Stop background alert processing
        """
        if self._processing_task and not self._processing_task.done():
            self._processing_task.cancel()
            logger.info("Alert processing stopped")
    
    def get_alert_history(
        self, 
        alert_type: Optional[AlertType] = None,
        severity: Optional[AlertSeverity] = None,
        duration: Optional[timedelta] = None
    ) -> List[SystemAlert]:
        """
        Retrieve alert history with optional filtering
        
        Args:
            alert_type: Optional alert type to filter
            severity: Optional severity level to filter
            duration: Optional time duration to retrieve alerts for
        
        Returns:
            Filtered list of alerts
        """
        alerts = self._alert_history
        
        # Filter by alert type
        if alert_type:
            alerts = [a for a in alerts if a.alert_type == alert_type]
        
        # Filter by severity
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        
        # Filter by duration
        if duration:
            cutoff_time = datetime.now() - duration
            alerts = [a for a in alerts if a.timestamp >= cutoff_time]
        
        return alerts

# Global system alerts manager instance
system_alerts_manager = SystemAlertsManager()

# Expose key functions and types
__all__ = [
    'SystemAlertsManager', 
    'SystemAlert', 
    'AlertSeverity', 
    'AlertType',
    'system_alerts_manager',
    'EmailNotificationChannel',
    'WebhookNotificationChannel'
]