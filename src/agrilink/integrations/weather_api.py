"""Weather API integration."""

import logging
from typing import Any, Dict, Optional

import httpx

from agrilink.config import get_settings

logger = logging.getLogger(__name__)


async def get_weather_forecast(region: str, days: int = 3) -> Dict[str, Any]:
    """
    Get weather forecast for a region using the configured provider.
    
    Args:
        region: City or region name
        days: Number of forecast days
        
    Returns:
        Dictionary with weather data
    """
    settings = get_settings()
    
    if settings.weather_api_provider == "weatherapi":
        return await _get_weatherapi_forecast(region, days, settings.weatherapi_key)
    elif settings.weather_api_provider == "openweathermap":
        # Placeholder for OpenWeatherMap implementation
        logger.warning("OpenWeatherMap integration not yet implemented")
        return {"error": "Provider not implemented"}
    else:
        logger.warning(f"Unknown weather provider: {settings.weather_api_provider}")
        return {"error": "Unknown provider"}


async def _get_weatherapi_forecast(region: str, days: int, api_key: str) -> Dict[str, Any]:
    """Get forecast from WeatherAPI.com."""
    if not api_key:
        logger.error("WeatherAPI key not configured")
        return {"error": "API key missing"}
        
    url = "http://api.weatherapi.com/v1/forecast.json"
    params = {
        "key": api_key,
        "q": region,
        "days": days,
        "aqi": "no",
        "alerts": "no",
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=10.0)
            
            if response.status_code == 200:
                data = response.json()
                
                # Format into a simplified structure for the agent
                forecast = {
                    "location": data.get("location", {}),
                    "current": {
                        "temp_c": data.get("current", {}).get("temp_c"),
                        "condition": data.get("current", {}).get("condition", {}).get("text"),
                        "humidity": data.get("current", {}).get("humidity"),
                        "wind_kph": data.get("current", {}).get("wind_kph"),
                        "precip_mm": data.get("current", {}).get("precip_mm"),
                    },
                    "forecast": []
                }
                
                for day in data.get("forecast", {}).get("forecastday", []):
                    forecast["forecast"].append({
                        "date": day.get("date"),
                        "max_temp_c": day.get("day", {}).get("maxtemp_c"),
                        "min_temp_c": day.get("day", {}).get("mintemp_c"),
                        "condition": day.get("day", {}).get("condition", {}).get("text"),
                        "chance_of_rain": day.get("day", {}).get("daily_chance_of_rain"),
                        "precip_mm": day.get("day", {}).get("totalprecip_mm"),
                    })
                    
                return forecast
            else:
                logger.error(f"WeatherAPI error: {response.status_code} - {response.text}")
                return {"error": f"API Error: {response.status_code}"}
                
    except Exception as e:
        logger.error(f"Error fetching weather data: {e}")
        return {"error": f"Connection error: {str(e)}"}
