# File: agent/agent_nodes.py
#
# This file implements the core logic for each step in the agent's workflow.
# This version is updated to build a conceptual graph with rich, combined metadata.

import os
import json
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from .agent_state import AgentState
from core.graph_searcher import RepoSearcher
from prompts.templates import DOCUMENTATION_PROMPT_TEMPLATE, CONCEPTUAL_GRAPH_PROMPT_TEMPLATE

# ... (initialize_documentation_queue, select_next_node, gather_documentation_context, generate_documentation functions remain the same as the previous corrected version) ...

def initialize_documentation_queue(state: AgentState) -> dict:
    print("--- Initializing Documentation Queue ---")
    repo_graph = state['repo_graph']
    all_nodes = set(repo_graph.nodes())
    leaf_nodes = [node for node in repo_graph.nodes() if repo_graph.out_degree(node) == 0]
    print(f"Found {len(leaf_nodes)} leaf nodes to start with.")
    return {
        "nodes_to_process": all_nodes,
        "documented_nodes": {},
        "nodes_to_document": leaf_nodes,
        "final_output_data": {},
        "is_finished": False,
    }

def select_next_node(state: AgentState) -> dict:
    print("\n--- Selecting Next Node to Document ---")
    nodes_to_document = state['nodes_to_document']
    if not nodes_to_document:
        remaining_nodes = state['nodes_to_process'] - set(state['documented_nodes'].keys())
        if not remaining_nodes:
            return {"is_finished": True}
        next_node_name = list(remaining_nodes)[0]
    else:
        next_node_name = nodes_to_document.pop(0)
    node_info = state['repo_graph'].nodes[next_node_name]
    print(f"Selected: '{next_node_name}' (Category: {node_info.get('category')})")
    return {
        "current_node_name": next_node_name,
        "current_node_info": node_info,
        "nodes_to_document": nodes_to_document,
    }

def gather_documentation_context(state: AgentState) -> dict:
    if state.get("is_finished"): return {}
    print(f"--- Gathering Context for '{state['current_node_name']}' ---")
    searcher = RepoSearcher(graph=state['repo_graph'])
    dependencies = searcher.get_dependencies(state['current_node_name'])
    context_str = ""
    if not dependencies:
        context_str = "This node has no internal dependencies."
    else:
        for dep_name in dependencies:
            if dep_name in state['documented_nodes']:
                context_str += f"\n- Dependency `{dep_name}`:\n{state['documented_nodes'][dep_name]}\n---"
    return {"context_for_llm": context_str}

def generate_documentation(state: AgentState) -> dict:
    if state.get("is_finished"): return {}
    print(f"--- Generating Documentation for '{state['current_node_name']}' ---")
    node_info = state['current_node_info']
    llm = AzureChatOpenAI(deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"), temperature=0.2, max_tokens=1024)
    prompt = PromptTemplate.from_template(DOCUMENTATION_PROMPT_TEMPLATE)
    chain = prompt | llm | StrOutputParser()
    print("Invoking LLM for documentation...")
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
    documented_nodes = state['documented_nodes']
    documented_nodes[state['current_node_name']] = generated_doc
    return {"documented_nodes": documented_nodes}


# --- MODIFIED: This function now builds the rich conceptual graph ---
def generate_conceptual_graph_data(state: AgentState) -> dict:
    """
    Builds the conceptual graph by merging AST metadata with LLM-generated
    semantic metadata for the current node.
    """
    if state.get("is_finished"): return {}
    current_node = state['current_node_name']
    print(f"--- Generating Conceptual Graph Data for '{current_node}' ---")

    llm = AzureChatOpenAI(
        deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        temperature=0.0, max_tokens=1024
    )
    prompt = PromptTemplate.from_template(CONCEPTUAL_GRAPH_PROMPT_TEMPLATE)
    chain = prompt | llm | StrOutputParser()

    print("Invoking LLM for conceptual analysis...")
    response_str = chain.invoke({
        "node_name": current_node,
        "documentation": state['documented_nodes'][current_node],
        "dependencies_context": state['context_for_llm'],
        "source_code": state['current_node_info'].get('info', '# Source code not available')
    })

    conceptual_graph = state['conceptual_graph']
    
    try:
        graph_data = json.loads(response_str)
        
        # 1. Get the base metadata from the original AST graph
        base_metadata = state['repo_graph'].nodes[current_node]
        
        # 2. Get the new semantic metadata from the LLM
        semantic_metadata = graph_data.get('semantic_metadata', {})
        
        # 3. Merge them to create the rich node for the conceptual graph
        # If the node doesn't exist, add it with all merged data.
        if not conceptual_graph.has_node(current_node):
            conceptual_graph.add_node(current_node, **base_metadata)
        
        # Update the node with the new semantic attributes
        nx.set_node_attributes(conceptual_graph, {current_node: semantic_metadata})

        # 4. Add the new semantic edges
        for edge in graph_data.get('semantic_edges', []):
            target_node = edge.get('target')
            if target_node and conceptual_graph.has_node(target_node):
                conceptual_graph.add_edge(current_node, target_node, label=edge.get('label', 'RELATED_TO'))

    except (json.JSONDecodeError, KeyError) as e:
        print(f"Warning: Failed to process conceptual data for node '{current_node}': {e}")

    return {"conceptual_graph": conceptual_graph}

def update_documentation_queue(state: AgentState) -> dict:
    if state.get("is_finished"): return {}
    current_node = state['current_node_name']
    print(f"--- Updating Queue after processing '{current_node}' ---")

    searcher = RepoSearcher(graph=state['repo_graph'])
    potential_new_nodes = searcher.get_references(current_node)

    nodes_to_document = state['nodes_to_document']
    for node in potential_new_nodes:
        if node in state['documented_nodes'] or node in nodes_to_document:
            continue 

        dependencies = searcher.get_dependencies(node)
        if all(dep in state['documented_nodes'] for dep in dependencies):
            print(f"New node ready for documentation: '{node}'")
            nodes_to_document.append(node)
            
    return {"nodes_to_document": nodes_to_document}

def should_continue(state: AgentState) -> str:
    if state.get("is_finished"):
        return "end"
    num_documented = len(state['documented_nodes'])
    num_total = len(state['nodes_to_process'])
    print(f"--- Progress Check: {num_documented} / {num_total} nodes documented. ---")
    if num_documented < num_total:
        return "continue"
    else:
        print("\n--- All nodes have been documented. Agent is finished. ---")
        return "end"
