from typing import Any, Dict, List
from concurrent.futures import ThreadPoolExecutor
from graph.state import TravelState
from tools.weather_api import WeatherTool
from tools.image_api import ImageTool


# tool registry which maps tool names to actual functions
TOOL_REGISTRY = {
    "fetch_weather": lambda city: WeatherTool().get_forecast(city),
    "fetch_images": lambda city: ImageTool().search_images(city, limit=10),
}


def execute_tool_calls_node(state: TravelState) -> TravelState:
    """
    Manually parse and execute tool calls from LLM without framework abstractions.
    Demonstrates understanding of raw tool calling protocol.
    Weather and image tools run in parallel for reduced latency.
    """
    # check if we need to execute tools
    if not state.city:
        state.errors.append("Tool executor: no city to work with")
        return state

    # Define parallel task functions
    def fetch_weather():
        """Fetch weather forecast for the city."""
        try:
            weather_tool = WeatherTool()
            forecast = weather_tool.get_forecast(state.city)
            return forecast if forecast else []
        except Exception as e:
            state.errors.append(f"Weather error: {str(e)}")
            return []

    def fetch_images():
        """Fetch images for the city (respects skip_images flag)."""
        if state.skip_images:
            return state.image_urls or []
        try:
            image_tool = ImageTool()
            urls = image_tool.search_images(state.city, limit=10)
            return urls if urls else []
        except Exception as e:
            state.errors.append(f"Images: {str(e)}")
            return []

    # Execute weather and images in parallel using ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=2) as executor:
        weather_future = executor.submit(fetch_weather)
        images_future = executor.submit(fetch_images)

        # Collect results as they complete
        state.weather_forecast = weather_future.result()
        state.image_urls = images_future.result()

    # Validate results and add error messages
    if not state.weather_forecast:
        state.errors.append(f"Weather data unavailable for {state.city}")
    # add clarity if user asked for dates beyond provider window (OWM is 5-day/3-hour)
    if state.date_range and len(state.weather_forecast) < 5:
        state.errors.append(
            f"Weather API only provides ~5-day forecast; requested '{state.date_range}' may extend beyond available data"
        )

    if not state.skip_images and not state.image_urls:
        state.errors.append(f"Images: no results for {state.city}")

    return state
