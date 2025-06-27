# This is the main entry point for the AI Documentation Agent.
# It handles command-line arguments, sets up the environment,
# constructs the code graph, and invokes the LangGraph agent.

import os
import sys
import pickle
from dotenv import load_dotenv

from RepoGraph.construct_graph import CodeGraph
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
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not found in .env file.")
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
        py_files = code_graph_builder.find_files(repo_path)
        _, repo_graph = code_graph_builder.get_code_graph(py_files)
        
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
    
    print("\n--- Invoking Agent ---")
    # The .stream() method runs the agent and yields the state after each step.
    for step in agent_app.stream(initial_state):
        # This loop will print the state of the graph as it executes.
        # It's useful for debugging and seeing the agent's progress.
        # The key is the name of the node that just executed.
        node_name = list(step.keys())[0]
        print(f"\nCompleted step: {node_name}")
        # print(f"Current State: {list(step.values())[0]}")
        print("--------------------")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <path_to_repository>")
        sys.exit(1)
        
    repository_path = sys.argv[1]
    run_documentation_agent(repository_path)