# This script loads the repository graph and, for any given node name,
# finds all other nodes that are directly connected to it. It distinguishes
# between outgoing connections (e.g., functions that the given node calls)
# and incoming connections (e.g., functions that call the given node).
#
# The results are printed in a clean, indented format.

import pickle
import networkx as nx
import sys

def find_direct_connections(node_name: str, graph_path: str = "graph.pkl"):
    """
    Finds and prints all direct incoming and outgoing connections for a specific node.

    Args:
        node_name (str): The name of the node to find connections for.
        graph_path (str): The path to the saved graph.pkl file.
    """
    # --- Step 1: Load the graph from the file ---
    try:
        with open(graph_path, 'rb') as f:
            repo_graph = pickle.load(f)
    except FileNotFoundError:
        print(f"Error: The graph file '{graph_path}' was not found.")
        print("Please ensure you have run 'construct_graph.py' first.")
        return

    # --- Step 2: Check if the requested node exists in the graph ---
    if node_name not in repo_graph:
        print(f"Error: Node '{node_name}' not found in the graph.")
        # Suggest similar nodes if any exist
        suggestions = [n for n in repo_graph.nodes() if node_name.lower() in n.lower()]
        if suggestions:
            print("\nDid you mean one of these?")
            for s in suggestions[:10]: # Limit suggestions
                print(f"  - {s}")
        return

    print(f"Connections for node: '{node_name}'")
    print("-" * (25 + len(node_name)))

    # --- Step 3: Find and print outgoing connections ---
    # In a directed graph, 'successors' are the nodes that the current node
    # has an edge pointing TO. This represents functions/classes it calls or invokes.
    outgoing_nodes = list(repo_graph.successors(node_name))

    print("\n  Outgoing Connections (i.e., what '{0}' calls):".format(node_name))
    if outgoing_nodes:
        for i, successor in enumerate(outgoing_nodes):
            print(f"    {i+1}. {successor}")
    else:
        print("    (None)")

    # --- Step 4: Find and print incoming connections ---
    # 'Predecessors' are the nodes that have an edge pointing FROM them
    # TO the current node. This represents functions/classes that call it.
    incoming_nodes = list(repo_graph.predecessors(node_name))

    print("\n  Incoming Connections (i.e., what calls '{0}'):".format(node_name))
    if incoming_nodes:
        for i, predecessor in enumerate(incoming_nodes):
            print(f"    {i+1}. {predecessor}")
    else:
        print("    (None)")

    return incoming_nodes, outgoing_nodes


# if __name__ == '__main__':
#     # We use command-line arguments to get the node name from the user.
#     if len(sys.argv) < 2:
#         print("Usage: python find_node_connections.py <NodeName>")
#         print("Example: python find_node_connections.py MyClassName")
#         sys.exit(1)
    
#     # The node name is the first argument after the script name.
#     target_node = sys.argv[1]
    
#     find_direct_connections(target_node)