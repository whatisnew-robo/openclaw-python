"""
Monitoring module for ClawdBot
"""
from .health import (
    HealthCheck,
    HealthStatus,
    ComponentHealth,
    HealthCheckResponse,
    get_health_check,
    register_health_check
)
from .metrics import (
    MetricsCollector,
    Counter,
    Gauge,
    Histogram,
    Timer,
    get_metrics,
    counter,
    gauge,
    histogram
)
from .logger import (
    setup_logging,
    get_logger,
    JSONFormatter,
    ColoredFormatter,
    LogContext,
    log_with_context
)

__all__ = [
    # Health
    "HealthCheck",
    "HealthStatus",
    "ComponentHealth",
    "HealthCheckResponse",
    "get_health_check",
    "register_health_check",
    # Metrics
    "MetricsCollector",
    "Counter",
    "Gauge",
    "Histogram",
    "Timer",
    "get_metrics",
    "counter",
    "gauge",
    "histogram",
    # Logging
    "setup_logging",
    "get_logger",
    "JSONFormatter",
    "ColoredFormatter",
    "LogContext",
    "log_with_context",
]
