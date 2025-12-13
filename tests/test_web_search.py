# test_web_search.py
"""Test script for web search functionality"""

from tools.web_search import WebSearchTool
from graph.state import TravelState
from graph.nodes.city_summary_web import city_summary_web_node
import os

def test_search_tool():
    """Test the web search tool"""
    print("="*60)
    print("Testing Web Search Tool")
    print("="*60)
    
    tool = WebSearchTool()
    results = tool.search("Snohomish Washington information", max_results=3)
    
    print(f"\nFound {len(results)} results:\n")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['title']}")
        print(f"   Snippet: {result['snippet'][:150]}...")
        print(f"   URL: {result['url']}\n")

def test_web_summary_node():
    """Test the web summary node"""
    print("="*60)
    print("Testing Web Summary Node")
    print("="*60)
    
    # Create test state
    state = TravelState(
        user_query="Tell me about Snohomish",
        city="Snohomish"
    )
    
    # Run node
    result = city_summary_web_node(state)
    
    # Display results
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    print(f"\nCity: {result.city}")
    print(f"\nSummary:\n{result.city_summary}")
    
    if result.errors:
        print(f"\nErrors: {result.errors}")

if __name__ == "__main__":
    # Make sure API key is set
    if not os.getenv("TAVILY_API_KEY"):
        print("Error: TAVILY_API_KEY not found in environment")
        print("Set it with: export TAVILY_API_KEY='your_key_here'")
        exit(1)
    
    # Run tests
    test_search_tool()
    print("\n\n")
    test_web_summary_node()