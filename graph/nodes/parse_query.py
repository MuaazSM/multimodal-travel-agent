from langchain_openai import ChatOpenAI
from graph.schemas.extraction import CityExtraction
from graph.state import TravelState
from config.prompts import PARSE_QUERY_PROMPT


def parse_query_node(state: TravelState) -> TravelState:
    
    llm = ChatOpenAI(
        model="gpt-4o",  
        temperature=0         
    )
    
    structured_llm = llm.with_structured_output(CityExtraction)
    
    # extraction prompt
    extraction = structured_llm.invoke(PARSE_QUERY_PROMPT.format(user_query=state.user_query))
    date_ref = extraction.date_reference or ""
    
    # update state
    if extraction.confidence >= 0.5:
        # Detect if city changed from previous query
        if state.previous_city and state.previous_city.lower() == extraction.city_name.lower():
            # Same city - skip summary and images, only update weather if date changed
            state.skip_summary = True
            state.skip_images = True
        else:
            # New city - fetch everything
            state.skip_summary = False
            state.skip_images = False
        
        state.previous_city = state.city  # Store current as previous
        state.city = extraction.city_name
        state.date_range = date_ref
    else:
        # no clear city found; fallback to previous city if available
        if state.city:
            state.skip_summary = True
            state.skip_images = True
        else:
            state.city = None
            state.errors.append("Could not identify a city in your query")
        state.date_range = date_ref
    
    return state