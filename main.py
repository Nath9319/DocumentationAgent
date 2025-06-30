# File: main.py
#
# This is the main entry point for the AI Documentation Agent.
# This version is corrected to use .invoke() instead of .stream() to
# robustly capture the final state and prevent KeyErrors when saving outputs.

import os
import sys
import pickle
import json
import networkx as nx
from dotenv import load_dotenv

from core.construct_graph import CodeGraph
from agent.agent_graph import create_agent_graph

def run_documentation_agent(repo_path: str):
    """
    Sets up and runs the entire documentation and conceptual graph generation process.
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
    print(f"Outputs will be saved in: '{output_dir}'")
    
    # --- Step 4: Create and Run the LangGraph Agent ---
    agent_app = create_agent_graph()
    
    initial_state = {
        "repo_graph": repo_graph,
        "output_dir": output_dir,
        "conceptual_graph": nx.MultiDiGraph(),
        "final_output_data": {}
    }
    
    total_nodes = len(repo_graph.nodes())
    recursion_limit = total_nodes * 6
    config = {"recursion_limit": recursion_limit}
    
    print(f"\n--- Invoking Agent (Total nodes: {total_nodes}, Recursion limit set to: {recursion_limit}) ---")
    
    # --- THIS IS THE FIX ---
    # Use .invoke() to run the agent to completion and get the final state directly.
    # This is more robust than iterating with .stream() for this use case.
    final_state = agent_app.invoke(initial_state, config=config)
    # --- END OF FIX ---

    # --- Step 5: Save the Final Outputs ---
    if final_state:
        print("\n--- Agent finished. Saving final outputs. ---")
        
        # 1. Save the LLM-generated conceptual graph
        conceptual_graph_path = os.path.join(output_dir, "conceptual_graph.pkl")
        with open(conceptual_graph_path, 'wb') as f:
            pickle.dump(final_state['conceptual_graph'], f)
        print(f"Conceptual graph saved to: {conceptual_graph_path}")
        
        # 2. Save the consolidated documentation and graph data as JSON
        json_output_path = os.path.join(output_dir, "documentation_and_graph_data.json")
        with open(json_output_path, 'w', encoding='utf-8') as f:
            json.dump(final_state['final_output_data'], f, indent=2)
        print(f"Consolidated JSON data saved to: {json_output_path}")
    else:
        print("\n--- Agent finished, but no final state was captured. Outputs not saved. ---")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <path_to_repository>")
        sys.exit(1)
        
    repository_path = sys.argv[1]
    run_documentation_agent(repository_path)
