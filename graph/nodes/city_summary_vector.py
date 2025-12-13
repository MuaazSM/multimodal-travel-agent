import chromadb
from sentence_transformers import SentenceTransformer
from graph.state import TravelState
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
_client = None
_model = None
_collection = None

def get_vector_store():
    global _client, _model, _collection

    if _collection is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
        _client = chromadb.PersistentClient(path="storage/chroma")
        _collection = _client.get_collection(name="cities")

    return _collection, _model


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

            prompt = PromptTemplate.from_template(
                """Using ONLY the information provided below, write a comprehensive summary about {city}.

                Information from knowledge base:
                {context}

                Write a well-structured summary (3-4 paragraphs) covering the most important aspects of this city.
                Do not add any information not present in the provided context."""
            )              
            llm = ChatOpenAI(model="gpt-4o", temperature=0)
            chain = prompt | llm | StrOutputParser()

            summary = chain.invoke({"city": state.city, "context": context})
            state.city_summary = summary

        else:
            state.city_summary = f"Information about {state.city} is not available."
            state.errors.append(f"No vector DB results for {state.city}")
    
    except Exception as e:
        state.city_summary = f"Unable to retrieve information about {state.city}."
        state.errors.append(f"Vector DB error: {str(e)}")
        return state