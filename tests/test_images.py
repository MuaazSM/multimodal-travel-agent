"""Test script for images tool and node"""

from tools.image_api import ImageTool
from graph.state import TravelState
from graph.nodes.images import images_node


def test_image_tool_init():
    print("=" * 60)
    print("Testing Image Tool initialization")
    print("=" * 60)
    try:
        tool = ImageTool()
        print(f"Provider selected: {tool.provider}")
        urls = tool.search_images("Paris", limit=6)
        print(f"Fetched {len(urls)} image URLs")
        if urls:
            for i, u in enumerate(urls[:3], 1):
                print(f"  {i}. {u}")
    except Exception as e:
        print(f"ImageTool init/search error: {e}")


def test_images_node():
    print("\n" + "=" * 60)
    print("Testing Images Node")
    print("=" * 60)
    state = TravelState(user_query="Show me images", city="Paris")
    result = images_node(state)
    print(f"City: {result.city}")
    print(f"Image URLs: {len(result.image_urls)}")
    if result.image_urls:
        for i, u in enumerate(result.image_urls[:3], 1):
            print(f"  {i}. {u}")
    if result.errors:
        print("Errors:")
        for err in result.errors:
            print(f"  - {err}")


if __name__ == "__main__":
    test_image_tool_init()
    print("\n")
    test_images_node()
