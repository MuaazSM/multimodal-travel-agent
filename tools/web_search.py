from tavily import TavilyClient
import os
from dotenv import load_dotenv
class WebSearchTool:
    def __init__(self):
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            raise ValueError("Tavily api key not found in env")
        
        self.client = TavilyClient(api_key=api_key)

    def search(self, query, max_results=5):
        try:
            response = self.client.search(
                query=query,
                max_results=max_results,
                search_depth="basic",
                include_answer=False,
                include_raw_content=False
            )

            return self._normalize_results(response)
        except Exception as e:
            print(f"Search Error: {e}")
            return []

    def _normalize_results(self, raw_response):
        normalized = []
        for result in raw_response.get("results", []):
            normalized.append({
                "title": result.get("title", "No Title"),
                "snippet": result.get("content", "no content available"),
                "url": result.get("url", "")
            })

        return normalized

