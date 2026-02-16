"""Event type definitions and Pydantic models."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class EventType(str, Enum):
    """Event types in the AgriLink system."""
    
    # User actions
    USER_QUERY = "user_query"
    FARMER_QUERY = "farmer_query"
    LISTING_CREATED = "listing_created"
    ORDER_PLACED = "order_placed"
    PURCHASE_REQUEST = "purchase_request"
    
    # External API updates
    WEATHER_UPDATE = "weather_update"
    WEATHER_ALERT = "weather_alert"
    PRICE_UPDATE = "price_update"
    MARKET_UPDATE = "market_update"
    
    # System events
    DELIVERY_DELAY = "delivery_delay"
    LOGISTICS_ISSUE = "logistics_issue"
    ORDER_UPDATE = "order_update"
    THRESHOLD_EXCEEDED = "threshold_exceeded"
    ANOMALY_DETECTED = "anomaly_detected"
    
    # Agent events
    AGENT_RESPONSE = "agent_response"
    ORCHESTRATION_COMPLETE = "orchestration_complete"


class EventPriority(str, Enum):
    """Event priority levels."""
    
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class BaseEvent(BaseModel):
    """Base event model."""
    
    event_id: str = Field(description="Unique event identifier")
    event_type: EventType = Field(description="Type of event")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    priority: EventPriority = Field(default=EventPriority.MEDIUM)
    source: str = Field(description="Event source (e.g., 'user', 'weather_api', 'system')")
    user_id: Optional[str] = Field(default=None, description="Associated user ID")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        use_enum_values = True


class UserQueryEvent(BaseEvent):
    """User query event."""
    
    event_type: EventType = EventType.USER_QUERY
    query: str = Field(description="User's question or query")
    crop: Optional[str] = None
    region: Optional[str] = None
    context: Dict[str, Any] = Field(default_factory=dict)


class FarmerQueryEvent(BaseEvent):
    """Farmer-specific query event."""
    
    event_type: EventType = EventType.FARMER_QUERY
    question: str
    crop: Optional[str] = None
    region: Optional[str] = None
    season: Optional[str] = None
    farm_size: Optional[float] = None


class WeatherUpdateEvent(BaseEvent):
    """Weather update event."""
    
    event_type: EventType = EventType.WEATHER_UPDATE
    region: str
    forecast: Dict[str, Any]
    crop: Optional[str] = None
    growth_stage: Optional[str] = None


class WeatherAlertEvent(BaseEvent):
    """Weather alert event."""
    
    event_type: EventType = EventType.WEATHER_ALERT
    priority: EventPriority = EventPriority.HIGH
    alert_type: str  # e.g., "heavy_rain", "frost", "heatwave"
    region: str
    severity: str  # e.g., "warning", "watch", "advisory"
    affected_crops: list[str] = Field(default_factory=list)
    forecast: Dict[str, Any]


class PriceUpdateEvent(BaseEvent):
    """Market price update event."""
    
    event_type: EventType = EventType.PRICE_UPDATE
    crop: str
    region: str
    price: float
    unit: str  # e.g., "per_kg", "per_quintal"
    change_percent: Optional[float] = None
    market_name: Optional[str] = None


class OrderEvent(BaseEvent):
    """Order-related event."""
    
    event_type: EventType = EventType.ORDER_PLACED
    order_id: str
    crop: str
    quantity: float
    origin: str
    destination: str
    buyer_id: str
    seller_id: str


class LogisticsEvent(BaseEvent):
    """Logistics-related event."""
    
    event_type: EventType = EventType.LOGISTICS_ISSUE
    priority: EventPriority = EventPriority.HIGH
    order_id: str
    issue_description: str
    current_status: str
    origin: str
    destination: str
    crop: Optional[str] = None


class PurchaseRequestEvent(BaseEvent):
    """Purchase request event."""
    
    event_type: EventType = EventType.PURCHASE_REQUEST
    crop: str
    quantity: float
    quality_grade: str = "standard"
    region: str
    asking_price: Optional[float] = None
    buyer_id: str


class AgentResponseEvent(BaseEvent):
    """Agent response event."""
    
    event_type: EventType = EventType.AGENT_RESPONSE
    agent_name: str
    recommendation: str
    confidence: float
    reasoning: str
    sources: list[Dict[str, Any]] = Field(default_factory=list)
    original_event_id: str


def create_event(event_type: EventType, **kwargs) -> BaseEvent:
    """
    Factory function to create events.
    
    Args:
        event_type: Type of event to create
        **kwargs: Event-specific parameters
        
    Returns:
        Appropriate event instance
    """
    event_classes = {
        EventType.USER_QUERY: UserQueryEvent,
        EventType.FARMER_QUERY: FarmerQueryEvent,
        EventType.WEATHER_UPDATE: WeatherUpdateEvent,
        EventType.WEATHER_ALERT: WeatherAlertEvent,
        EventType.PRICE_UPDATE: PriceUpdateEvent,
        EventType.ORDER_PLACED: OrderEvent,
        EventType.LOGISTICS_ISSUE: LogisticsEvent,
        EventType.PURCHASE_REQUEST: PurchaseRequestEvent,
        EventType.AGENT_RESPONSE: AgentResponseEvent,
    }
    
    event_class = event_classes.get(event_type, BaseEvent)
    return event_class(event_type=event_type, **kwargs)
