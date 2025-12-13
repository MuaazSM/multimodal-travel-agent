# test_weather.py
"""Test script for weather functionality"""

from tools.weather_api import WeatherTool
from graph.state import TravelState
from graph.nodes.weather import weather_node
import os

def test_weather_tool():
    """Test the weather tool directly"""
    print("="*60)
    print("Testing Weather Tool")
    print("="*60)
    
    tool = WeatherTool()
    
    # Test with a few cities
    cities = ["Paris", "Tokyo", "New York"]
    
    for city in cities:
        print(f"\n{city}:")
        forecast = tool.get_forecast(city)
        
        if forecast:
            print(f"  Got {len(forecast)} days of forecast")
            # Show first day
            print(f"  {forecast[0]['date']}: {forecast[0]['temp_min']}°C - {forecast[0]['temp_max']}°C")
            print(f"  Conditions: {forecast[0]['description']}")
        else:
            print("  No forecast available")

def test_weather_node():
    """Test the weather node"""
    print("\n" + "="*60)
    print("Testing Weather Node")
    print("="*60)
    
    # Create test state
    state = TravelState(
        user_query="What's the weather in Paris?",
        city="Paris"
    )
    
    # Run node
    result = weather_node(state)
    
    # Display results
    print(f"\nCity: {result.city}")
    print(f"Forecast days: {len(result.weather_forecast)}")
    
    if result.weather_forecast:
        print("\nForecast:")
        for day in result.weather_forecast:
            print(f"  {day['date']}: {day['temp_min']}°C to {day['temp_max']}°C - {day['description']}")
    
    if result.errors:
        print(f"\nErrors: {result.errors}")

def test_geocoding():
    """Test geocoding specifically"""
    print("\n" + "="*60)
    print("Testing Geocoding")
    print("="*60)
    
    tool = WeatherTool()
    
    cities = ["Paris", "Tokyo", "New York", "InvalidCity123"]
    
    for city in cities:
        lat, lon = tool._geocode_city(city)
        if lat and lon:
            print(f"{city}: {lat}, {lon}")
        else:
            print(f"{city}: Could not geocode")

if __name__ == "__main__":
    # Check API key
    if not os.getenv("OPENWEATHER_API_KEY"):
        print("Error: OPENWEATHER_API_KEY not found")
        print("Get your free key at: https://openweathermap.org/api")
        exit(1)
    
    # Run tests
    test_geocoding()
    print("\n")
    test_weather_tool()
    print("\n")
    test_weather_node()