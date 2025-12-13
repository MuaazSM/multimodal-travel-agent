from graph.state import TravelState
from tools.web_search import WebSearchTool
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from config.prompts import WEB_SUMMARY_PROMPT
def city_summary_web_node(state):
    try:
        search_tool = WebSearchTool()

        search_query = f"{state.city} city information overview guide"

        print(f"Searching for: {search_query}")

        results = search_tool.search(search_query, max_results=5)

        if not results:
            state.city_summary = f"Unable tp find info about {state.city} online"
            state.errors.append(f"Web search returned no results for {state.city}")
            return state

        print(f"Found {len(results)} search results")

        context_parts = []

        for i,result in enumerate(results, 1):
            context_parts.append(
                f"[Source {i}: {result['title']}]\n{result['snippet']}"
            )

        context = "\n\n---\n\n".join(context_parts)
        prompt = PromptTemplate.from_template(WEB_SUMMARY_PROMPT)
        llm = ChatOpenAI(model="gpt-4o", temperature=0)
        chain = prompt | llm | StrOutputParser()

        print(f"Generating summary for {state.city}...")
        summary = chain.invoke({"city": state.city, "context": context})

        state.city_summary = (summary or "").strip()
        if not state.city_summary:
            state.city_summary = f"No summary generated for {state.city} from web search."
            state.errors.append("Web summary was empty")
        else:
            print(f"Summary generated successfully ({len(summary)} characters)")

    except Exception as e:
        print(f"Error in web summary node: {e}")
        state.city_summary = f"Unable to retrieve information about {state.city} at this time."
        state.errors.append(f"Web summary error: {str(e)}")

    return state