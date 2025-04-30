import asyncio
import logging
import aiosmtplib
import aiohttp
import platform
from typing import Dict, Any, List, Optional, Set
from enum import Enum, auto
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import json

logger = logging.getLogger(__name__)

class AlertSeverity(Enum):
    INFO = 1
    WARNING = 2
    CRITICAL = 3
    EMERGENCY = 4

class AlertType(Enum):
    SYSTEM_RESOURCE = auto()
    PERFORMANCE_DEGRADATION = auto()
    SECURITY_EVENT = auto()
    MOD_RELATED = auto()
    PROCESS_RELATED = auto()
    AUTOMATION_EVENT = auto()
    PLUGIN_EVENT = auto()

@dataclass(frozen=True)
class SystemAlert:
    alert_type: AlertType
    severity: AlertSeverity
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = field(default_factory=platform.node)
    details: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.alert_type.name,
            "severity": self.severity.name,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "details": self.details
        }

class AlertNotificationChannel:
    async def send_alert(self, alert: SystemAlert) -> None:
        raise NotImplementedError("Subclasses must implement send_alert method")

class EmailNotificationChannel(AlertNotificationChannel):
    def __init__(self, smtp_host: str, smtp_port: int, sender_email: str,
                 sender_password: Optional[str] = None, recipients: Set[str] = None,
                 use_tls: bool = True):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.recipients = recipients or set()
        self.use_tls = use_tls
    
    async def send_alert(self, alert: SystemAlert) -> None:
        if not self.recipients:
            return

        try:
            subject = f"[{alert.severity.name}] {alert.alert_type.name} Alert"
            body = json.dumps(alert.to_dict(), indent=2)
            message = f"Subject: {subject}\nFrom: {self.sender_email}\nTo: {', '.join(self.recipients)}\n\n{body}"
            
            async with aiosmtplib.SMTP(hostname=self.smtp_host, port=self.smtp_port) as server:
                if self.use_tls:
                    await server.starttls()
                if self.sender_password:
                    await server.login(self.sender_email, self.sender_password)
                await server.sendmail(self.sender_email, list(self.recipients), message)
            
            logger.info(f"Email alert sent: {subject}")
        except Exception as e:
            logger.error(f"Failed to send email alert: {str(e)}")
            raise

class WebhookNotificationChannel(AlertNotificationChannel):
    def __init__(self, webhook_url: str, headers: Optional[Dict[str, str]] = None,
                 timeout: float = 10.0):
        self.webhook_url = webhook_url
        self.headers = headers or {'Content-Type': 'application/json'}
        self.timeout = aiohttp.ClientTimeout(total=timeout)
    
    async def send_alert(self, alert: SystemAlert) -> None:
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.post(
                    self.webhook_url,
                    headers=self.headers,
                    json=alert.to_dict()
                ) as response:
                    response.raise_for_status()
            logger.info(f"Webhook alert sent: {alert.alert_type.name}")
        except Exception as e:
            logger.error(f"Failed to send webhook alert: {str(e)}")
            raise

class SystemAlertsManager:
    def __init__(self, max_alert_history: int = 1000,
                 default_channels: Optional[List[AlertNotificationChannel]] = None):
        self._alert_history: List[SystemAlert] = []
        self._max_alert_history = max(100, max_alert_history)
        self._notification_channels = default_channels or []
        self._alert_routing: Dict[AlertType, Dict[AlertSeverity, List[AlertNotificationChannel]]] = {}
        self._alert_queue: asyncio.Queue = asyncio.Queue()
        self._processing_task: Optional[asyncio.Task] = None
        self._running = False
        self._lock = asyncio.Lock()

    def add_notification_channel(self, channel: AlertNotificationChannel,
                               alert_types: Optional[List[AlertType]] = None,
                               severity_threshold: AlertSeverity = AlertSeverity.WARNING) -> None:
        if channel not in self._notification_channels:
            self._notification_channels.append(channel)
        
        if alert_types:
            for alert_type in alert_types:
                if alert_type not in self._alert_routing:
                    self._alert_routing[alert_type] = {}
                for severity in AlertSeverity:
                    if severity.value >= severity_threshold.value:
                        if severity not in self._alert_routing[alert_type]:
                            self._alert_routing[alert_type][severity] = []
                        if channel not in self._alert_routing[alert_type][severity]:
                            self._alert_routing[alert_type][severity].append(channel)

    async def _process_alerts(self) -> None:
        while self._running:
            try:
                alert = await self._alert_queue.get()
                channels = self._get_notification_channels(alert)
                
                async with asyncio.TaskGroup() as tg:
                    for channel in channels:
                        tg.create_task(self._send_alert_safely(channel, alert))
                
                self._alert_queue.task_done()
            except* Exception as e:
                logger.error(f"Error processing alert: {e}")
            except asyncio.CancelledError:
                break

    async def _send_alert_safely(self, channel: AlertNotificationChannel, alert: SystemAlert) -> None:
        try:
            await channel.send_alert(alert)
        except Exception as e:
            logger.error(f"Failed to send alert through {channel.__class__.__name__}: {e}")

    def _get_notification_channels(self, alert: SystemAlert) -> List[AlertNotificationChannel]:
        channels = set()
        if alert.alert_type in self._alert_routing and alert.severity in self._alert_routing[alert.alert_type]:
            channels.update(self._alert_routing[alert.alert_type][alert.severity])
        channels.update(self._notification_channels)
        return list(channels)

    async def generate_alert(self, alert_type: AlertType, message: str,
                           severity: AlertSeverity = AlertSeverity.WARNING,
                           source: Optional[str] = None,
                           details: Optional[Dict[str, Any]] = None) -> None:
        alert = SystemAlert(
            alert_type=alert_type,
            severity=severity,
            message=message,
            source=source or platform.node(),
            details=details or {}
        )
        
        async with self._lock:
            self._alert_history.append(alert)
            if len(self._alert_history) > self._max_alert_history:
                self._alert_history = self._alert_history[-self._max_alert_history:]
            
        if self._running:
            await self._alert_queue.put(alert)

    def start_processing(self) -> None:
        if not self._running:
            self._running = True
            self._processing_task = asyncio.create_task(self._process_alerts())
            logger.info("Alert processing started")

    async def stop_processing(self) -> None:
        if self._running:
            self._running = False
            if self._processing_task:
                self._processing_task.cancel()
                try:
                    await self._processing_task
                except asyncio.CancelledError:
                    pass
            await self._alert_queue.join()
            logger.info("Alert processing stopped")

    def get_alert_history(self, alert_type: Optional[AlertType] = None,
                         severity: Optional[AlertSeverity] = None,
                         duration: Optional[timedelta] = None) -> List[SystemAlert]:
        alerts = self._alert_history.copy()
        cutoff_time = datetime.now() - duration if duration else None
        
        return [
            alert for alert in alerts
            if (not alert_type or alert.alert_type == alert_type) and
               (not severity or alert.severity == severity) and
               (not cutoff_time or alert.timestamp >= cutoff_time)
        ]

system_alerts_manager = SystemAlertsManager()

__all__ = [
    'SystemAlertsManager',
    'SystemAlert',
    'AlertSeverity',
    'AlertType',
    'system_alerts_manager',
    'EmailNotificationChannel',
    'WebhookNotificationChannel'
]