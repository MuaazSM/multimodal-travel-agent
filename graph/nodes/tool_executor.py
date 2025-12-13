from typing import Any, Dict, List
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
    """
    # check if we need to execute tools
    if not state.city:
        state.errors.append("Tool executor: no city to work with")
        return state

    # execute weather tool
    try:
        weather_tool = WeatherTool()
        forecast = weather_tool.get_forecast(state.city)
        state.weather_forecast = forecast if forecast else []
        if not state.weather_forecast:
            state.errors.append(f"Weather data unavailable for {state.city}")
        # add clarity if user asked for dates beyond provider window (OWM is 5-day/3-hour)
        if state.date_range and len(state.weather_forecast) < 5:
            state.errors.append(
                f"Weather API only provides 5-day forecast; requested '{state.date_range}' may extend beyond available data"
            )
    except Exception as e:
        state.weather_forecast = []
        state.errors.append(f"Weather error: {str(e)}")

    # execute image tool (skip if city unchanged)
    if not state.skip_images:
        try:
            image_tool = ImageTool()
            urls = image_tool.search_images(state.city, limit=10)
            state.image_urls = urls if urls else []
            if not state.image_urls:
                state.errors.append(f"Images: no results for {state.city}")
        except Exception as e:
            state.image_urls = []
            state.errors.append(f"Images: {str(e)}")
    else:
        # preserve existing images (if any) on skip
        state.image_urls = state.image_urls or []

    return state
