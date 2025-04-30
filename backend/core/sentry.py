import os
import logging
from typing import Optional, List, Any, Dict
from sentry_sdk.client import Client

logger = logging.getLogger(__name__)

def configure_sentry(
    dsn: Optional[str] = None,
    environment: str = 'development',
    release: str = '0.2.0',
    traces_sample_rate: float = 0.1,
    profiles_sample_rate: float = 0.1,
    integrations: Optional[List[Any]] = None
) -> Optional[Client]:
    import sentry_sdk
    
    sentry_dsn = dsn or os.getenv('MODHUB_SENTRY_DSN')
    
    if not sentry_dsn:
        logger.warning("No Sentry DSN provided. Error tracking is disabled.")
        return None

    try:
        sdk_integrations = []
        integration_classes = [
            ('sentry_sdk.integrations.fastapi', 'FastAPIIntegration'),
            ('sentry_sdk.integrations.sqlalchemy', 'SqlAlchemyIntegration'),
            ('sentry_sdk.integrations.logging', 'LoggingIntegration')
        ]

        for module_path, class_name in integration_classes:
            try:
                module = __import__(module_path, fromlist=[class_name])
                integration_class = getattr(module, class_name)
                integration = (
                    integration_class(level=logging.INFO, event_level=logging.ERROR)
                    if class_name == 'LoggingIntegration'
                    else integration_class()
                )
                sdk_integrations.append(integration)
            except ImportError:
                logger.warning(f"Failed to load {class_name} for Sentry")

        if integrations:
            sdk_integrations.extend(integrations)

        sentry_sdk.init(
            dsn=sentry_dsn,
            environment=environment,
            release=release,
            traces_sample_rate=traces_sample_rate,
            profiles_sample_rate=profiles_sample_rate,
            integrations=sdk_integrations,
            send_default_pii=False,
            max_breadcrumbs=50,
            attach_stacktrace=True,
            before_send=_filter_sensitive_data
        )

        logger.info("Sentry error tracking initialized successfully")
        return sentry_sdk.Hub.current.client

    except Exception as e:
        logger.error(f"Failed to initialize Sentry: {e}")
        return None

def _filter_sensitive_data(event: Dict[str, Any], hint: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    if not isinstance(event, dict):
        return None

    sensitive_paths = ['/home/', '/Users/', 'C:\\Users\\']

    if 'exception' in event:
        try:
            exception_value = event['exception']['values'][0]
            stacktrace = exception_value.get('stacktrace', {})
            frames = stacktrace.get('frames', [])
            
            filtered_frames = [
                frame for frame in frames
                if not any(sensitive in str(frame.get('filename', '')) for sensitive in sensitive_paths)
            ]
            
            if filtered_frames:
                exception_value['stacktrace']['frames'] = filtered_frames
        except (KeyError, IndexError, AttributeError):
            pass

    if isinstance(event.get('request'), dict):
        request = event['request']
        sensitive_headers = {'authorization', 'cookie', 'x-api-key'}
        
        if 'headers' in request:
            request['headers'] = {
                k: '**masked**' if k.lower() in sensitive_headers else v
                for k, v in request['headers'].items()
            }
        
        if 'query_string' in request:
            request['query_string'] = '**masked**'

    return event

def add_sentry_context(
    user_id: Optional[str] = None,
    email: Optional[str] = None,
    extra_context: Optional[Dict[str, Any]] = None
) -> None:
    import sentry_sdk
    
    if not sentry_sdk.Hub.current.client:
        return

    with sentry_sdk.configure_scope() as scope:
        if user_id or email:
            scope.set_user({"id": user_id, "email": email})
        if extra_context:
            for key, value in extra_context.items():
                scope.set_extra(key, value)

def capture_exception(
    exc: Optional[Exception] = None,
    message: Optional[str] = None,
    extra: Optional[Dict[str, Any]] = None
) -> Optional[str]:
    import sentry_sdk
    
    if not sentry_sdk.Hub.current.client:
        return None

    if exc:
        return sentry_sdk.capture_exception(exc)
    if message:
        return sentry_sdk.capture_message(message, level='error', extras=extra)
    return None

def capture_message(
    message: str,
    level: str = 'info',
    extra: Optional[Dict[str, Any]] = None
) -> Optional[str]:
    import sentry_sdk
    
    if not sentry_sdk.Hub.current.client or not message:
        return None

    return sentry_sdk.capture_message(message, level=level, extras=extra)