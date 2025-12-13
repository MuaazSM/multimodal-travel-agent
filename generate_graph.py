"""Generate graph.png visualization"""

from graph.build_graph import build_app

def generate_graph_png():
    # Build the graph
    app = build_app(enable_checkpointer=False)  #disable checkpointer for visualization
    

    # mermaid PNG generation
    png_data = app.get_graph().draw_mermaid_png()
        
    with open("graph.png", "wb") as f:
        f.write(png_data)
        
    print("graph.png generated successfully")
    print("\nGraph Structure:")
    print("- Entry: parse (extract city from query)")
    print("- Router: vector/web decision")
    print("- Parallel: vector_summary OR web_summary")
    print("- Tools: Manual execution (weather + images in parallel)")
    print("- Final: Assembly with fallbacks")
    print("- Memory: Checkpointer enabled for context preservation")


if __name__ == "__main__":
    generate_graph_png()
