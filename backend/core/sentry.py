"""
Sentry Configuration and Integration Module

Provides centralized configuration and initialization 
for error tracking and performance monitoring with Sentry.
"""

import os
import logging
import sentry_sdk
from typing import Optional, List, Any

logger = logging.getLogger(__name__)

def configure_sentry(
    dsn: Optional[str] = None, 
    environment: str = 'development', 
    release: str = '0.2.0',
    traces_sample_rate: float = 0.1,
    profiles_sample_rate: float = 0.1,
    integrations: Optional[List[Any]] = None
):
    """
    Configure and initialize Sentry SDK
    
    Args:
        dsn: Sentry Data Source Name
        environment: Deployment environment
        release: Application release version
        traces_sample_rate: Percentage of transactions to send to Sentry
        profiles_sample_rate: Percentage of performance profiles to send
        integrations: Optional list of additional integrations
    
    Returns:
        Configured Sentry SDK instance or None
    """
    # Use environment variable if no DSN is provided
    sentry_dsn = dsn or os.getenv('MODHUB_SENTRY_DSN')
    
    if not sentry_dsn:
        logger.warning("No Sentry DSN provided. Error tracking is disabled.")
        return None
    
    try:
        # Prepare integrations
        sdk_integrations = []
        
        # Try to import and add FastAPI integration if available
        try:
            from sentry_sdk.integrations.fastapi import FastAPIIntegration
            sdk_integrations.append(FastAPIIntegration())
        except (ImportError, AttributeError):
            logger.warning("FastAPI integration for Sentry could not be loaded")
        
        # Try to add SQLAlchemy integration
        try:
            from sentry_sdk.integrations.sqlalchemy import SqlAlchemyIntegration
            sdk_integrations.append(SqlAlchemyIntegration())
        except (ImportError, AttributeError):
            logger.warning("SQLAlchemy integration for Sentry could not be loaded")
        
        # Try to add logging integration
        try:
            from sentry_sdk.integrations.logging import LoggingIntegration
            import logging
            sentry_logging = LoggingIntegration(
                level=logging.INFO,       # Capture logs at INFO level and above
                event_level=logging.ERROR  # Send error logs as events
            )
            sdk_integrations.append(sentry_logging)
        except (ImportError, AttributeError):
            logger.warning("Logging integration for Sentry could not be loaded")
        
        # Add any additional user-provided integrations
        if integrations:
            sdk_integrations.extend(integrations)
        
        # Initialize Sentry SDK
        sentry_sdk.init(
            dsn=sentry_dsn,
            environment=environment,
            release=release,
            
            # Performance and error tracking
            traces_sample_rate=traces_sample_rate,
            profiles_sample_rate=profiles_sample_rate,
            
            # Integrations
            integrations=sdk_integrations,
            
            # Additional configuration
            send_default_pii=False,  # Disable sending of personal identifiable information
            max_breadcrumbs=50,  # Maximum number of breadcrumbs to capture
            attach_stacktrace=True,  # Attach stacktrace to error events
            
            # Error filtering
            before_send=_filter_sensitive_data
        )
        
        logger.info("Sentry error tracking initialized successfully")
        return sentry_sdk
    
    except Exception as e:
        logger.error(f"Failed to initialize Sentry: {e}")
        return None

def _filter_sensitive_data(event, hint):
    """
    Filter out sensitive data before sending to Sentry
    
    Args:
        event: Event dictionary to be sent
        hint: Additional information about the event
    
    Returns:
        Processed event or None to drop the event
    """
    # Remove sensitive paths from stacktrace
    if 'exception' in event and 'stacktrace' in event['exception']:
        frames = event['exception']['stacktrace'].get('frames', [])
        filtered_frames = [
            frame for frame in frames 
            if not any(sensitive in frame.get('filename', '') for sensitive in [
                '/home/', '/Users/', 'C:\\Users\\'  # User home directories
            ])
        ]
        event['exception']['stacktrace']['frames'] = filtered_frames
    
    # Remove or mask certain sensitive keys
    if 'request' in event:
        # Mask sensitive headers and query parameters
        sensitive_headers = ['authorization', 'cookie', 'x-api-key']
        if 'headers' in event['request']:
            event['request']['headers'] = {
                k: '**masked**' if k.lower() in sensitive_headers else v 
                for k, v in event['request'].get('headers', {}).items()
            }
        
        # Mask sensitive query parameters
        if 'query_string' in event['request']:
            event['request']['query_string'] = '**masked**'
    
    return event

def add_sentry_context(
    user_id: Optional[str] = None, 
    email: Optional[str] = None, 
    extra_context: Optional[dict] = None
):
    """
    Add additional context to Sentry events
    
    Args:
        user_id: User identifier
        email: User email
        extra_context: Additional custom context
    """
    if not sentry_sdk.Hub.current.client:
        return
    
    with sentry_sdk.configure_scope() as scope:
        # Set user context if available
        if user_id or email:
            scope.set_user({
                "id": user_id,
                "email": email
            })
        
        # Add extra context
        if extra_context:
            for key, value in extra_context.items():
                scope.set_extra(key, value)

def capture_exception(
    exc: Optional[Exception] = None, 
    message: Optional[str] = None, 
    extra: Optional[dict] = None
):
    """
    Capture an exception or custom error
    
    Args:
        exc: Exception object
        message: Custom error message
        extra: Additional context
    
    Returns:
        Sentry event ID
    """
    if not sentry_sdk.Hub.current.client:
        return None
    
    if exc:
        return sentry_sdk.capture_exception(exc)
    
    if message:
        return sentry_sdk.capture_message(
            message, 
            level='error',
            extras=extra
        )

def capture_message(
    message: str, 
    level: str = 'info', 
    extra: Optional[dict] = None
):
    """
    Capture a custom message
    
    Args:
        message: Message to capture
        level: Logging level (default: info)
        extra: Additional context
    
    Returns:
        Sentry event ID
    """
    if not sentry_sdk.Hub.current.client:
        return None
    
    return sentry_sdk.capture_message(
        message, 
        level=level,
        extras=extra
    )