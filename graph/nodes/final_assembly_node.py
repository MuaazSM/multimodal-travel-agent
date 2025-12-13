from graph.state import TravelState


def final_assembly_node(state: TravelState):

    # Track the current city for the next query (context preservation)
    state.previous_city = state.city

    # city presence is fundamental for rendering context
    if not state.city:
        state.errors.append("Final: city is missing from state")

    # summary fallback
    if not state.city_summary or not state.city_summary.strip():
        city_label = state.city or "the city"
        state.city_summary = (
            f"Summary for {city_label} isn't available right now. Key highlights: weather shown below; images provided."
        )
        state.errors.append("Final: missing city summary; using a default message")

    # weather fallback
    if not isinstance(state.weather_forecast, list) or len(state.weather_forecast) == 0:
        state.weather_forecast = []
        state.errors.append("Final: weather data unavailable; showing no forecast")

    # images fallback
    if not isinstance(state.image_urls, list) or len(state.image_urls) == 0:
        state.image_urls = []
        state.errors.append("Final: no images found; showing an empty list")

    return state
