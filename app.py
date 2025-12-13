import streamlit as st
from typing import Any, Dict, List
import uuid

from graph.build_graph import build_app
from graph.output_schema import TravelOutput
from graph.state import TravelState


st.set_page_config(page_title="Multimodal Travel Agent", layout="wide")
st.title("Multimodal Travel Agent")


def get_graph():
	if "app_graph" not in st.session_state:
		st.session_state["app_graph"] = build_app(enable_checkpointer=True)
	return st.session_state["app_graph"]


def get_thread_id():
	"""Get or create a thread ID for conversation persistence"""
	if "thread_id" not in st.session_state:
		import uuid
		st.session_state["thread_id"] = str(uuid.uuid4())
	return st.session_state["thread_id"]


def to_output_schema(state: TravelState) -> TravelOutput:
	# Convert weather dicts to strings for simple rendering
	weather_strs: List[str] = []
	for d in state.weather_forecast or []:
		try:
			weather_strs.append(
				f"{d.get('date','')}: {d.get('temp_min','?')}°C - {d.get('temp_max','?')}°C ({d.get('description','')})"
			)
		except Exception:
			# fallback to string representation
			weather_strs.append(str(d))

	return TravelOutput(
		city_summary=state.city_summary or "",
		weather_forecast=weather_strs,
		image_urls=state.image_urls or [],
		date_range=state.date_range or "",
	)


# Conversation history display
if "conversation_history" not in st.session_state:
	st.session_state["conversation_history"] = []

with st.sidebar:
	st.header("Conversation History")
	if st.button("🔄 New Conversation"):
		if "thread_id" in st.session_state:
			del st.session_state["thread_id"]
		st.session_state["conversation_history"] = []
		st.rerun()
	
	st.divider()
	for idx, msg in enumerate(st.session_state["conversation_history"]):
		with st.expander(f"Query {idx + 1}: {msg.get('query', '')[:30]}..."):
			st.write(f"**City:** {msg.get('city', 'N/A')}")
			st.write(f"**Dates:** {msg.get('date_range') or 'N/A'}")
			st.write(f"**Weather Days:** {msg.get('weather_count', 0)}")
			st.write(f"**Images:** {msg.get('image_count', 0)}")

query = st.text_input("Ask about a city", placeholder="e.g., What's the weather in Paris next week?")

if query:
	graph = get_graph()
	thread_id = get_thread_id()
	
	# distinction 3: used checkpointer for context preservation
	config = {"configurable": {"thread_id": thread_id}}
	result = graph.invoke({"user_query": query}, config)
	final_state: TravelState = result if isinstance(result, TravelState) else TravelState(**result)

	# Add to conversation history
	st.session_state["conversation_history"].append({
		"query": query,
		"city": final_state.city,
		"weather_count": len(final_state.weather_forecast or []),
		"image_count": len(final_state.image_urls or []),
		"date_range": final_state.date_range or ""
	})

	# Errors (if any)
	if final_state.errors:
		st.warning("\n".join(final_state.errors))

	# Show context preservation info
	if final_state.skip_summary:
		st.info(f"🔄 Context preserved: Using existing summary for {final_state.city}, only updating weather data")

	# convert and render output
	output = to_output_schema(final_state)

	st.subheader("Requested Dates")
	st.write(output.date_range or "Not provided")
	if output.date_range and len(final_state.weather_forecast or []) < 5:
		st.warning(
			"Weather provider returns about 5 days of forecast; your request may extend beyond available data. Showing available days."
		)

	st.subheader("City Summary")
	st.write(output.city_summary)

	# Weather chart (if detailed data exists)
	if final_state.weather_forecast:
		try:
			import pandas as pd
			import altair as alt
			df = pd.DataFrame(final_state.weather_forecast)
			if {"date", "temp_min", "temp_max"}.issubset(df.columns):
				# ensure proper ordering and numeric typing for plotting
				df["date"] = pd.to_datetime(df["date"], errors="coerce")
				df = df.dropna(subset=["date"]).sort_values("date")
				df["date_str"] = df["date"].dt.strftime("%Y-%m-%d")
				if len(df) >= 1:
					chart_data = df.melt(id_vars=["date_str"], value_vars=["temp_min", "temp_max"], var_name="series", value_name="temp")
					chart = (
						alt.Chart(chart_data)
						.mark_line(point=True)
						.encode(
							x=alt.X("date_str:N", title="Date"),
							y=alt.Y("temp:Q", title="°C"),
							color=alt.Color("series:N", title=""),
							tooltip=["date_str", "series", "temp"],
						)
						.properties(height=240)
					)
					st.subheader("Weather (°C)")
					st.altair_chart(chart, use_container_width=True)
				else:
					st.subheader("Weather Forecast")
					st.table(df)
			else:
				st.subheader("Weather Forecast")
				st.table(df)
		except Exception:
			st.subheader("Weather Forecast")
			st.write(output.weather_forecast)

	# Images
	if output.image_urls:
		st.subheader("Images")
		st.image(output.image_urls, width="stretch")

