# File: agent/agent_nodes.py
#
# This file implements the core logic for each step in the agent's workflow.
# This version includes more robust logic to ensure all nodes, including those
# in disconnected components, are documented.

import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from .agent_state import AgentState
from RepoGraph.graph_searcher import RepoSearcher
from prompts.templates import DOCUMENTATION_PROMPT_TEMPLATE

def initialize_documentation_queue(state: AgentState) -> AgentState:
    """
    Initializes the agent's state by identifying all "leaf" nodes across
    all disconnected components of the graph. It also adds all nodes to a
    master "to do" set for tracking overall progress.
    """
    print("--- Initializing Documentation Queue ---")
    repo_graph = state['repo_graph']
    
    # --- MODIFIED: Track all nodes to ensure complete coverage ---
    all_nodes = set(repo_graph.nodes())
    state['nodes_to_process'] = all_nodes
    state['documented_nodes'] = {}
    # ---

    leaf_nodes = []
    for node in repo_graph.nodes():
        if repo_graph.out_degree(node) == 0:
            leaf_nodes.append(node)

    print(f"Found {len(leaf_nodes)} leaf nodes to start with across all components.")
    state['nodes_to_document'] = leaf_nodes
    
    return state

def select_next_node(state: AgentState) -> AgentState:
    """
    Selects the next node to document from the queue. If the primary queue
    is empty but there are still undocumented nodes (e.g., in a cycle),
    it will pick one to break the cycle.
    """
    print("\n--- Selecting Next Node to Document ---")
    
    # --- MODIFIED: Fallback for disconnected or cyclical components ---
    if not state['nodes_to_document']:
        print("Primary queue is empty. Checking for remaining undocumented nodes...")
        remaining_nodes = state['nodes_to_process'] - set(state['documented_nodes'].keys())
        if not remaining_nodes:
            # This case should be caught by should_continue, but as a safeguard:
            print("No remaining nodes to document.")
            return state
        
        # Pick an arbitrary node from the remaining ones to process.
        # This can happen if a component is a cycle with no leaf nodes.
        next_node_name = list(remaining_nodes)[0]
        print(f"Force-selecting '{next_node_name}' to break a cycle or start a new component.")
        state['current_node_name'] = next_node_name
    else:
        # Standard operation: Pop the first node from the list.
        next_node_name = state['nodes_to_document'].pop(0)
        state['current_node_name'] = next_node_name
    # ---
    
    # Get all stored information for this node from the graph.
    node_info = state['repo_graph'].nodes[next_node_name]
    state['current_node_info'] = node_info

    print(f"Selected: '{next_node_name}' (Category: {node_info.get('category')})")
    return state

def gather_documentation_context(state: AgentState) -> AgentState:
    """
    Gathers all necessary context for the LLM to document the current node.
    This includes the documentation of all its direct dependencies.
    """
    print(f"--- Gathering Context for '{state['current_node_name']}' ---")
    
    repo_graph = state['repo_graph']
    searcher = RepoSearcher(graph=repo_graph)
    
    dependencies = searcher.get_dependencies(state['current_node_name'])
    
    context_str = ""
    if not dependencies:
        context_str = "This node has no internal dependencies."
    else:
        print(f"Found dependencies: {dependencies}")
        for dep_name in dependencies:
            if dep_name in state['documented_nodes']:
                doc = state['documented_nodes'][dep_name]
                context_str += f"\n- Dependency `{dep_name}`:\n{doc}\n---"
            else:
                context_str += f"\n- Dependency `{dep_name}`: (Not yet documented)"
    
    state['context_for_llm'] = context_str
    return state

def generate_documentation(state: AgentState) -> AgentState:
    """
    Invokes the LLM with the gathered context and source code to generate
    the documentation for the current node.
    """
    print(f"--- Generating Documentation for '{state['current_node_name']}' ---")
    
    node_info = state['current_node_info']
    llm = ChatOpenAI(model="gpt-4o", temperature=0.2, max_tokens=1024)
    prompt = PromptTemplate.from_template(DOCUMENTATION_PROMPT_TEMPLATE)
    chain = prompt | llm | StrOutputParser()
    
    print("Invoking language model...")
    generated_doc = chain.invoke({
        "node_name": state['current_node_name'],
        "node_category": node_info.get('category', 'N/A'),
        "node_fname": node_info.get('fname', 'N/A'),
        "node_line_start": node_info.get('line', [0, 0])[0],
        "node_line_end": node_info.get('line', [0, 0])[1],
        "node_docstring": node_info.get('docstring', 'Not available.'),
        "dependencies_context": state['context_for_llm'],
        "source_code": node_info.get('info', '# Source code not available')
    })
    
    state['documented_nodes'][state['current_node_name']] = generated_doc
    print("Documentation generated successfully.")
    return state

def save_documentation_and_update_queue(state: AgentState) -> AgentState:
    """
    Saves the newly generated documentation to a file and updates the
    documentation queue with new nodes that are now ready to be processed.
    """
    current_node = state['current_node_name']
    print(f"--- Saving Documentation and Updating Queue for '{current_node}' ---")

    sanitized_name = "".join(c for c in current_node if c.isalnum() or c in ('_', '-')).rstrip()
    output_path = os.path.join(state['output_dir'], f"{sanitized_name}.md")
    
    with open(output_path, "w", encoding='utf-8') as f:
        f.write(f"# Documentation for `{current_node}`\n\n")
        f.write(state['documented_nodes'][current_node])
    print(f"Saved documentation to: {output_path}")

    repo_graph = state['repo_graph']
    searcher = RepoSearcher(graph=repo_graph)
    potential_new_nodes = searcher.get_references(current_node) # Nodes that call the current one

    for node in potential_new_nodes:
        if node in state['documented_nodes'] or node in state['nodes_to_document']:
            continue 

        dependencies = searcher.get_dependencies(node)
        all_deps_documented = all(dep in state['documented_nodes'] for dep in dependencies)

        if all_deps_documented:
            print(f"New node ready for documentation: '{node}'")
            state['nodes_to_document'].append(node)
            
    return state

def should_continue(state: AgentState) -> str:
    """
    Determines whether the agent should continue its work by checking if
    the number of documented nodes is less than the total number of nodes.
    """
    # --- MODIFIED: More robust completion check ---
    num_documented = len(state['documented_nodes'])
    num_total = len(state['nodes_to_process'])
    
    print(f"--- Progress Check: {num_documented} / {num_total} nodes documented. ---")

    if num_documented < num_total:
        return "continue"
    else:
        print("\n--- All nodes have been documented. Agent is finished. ---")
        return "end"

