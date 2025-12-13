from graph.state import TravelState
from tools.image_api import ImageTool


def images_node(state: TravelState) -> TravelState:
    try:
        if not state.city:
            state.errors.append("Images: city is missing")
            state.image_urls = []
            return state

        tool = ImageTool()
        urls = tool.search_images(state.city, limit=10)
        state.image_urls = urls or []
        if not state.image_urls:
            state.errors.append(f"Images: no results for {state.city}")
        return state
    except Exception as e:
        state.errors.append(f"Images: {e}")
        state.image_urls = []
        return state
