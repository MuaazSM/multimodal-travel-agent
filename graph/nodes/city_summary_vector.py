from tools.vector_store import get_vector_store
from graph.state import TravelState
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from config.prompts import VECTOR_SUMMARY_PROMPT

def city_summary_vector_node(state: TravelState):
    try:
        collection, model = get_vector_store()
        query_text = f"Overview and information about {state.city}"
        query_embedding = model.encode([query_text])[0]

        results = collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=5,
            where={"city": state.city.lower()}
        )

        if results.get("documents") and results["documents"] and results["documents"][0]:
            chunks = results["documents"][0]
            context = "\n---\n".join(chunks)

            prompt = PromptTemplate.from_template(VECTOR_SUMMARY_PROMPT)
            llm = ChatOpenAI(model="gpt-4o", temperature=0)
            chain = prompt | llm | StrOutputParser()

            summary = chain.invoke({"city": state.city, "context": context})
            state.city_summary = summary.strip()

            if not state.city_summary:
                state.city_summary = f"No summary generated for {state.city} from vector data."
                state.errors.append("Vector summary was empty")

        else:
            state.city_summary = f"Information about {state.city} is not available."
            state.errors.append(f"No vector DB results for {state.city}")
    
    except Exception as e:
        state.city_summary = f"Unable to retrieve information about {state.city}."
        state.errors.append(f"Vector DB error: {str(e)}")
        return state

    return state