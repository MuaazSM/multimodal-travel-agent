from graph.state import TravelState
from tools.weather_api import WeatherTool

def weather_node(state):
    try:
        weather_tool = WeatherTool()

        print(f"Fetching weather for {state.city}...")
        forecast = weather_tool.get_forecast(state.city)

        state.weather_forecast = forecast
        if forecast:
            print(f"Got {len(forecast)} days of forecast")
        else:
            print("No weather data available")
            state.errors.append(f"Weather data unavailable for {state.city}")

    except Exception as e:
        # handle any errors gracefully
        print(f"Weather node error: {e}")
        state.weather_forecast = []
        state.errors.append(f"Weather error: {str(e)}")
    
    return state