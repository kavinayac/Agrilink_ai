"""Pydantic models for API request/response validation."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """Request model for user queries."""
    
    query: str = Field(description="User's question or query")
    user_id: str = Field(description="User identifier")
    crop: Optional[str] = Field(default=None, description="Crop type")
    region: Optional[str] = Field(default=None, description="Geographic region")
    season: Optional[str] = Field(default=None, description="Current season")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context")


class QueryResponse(BaseModel):
    """Response model for queries."""
    
    query_id: str = Field(description="Query identifier")
    answer: str = Field(description="Answer to the query")
    confidence: float = Field(description="Confidence score (0.0 to 1.0)")
    sources: List[Dict[str, Any]] = Field(description="Source documents")
    agent_name: str = Field(description="Name of the responding agent")
    reasoning: str = Field(description="Reasoning behind the answer")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MarketInsightRequest(BaseModel):
    """Request model for market insights."""
    
    crop: str = Field(description="Crop type")
    region: str = Field(description="Geographic region")
    action: str = Field(default="analyze", description="Action type (buy/sell/analyze)")
    user_id: str


class PriceRecommendationRequest(BaseModel):
    """Request model for pricing recommendations."""
    
    crop: str
    quantity: float
    quality_grade: str = "standard"
    region: str
    user_id: str
    asking_price: Optional[float] = None


class WeatherRiskRequest(BaseModel):
    """Request model for weather risk assessment."""
    
    crop: str
    region: str
    growth_stage: str = "unknown"
    user_id: str


class LogisticsRequest(BaseModel):
    """Request model for logistics optimization."""
    
    order_id: str
    origin: str
    destination: str
    crop: str
    quantity: float
    user_id: str


class HealthResponse(BaseModel):
    """Health check response."""
    
    status: str
    service: str
    version: str
    environment: str
