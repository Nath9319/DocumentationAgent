# get_node_info.py
#
# This script provides a function to retrieve all stored information for a
# single node from the repository graph. It packages the node's attributes
# and its direct connections into a clean, easy-to-use dictionary.

import pickle
import networkx as nx
import sys
import json

def get_info_for_node(node_name: str, graph_path: str = "graph.pkl") -> dict:
    """
    Loads the repository graph and returns a dictionary containing all
    available information for a specified node.

    Args:
        node_name (str): The name of the node (e.g., a function or class name)
                         to retrieve information for.
        graph_path (str): The path to the saved graph.pkl file.

    Returns:
        dict: A dictionary containing the node's attributes and connections,
              or None if the node is not found.
    """
    try:
        # Step 1: Load the graph from the .pkl file
        with open(graph_path, 'rb') as f:
            repo_graph = pickle.load(f)
    except FileNotFoundError:
        print(f"Error: The graph file '{graph_path}' was not found.")
        return None

    # Step 2: Check if the node exists in the graph
    if node_name not in repo_graph:
        return None

    # Step 3: Retrieve the node's stored attributes.
    # The attributes are already stored as a dictionary in networkx.
    # We make a copy to avoid modifying the original graph data.
    node_attributes = repo_graph.nodes[node_name].copy()

    # Step 4: Find the node's direct connections
    # Successors are nodes that `node_name` has an edge pointing TO.
    outgoing_connections = list(repo_graph.successors(node_name))
    
    # Predecessors are nodes that have an edge pointing TO `node_name`.
    incoming_connections = list(repo_graph.predecessors(node_name))

    # Step 5: Add the connection information to our dictionary
    node_attributes['outgoing_connections'] = outgoing_connections
    node_attributes['incoming_connections'] = incoming_connections
    
    return node_attributes


# if __name__ == '__main__':
#     # This block allows you to run the script directly from the command line
#     # to test the function.
#     if len(sys.argv) < 2:
#         print("Usage: python get_node_info.py <NodeName>")
#         print("Example: python get_node_info.py MyClassName")
#         sys.exit(1)

#     target_node = sys.argv[1]

#     # Call our main function to get the dictionary
#     node_info_dict = get_info_for_node(target_node)

#     # Print the results
#     if node_info_dict:
#         print(f"--- Information for Node: '{target_node}' ---")
#         # Use json.dumps for a nicely formatted, indented print of the dictionary
#         print(json.dumps(node_info_dict, indent=2))
#     else:
#         print(f"Could not retrieve information for node '{target_node}'.")
#         print("Please make sure the node exists in your 'graph.pkl' file.")