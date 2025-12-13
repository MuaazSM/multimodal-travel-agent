from langchain_openai import ChatOpenAI
from graph.schemas.extraction import CityExtraction
from graph.state import TravelState
from dotenv import load_dotenv

def parse_query_node(state: TravelState) -> TravelState:
    
    llm = ChatOpenAI(
        model="gpt-4o",  
        temperature=0         
    )
    
    structured_llm = llm.with_structured_output(CityExtraction)
    
    # extraction prompt
    extraction = structured_llm.invoke(
        f"""Extract the city name from this travel query.
        
        User query: "{state.user_query}"

        Instructions:
        - Normalize city names (NYC to New York, Paras to Paris)
        - Handle misspellings and variations
        - Extract date/time references if present
        - If no city is clearly mentioned, set confidence < 0.5

        Examples:
        "Tell me about Paras" -> city_name: "Paris", confidence: 0.9
        "What's the weather like in NYC next week?" ->  city_name: "New York", date_reference: "next week"
        "Japan's capital" -> city_name: "Tokyo", confidence: 0.95
        """
    )
    
    # update state
    if extraction.confidence >= 0.5:
        state.city = extraction.city_name
        state.date_range = extraction.date_reference
    else:
        # no clear city found
        state.city = None
        state.errors.append("Could not identify a city in your query")
    
    return state