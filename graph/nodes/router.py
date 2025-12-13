from graph.state import TravelState


def router_node(state: TravelState) -> TravelState:
	"""decide retrieval route: vector for ingested cities, else web"""
	if not state.city:
		state.route = "web"
		return state
	city_norm = state.city.strip().lower()
	prepopulated = {"paris", "tokyo", "new york"}
	state.route = "vector" if city_norm in prepopulated else "web"
	return state

