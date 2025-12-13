from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from graph.state import TravelState
from graph.nodes.parse_query import parse_query_node
from graph.nodes.router import router_node
from graph.nodes.city_summary_vector import city_summary_vector_node
from graph.nodes.city_summary_web import city_summary_web_node
from graph.nodes.weather import weather_node
from graph.nodes.images import images_node
from graph.nodes.final_assembly_node import final_assembly_node
from graph.nodes.tool_executor import execute_tool_calls_node


def _routing_function(state: TravelState) -> str:
	"""Return vector for pre ingested cities, else web"""
	if not state.city:
		return "web"
	# Skip summary if same city as before
	if state.skip_summary:
		return "skip"
	city_norm = state.city.strip().lower()
	prepopulated = {"paris", "tokyo", "new york"}
	return "vector" if city_norm in prepopulated else "web"


def build_app(enable_checkpointer=True):
	graph = StateGraph(TravelState)

	# nodes
	graph.add_node("parse", parse_query_node)
	graph.add_node("router", router_node)
	graph.add_node("vector_summary", city_summary_vector_node)
	graph.add_node("web_summary", city_summary_web_node)
	
	# distinction 1: Manual tool executor (replaces weather + images nodes)
	graph.add_node("tools", execute_tool_calls_node)
	
	graph.add_node("final", final_assembly_node)

	# flow
	graph.set_entry_point("parse")
	graph.add_edge("parse", "router")
	graph.add_conditional_edges(
		"router",
		_routing_function,
		{"vector": "vector_summary", "web": "web_summary", "skip": "tools"},
	)

	# distinction 2: Parallel fan-out - both summary paths lead to tools node
	# the tools node executes weather and images in parallel internally
	graph.add_edge("vector_summary", "tools")
	graph.add_edge("web_summary", "tools")

	# sequential to final
	graph.add_edge("tools", "final")
	graph.add_edge("final", END)

	# distinction 3: Human-in-the-loop with checkpointer for time travel
	if enable_checkpointer:
		memory = MemorySaver()
		return graph.compile(checkpointer=memory)
	
	return graph.compile()