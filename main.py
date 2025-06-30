# File: main.py
#
# This is the main entry point for the AI Documentation Agent.
# This version includes a higher recursion limit to handle large repositories
# without encountering a GraphRecursionError.

import os
import sys
import pickle
from dotenv import load_dotenv

from core.construct_graph import CodeGraph
from agent.agent_graph import create_agent_graph

def run_documentation_agent(repo_path: str):
    """
    Sets up and runs the entire documentation generation process.

    Args:
        repo_path (str): The local file path to the repository to be documented.
    """
    print("--- AI Documentation Agent Initializing ---")
    
    # --- Step 1: Environment Setup ---
    load_dotenv()
    if not os.getenv("AZURE_OPENAI_API_KEY") or not os.getenv("AZURE_OPENAI_ENDPOINT"):
        print("Error: AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT must be set in the .env file.")
        sys.exit(1)

    if not os.path.isdir(repo_path):
        print(f"Error: Repository path '{repo_path}' not found.")
        sys.exit(1)

    # --- Step 2: Construct or Load the Code Graph ---
    graph_file = "graph.pkl"
    if os.path.exists(graph_file):
        print(f"Found existing graph file: '{graph_file}'. Loading it.")
        with open(graph_file, 'rb') as f:
            repo_graph = pickle.load(f)
    else:
        print(f"No graph file found. Constructing new graph for '{repo_path}'...")
        code_graph_builder = CodeGraph(root=repo_path)
        repo_graph = code_graph_builder.build_graph()
        
        with open(graph_file, 'wb') as f:
            pickle.dump(repo_graph, f)
        print(f"Successfully constructed and saved graph to '{graph_file}'.")

    if not repo_graph.nodes():
        print("Error: The constructed graph has no nodes. Cannot proceed.")
        sys.exit(1)

    # --- Step 3: Set up Output Directory ---
    repo_name = os.path.basename(os.path.normpath(repo_path))
    output_dir = os.path.join("output", repo_name)
    os.makedirs(output_dir, exist_ok=True)
    print(f"Documentation will be saved in: '{output_dir}'")
    
    # --- Step 4: Create and Run the LangGraph Agent ---
    agent_app = create_agent_graph()
    
    initial_state = {
        "repo_graph": repo_graph,
        "output_dir": output_dir
    }
    
    # --- MODIFIED SEGMENT: Set a higher recursion limit ---
    # The default is 25, which is too low for documenting a whole repo.
    # We get the total number of nodes to set a sensible limit.
    total_nodes = len(repo_graph.nodes())
    # We set the limit to be higher than the number of nodes, as each node
    # takes several steps in the graph. A buffer of 5 steps per node is safe.
    recursion_limit = total_nodes * 5
    
    config = {"recursion_limit": recursion_limit}
    # --- END MODIFIED SEGMENT ---

    print(f"\n--- Invoking Agent (Total nodes: {total_nodes}, Recursion limit set to: {recursion_limit}) ---")
    
    # Pass the config dictionary to the .stream() method.
    for step in agent_app.stream(initial_state, config=config):
        # This loop will print the state of the graph as it executes,
        # which is useful for debugging and seeing the agent's progress.
        node_name = list(step.keys())[0]
        print(f"Completed step: {node_name}")
        print("--------------------")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <path_to_repository>")
        sys.exit(1)
        
    repository_path = sys.argv[1]
    run_documentation_agent(repository_path)
