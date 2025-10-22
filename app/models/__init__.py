"""Database models and API schemas."""

from .analytics import (
    SearchMetric,
    SearchMetricCreate,
    SearchMetricRead,
    WebMetric,
    WebMetricCreate,
    WebMetricRead,
)
from .automation import AutomationRule, AutomationRuleCreate, AutomationRuleRead
from .content import (
    ContentDispatchResponse,
    ContentItem,
    ContentItemCreate,
    ContentItemRead,
)
from .osint import OSINTEvent, OSINTEventCreate, OSINTEventRead, OSINTSummary
from .seo import MetadataPatch, SEOReport, SEOReportCreate, SEOReportRead

__all__ = [
    "AutomationRule",
    "AutomationRuleCreate",
    "AutomationRuleRead",
    "ContentItem",
    "ContentItemCreate",
    "ContentItemRead",
    "ContentDispatchResponse",
    "OSINTEvent",
    "OSINTEventCreate",
    "OSINTEventRead",
    "OSINTSummary",
    "MetadataPatch",
    "SEOReport",
    "SEOReportCreate",
    "SEOReportRead",
    "WebMetric",
    "WebMetricCreate",
    "WebMetricRead",
    "SearchMetric",
    "SearchMetricCreate",
    "SearchMetricRead",
]
