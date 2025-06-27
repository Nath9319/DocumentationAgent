# traverse_graph.py
#
# This script demonstrates how to load the repository graph created by
# 'construct_graph.py' and iterate through its nodes and edges. It provides
# examples for both simple iteration and structured graph traversal algorithms
# like Depth-First Search (DFS).
#
# This is the foundation for any advanced analysis you want to perform,
# such as invoking an LLM for each node in a logical sequence.

import pickle
import networkx as nx
import sys

# We import RepoSearcher from your file to use its helpful traversal methods.
from RepoGraph.graph_searcher import RepoSearcher
from find_node_connections import find_direct_connections
from get_node_info import get_info_for_node

def load_graph(graph_path="graph.pkl"):
        # --- Step 1: Load the Graph ---
    # First, we load the graph object that you created with construct_graph.py.
    # This object contains all the nodes and their connections.
    print(f"Loading graph from '{graph_path}'...")
    try:
        with open(graph_path, 'rb') as f:
            repo_graph = pickle.load(f)
    except FileNotFoundError:
        print(f"ERROR: The file '{graph_path}' was not found.")
        print("Please make sure you have run construct_graph.py to create it first.")
        return
    except Exception as e:
        print(f"An error occurred while loading the graph: {e}")
        return
    print(f"Graph loaded successfully with {len(repo_graph.nodes())} nodes.")
    return repo_graph

def traverse_repository_graph_simple(graph_path="graph.pkl"):
    """
    Loads and demonstrates various ways to traverse a repository graph.

    Args:
        graph_path (str): The path to the graph.pkl file.
    """

    repo_graph = load_graph(graph_path)

    # --- Example 1: Simple Iteration Over ALL Nodes ---
    # This is the most basic way to "iterate through each and every node".
    # It visits every node but does not follow any specific path or connection order.
    # This is useful if you want to perform an action on every single node
    # regardless of its connections.
    print("\n" + "="*60)
    print("Example 1: Simple Iteration Over All Nodes")
    print("="*60)
    for node_name in repo_graph.nodes():
        # For each node, you can access its attributes stored during creation.
        node_attributes = repo_graph.nodes[node_name]
        print(f"- Visiting node: '{node_name}' (Type: {node_attributes.get('category', 'N/A')})")
        incomming , outgoing = find_direct_connections(node_name)
        for i in incomming:
            print(f"Node Attributes for Node {i}",get_info_for_node(node_name= i))
        for o in outgoing:
            print(f"Node Attributes for Node {o}",get_info_for_node(node_name= o))
        print("\nTraversal complete.")
        # Here you could invoke an LLM for each node individually.
        # llm.analyze(node_name, node_attributes)
def traverse_repository_graph_dfs(graph_path="graph.pkl"):
    # --- Example 2: Traversal Following Connected Edges (DFS) ---
    # This method truly "walks" the graph by following the edges from a
    # starting point. We'll use a Depth-First Search (DFS) as an example.
    # DFS explores as far as possible along each branch before backtracking.
    # print("\n" + "="*60)
    # print("Example 2: Traversal from a Starting Node (Depth-First Search)")
    # print("="*60)
    repo_graph = load_graph(graph_path)
    # A traversal needs a starting point. Let's pick one from the graph.
    # If the graph is empty, we can't do this.
    if not repo_graph.nodes():
        print("Graph has no nodes. Cannot perform traversal.")
        return

    # Let's dynamically pick the first node in the graph as our start.
    # In a real scenario, you might choose a specific function like 'main'.
    start_node = list(repo_graph.nodes())[0]
    print(f"Starting traversal from node: '{start_node}'\n")

    # We use the RepoSearcher class you created, which has a handy `dfs` method.
    searcher = RepoSearcher(graph=repo_graph)
    
    # We'll limit the depth to 5 to keep the output readable.
    # The `dfs` function returns a list of nodes in the order they were visited.
    visited_nodes_in_order = searcher.dfs(query=start_node, depth=5)

    # Now, let's iterate through the path the traversal took.
    for i, node_name in enumerate(visited_nodes_in_order):
        print(f"Step {i}: Visiting '{node_name}'")
        
        # For each visited node, let's see its direct connections.
        # This shows how the traversal moves "through the connected edges".
        direct_connections = list(repo_graph.neighbors(node_name))
    
        
        if direct_connections:
            print(f"    -> From '{node_name}', you can reach: {', '.join(direct_connections)}")
        else:
            print(f"    -> '{node_name}' has no outgoing connections (it's a leaf node in this traversal).")

        # This is another place where you could invoke an LLM.
        # The key difference is that the LLM could now be given the context
        # of the traversal path, not just the single node.
        # llm.analyze_with_context(node_name, traversal_path=visited_nodes_in_order[:i+1])
    
    print("\nTraversal complete.")


if __name__ == '__main__':
    # You can optionally pass the path to your graph file as a command-line argument.
    graph_file_path = sys.argv[1] if len(sys.argv) > 1 else "graph.pkl"
    traverse_repository_graph_simple(graph_file_path)