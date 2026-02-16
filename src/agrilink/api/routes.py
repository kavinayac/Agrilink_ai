"""REST API endpoints for AgriLink."""

import logging
import uuid
from typing import Dict

from fastapi import APIRouter, HTTPException

from agrilink.api.models import (
    LogisticsRequest,
    MarketInsightRequest,
    PriceRecommendationRequest,
    QueryRequest,
    QueryResponse,
    WeatherRiskRequest,
)
from agrilink.events.bus import publish_event
from agrilink.events.router import get_event_router
from agrilink.events.schema import (
    EventPriority,
    FarmerQueryEvent,
    LogisticsEvent,
    PurchaseRequestEvent,
    UserQueryEvent,
    WeatherUpdateEvent,
    create_event,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["api"])


@router.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest) -> QueryResponse:
    """
    Process a user query and return an answer.
    
    This endpoint creates a query event, routes it to appropriate agents,
    and returns the orchestrated response.
    """
    query_id = str(uuid.uuid4())
    
    # Create query event
    event = UserQueryEvent(
        event_id=query_id,
        source="api",
        user_id=request.user_id,
        query=request.query,
        crop=request.crop,
        region=request.region,
        context=request.context,
    )
    
    # Publish event (for async processing and logging)
    await publish_event(event)
    
    # Also get immediate response
    router_instance = get_event_router()
    response = await router_instance.route_and_orchestrate(event)
    
    if not response:
        raise HTTPException(
            status_code=500,
            detail="Failed to generate response from agents",
        )
    
    return QueryResponse(
        query_id=query_id,
        answer=response.recommendation,
        confidence=response.confidence,
        sources=response.sources,
        agent_name=response.agent_name,
        reasoning=response.reasoning,
        metadata=response.metadata,
    )


@router.post("/farmer/query", response_model=QueryResponse)
async def farmer_query(request: QueryRequest) -> QueryResponse:
    """
    Process a farmer-specific query.
    
    This endpoint is optimized for farmer advisory questions.
    """
    query_id = str(uuid.uuid4())
    
    event = FarmerQueryEvent(
        event_id=query_id,
        source="api",
        user_id=request.user_id,
        question=request.query,
        crop=request.crop,
        region=request.region,
        season=request.season,
    )
    
    await publish_event(event)
    
    router_instance = get_event_router()
    response = await router_instance.route_and_orchestrate(event)
    
    if not response:
        raise HTTPException(
            status_code=500,
            detail="Failed to generate farmer advisory response",
        )
    
    return QueryResponse(
        query_id=query_id,
        answer=response.recommendation,
        confidence=response.confidence,
        sources=response.sources,
        agent_name=response.agent_name,
        reasoning=response.reasoning,
        metadata=response.metadata,
    )


@router.post("/market/insights")
async def get_market_insights(request: MarketInsightRequest) -> Dict:
    """Get market intelligence insights for a crop and region."""
    query_id = str(uuid.uuid4())
    
    # Create a query event for market intelligence
    event = UserQueryEvent(
        event_id=query_id,
        source="api",
        user_id=request.user_id,
        query=f"Market analysis for {request.crop} in {request.region}",
        crop=request.crop,
        region=request.region,
        context={"action": request.action},
    )
    
    await publish_event(event)
    
    router_instance = get_event_router()
    response = await router_instance.route_and_orchestrate(event)
    
    if not response:
        raise HTTPException(status_code=500, detail="Failed to get market insights")
    
    return {
        "crop": request.crop,
        "region": request.region,
        "insights": response.recommendation,
        "confidence": response.confidence,
        "sources": response.sources,
    }


@router.post("/buyer/pricing")
async def get_pricing_recommendation(request: PriceRecommendationRequest) -> Dict:
    """Get buyer pricing strategy and recommendations."""
    query_id = str(uuid.uuid4())
    
    try:
        event = PurchaseRequestEvent(
            event_id=query_id,
            source="api",
            user_id=request.user_id,
            buyer_id=request.user_id,
            crop=request.crop,
            quantity=request.quantity,
            quality_grade=request.quality_grade,
            region=request.region,
            asking_price=request.asking_price,
        )
        
        await publish_event(event)
        
        router_instance = get_event_router()
        response = await router_instance.route_and_orchestrate(event)
        
        if not response:
            raise HTTPException(status_code=500, detail="Failed to get pricing recommendation - No response from agents")
        
        return {
            "crop": request.crop,
            "quantity": request.quantity,
            "recommendation": response.recommendation,
            "confidence": response.confidence,
            "sources": response.sources,
        }
    except Exception as e:
        logger.exception("Error in buyer pricing endpoint")
        raise HTTPException(status_code=500, detail=f"Failed to get pricing recommendation: {str(e)}")


from agrilink.integrations.weather_api import get_weather_forecast

@router.post("/weather/risk")
async def assess_weather_risk(request: WeatherRiskRequest) -> Dict:
    """Assess weather-related risks for a crop."""
    query_id = str(uuid.uuid4())
    
    # Fetch actual weather forecast
    try:
        forecast_data = await get_weather_forecast(request.region)
    except Exception as e:
        logger.error(f"Failed to fetch weather: {e}")
        forecast_data = {"error": "Weather data unavailable"}

    event = WeatherUpdateEvent(
        event_id=query_id,
        source="api",
        user_id=request.user_id,
        region=request.region,
        crop=request.crop,
        growth_stage=request.growth_stage,
        forecast=forecast_data,
    )
    
    await publish_event(event)
    
    router_instance = get_event_router()
    response = await router_instance.route_and_orchestrate(event)
    
    if not response:
        raise HTTPException(status_code=500, detail="Failed to assess weather risk")
    
    return {
        "crop": request.crop,
        "region": request.region,
        "risk_assessment": response.recommendation,
        "confidence": response.confidence,
        "sources": response.sources,
    }


@router.post("/logistics/optimize")
async def optimize_logistics(request: LogisticsRequest) -> Dict:
    """Get logistics optimization recommendations."""
    query_id = str(uuid.uuid4())
    
    event = LogisticsEvent(
        event_id=query_id,
        source="api",
        user_id=request.user_id,
        order_id=request.order_id,
        origin=request.origin,
        destination=request.destination,
        crop=request.crop,
        current_status="pending",
        issue_description="",
    )
    
    await publish_event(event)
    
    router_instance = get_event_router()
    response = await router_instance.route_and_orchestrate(event)
    
    if not response:
        raise HTTPException(status_code=500, detail="Failed to optimize logistics")
    
    return {
        "order_id": request.order_id,
        "optimization": response.recommendation,
        "confidence": response.confidence,
        "sources": response.sources,
    }
