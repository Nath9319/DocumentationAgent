# File: main.py
#
# This is the main entry point for the AI Documentation Agent.
# This version is corrected to properly initialize the agent's state and
# robustly save all final outputs, including individual markdown files.

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

    # --- Step 2: Construct or Load the AST Code Graph ---
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
    
    # --- THIS IS THE FIX: Initialize the state with all required keys ---
    initial_state = {
        "repo_graph": repo_graph,
        "conceptual_graph": nx.MultiDiGraph(),
        "final_output_data": {}
    }
    
    total_nodes = len(repo_graph.nodes())
    recursion_limit = total_nodes * 6
    config = {"recursion_limit": recursion_limit}
    
    print(f"\n--- Invoking Agent (Total nodes: {total_nodes}, Recursion limit set to: {recursion_limit}) ---")
    
    # Use .invoke() to run the agent to completion and get the final state.
    final_state = agent_app.invoke(initial_state, config=config)

    # --- Step 5: Save the Final Outputs ---
    if final_state:
        print("\n--- Agent finished. Saving final outputs. ---")
        
        # 1. Save the LLM-generated conceptual graph
        conceptual_graph = final_state.get('conceptual_graph')
        if conceptual_graph:
            conceptual_graph_path = os.path.join(output_dir, "conceptual_graph.pkl")
            with open(conceptual_graph_path, 'wb') as f:
                pickle.dump(conceptual_graph, f)
            print(f"Conceptual graph saved to: {conceptual_graph_path}")
        
        # 2. Save the consolidated documentation and graph data as JSON
        final_output_data = final_state.get('final_output_data', {})
        json_output_path = os.path.join(output_dir, "documentation_and_graph_data.json")
        with open(json_output_path, 'w', encoding='utf-8') as f:
            json.dump(final_output_data, f, indent=2)
        print(f"Consolidated JSON data saved to: {json_output_path}")

        # 3. Save individual markdown files for each documented node
        print("\n--- Saving individual documentation files... ---")
        docs_output_dir = os.path.join(output_dir, "documentation")
        os.makedirs(docs_output_dir, exist_ok=True)

        for node_name, data in final_output_data.items():
            if 'documentation' in data and data['documentation']:
                # Sanitize the node name for use as a filename
                sanitized_name = "".join(c for c in node_name if c.isalnum() or c in ('_', '-')).rstrip()
                doc_path = os.path.join(docs_output_dir, f"{sanitized_name}.md")
                with open(doc_path, "w", encoding='utf-8') as f:
                    f.write(f"# Documentation for `{node_name}`\n\n")
                    f.write(data['documentation'])
        print(f"Saved {len(final_output_data)} documentation files to: '{docs_output_dir}'")

    else:
        print("\n--- Agent finished, but no final state was captured. Outputs not saved. ---")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <path_to_repository>")
        sys.exit(1)
        
    repository_path = sys.argv[1]
    run_documentation_agent(repository_path)
