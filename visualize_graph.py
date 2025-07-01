# visualize_graph.py

import pickle
import networkx as nx
from pyvis.network import Network
import os
import sys

def create_graph_visualization(graph_path="graph.pkl", output_filename="graph_visualization.html"):
    """
    Loads a networkx graph from a pickle file and creates an interactive
    HTML visualization using pyvis.

    Args:
        graph_path (str): The path to the input graph.pkl file.
        output_filename (str): The name of the output HTML file.
    """
    print(f"Attempting to load graph from '{graph_path}'...")
    try:
        with open(graph_path, 'rb') as f:
            G = pickle.load(f)
    except FileNotFoundError:
        print(f"ERROR: The file '{graph_path}' was not found.")
        print("Please make sure you have run the graph construction script first.")
        return
    except Exception as e:
        print(f"An error occurred while loading the graph: {e}")
        return

    print(f"Graph loaded successfully with {len(G.nodes())} nodes and {len(G.edges())} edges.")

    # Create a pyvis network object
    # Set a height and width for the browser window
    net = Network(height="900px", width="100%", bgcolor="#222222", font_color="white", notebook=False, directed=True)

    # Define a color map for different node categories
    color_map = {
        'class': '#007bff',    # Blue for classes
        'function': '#28a745', # Green for functions
        'unknown': '#6c757d'   # Gray for others
    }

    # Add nodes and edges from the networkx graph to the pyvis network
    for node, attrs in G.nodes(data=True):
        category = attrs.get('category', 'unknown')
        title_text = (
            f"<b>{node}</b> ({attrs.get('kind', 'N/A')})<br>"
            f"--------------------<br>"
            f"<b>File:</b> {attrs.get('fname')}<br>"
            f"<b>Category:</b> {category}<br>"
            f"<b>Docstring:</b> {attrs.get('docstring', 'Not captured')}"
        )
        
        net.add_node(
            node,
            label=node,
            title=title_text,
            color=color_map.get(category, color_map['unknown']),
            shape='dot'
        )

    # Add edges
    for source, target, edge_attrs in G.edges(data=True):
        net.add_edge(source, target)

    # Add interactive options
    net.show_buttons(filter_=['physics'])

    # Generate the visualization
    try:
        net.save_graph(output_filename)
        print(f"Successfully created interactive visualization: '{os.path.abspath(output_filename)}'")
        print("You can now open this HTML file in your web browser.")
    except Exception as e:
        print(f"An error occurred while saving the visualization: {e}")

if __name__ == '__main__':
    # create_graph_visualization(graph_path="output\CalculatorCode\conceptual_graph.pkl", output_filename="conceptual_graph_visualization.html")
    create_graph_visualization()