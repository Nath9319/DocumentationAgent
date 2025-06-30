# File: agent/agent_nodes.py
#
# This file implements the core logic for each step in the agent's workflow.
# All functions have been refactored to return partial state updates for robustness.

import os
import json
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from .agent_state import AgentState
from core.graph_searcher import RepoSearcher
from prompts.templates import DOCUMENTATION_PROMPT_TEMPLATE, CONCEPTUAL_GRAPH_PROMPT_TEMPLATE

def initialize_documentation_queue(state: AgentState) -> dict:
    """
    Initializes the agent's state by identifying all "leaf" nodes and
    setting up the master tracking set.
    """
    print("--- Initializing Documentation Queue ---")
    repo_graph = state['repo_graph']
    all_nodes = set(repo_graph.nodes())
    
    leaf_nodes = [node for node in repo_graph.nodes() if repo_graph.out_degree(node) == 0]

    print(f"Found {len(leaf_nodes)} leaf nodes to start with across all components.")
    
    return {
        "nodes_to_process": all_nodes,
        "documented_nodes": {},
        "nodes_to_document": leaf_nodes,
        "final_output_data": {},
        "is_finished": False,
    }

def select_next_node(state: AgentState) -> dict:
    """
    Selects the next node to document from the queue, with a fallback
    for cyclic or disconnected graph components.
    """
    print("\n--- Selecting Next Node to Document ---")
    
    nodes_to_document = state['nodes_to_document']
    
    if not nodes_to_document:
        print("Primary queue is empty. Checking for remaining undocumented nodes...")
        remaining_nodes = state['nodes_to_process'] - set(state['documented_nodes'].keys())
        if not remaining_nodes:
            print("No remaining nodes to document.")
            return {"is_finished": True}
        
        next_node_name = list(remaining_nodes)[0]
        print(f"Force-selecting '{next_node_name}' to break a cycle or start a new component.")
    else:
        next_node_name = nodes_to_document.pop(0)

    node_info = state['repo_graph'].nodes[next_node_name]
    print(f"Selected: '{next_node_name}' (Category: {node_info.get('category')})")

    return {
        "current_node_name": next_node_name,
        "current_node_info": node_info,
        "nodes_to_document": nodes_to_document, # Return the modified list
    }

def gather_documentation_context(state: AgentState) -> dict:
    """
    Gathers all necessary context for the LLM to document the current node.
    """
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
                doc = state['documented_nodes'][dep_name]
                context_str += f"\n- Dependency `{dep_name}`:\n{doc}\n---"
    
    return {"context_for_llm": context_str}

def generate_documentation(state: AgentState) -> dict:
    """
    Invokes the LLM to generate documentation for the current node.
    """
    if state.get("is_finished"): return {}
    print(f"--- Generating Documentation for '{state['current_node_name']}' ---")
    
    node_info = state['current_node_info']
    llm = AzureChatOpenAI(
        deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        temperature=0.2, max_tokens=1024
    )
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

def generate_conceptual_graph_data(state: AgentState) -> dict:
    """
    Uses the generated documentation to ask the LLM to extract high-level
    conceptual nodes and edges.
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
    final_output_data = state['final_output_data']
    
    try:
        graph_data = json.loads(response_str)
        for node in graph_data.get('nodes', []):
            if 'id' in node and not conceptual_graph.has_node(node['id']):
                conceptual_graph.add_node(node['id'], **node)
        
        for edge in graph_data.get('edges', []):
            if 'source' in edge and 'target' in edge:
                conceptual_graph.add_edge(edge['source'], edge['target'], label=edge.get('label', 'RELATED_TO'))
        
        final_output_data[current_node] = {
            'documentation': state['documented_nodes'][current_node],
            'conceptual_data': graph_data
        }
    except json.JSONDecodeError:
        print(f"Warning: Failed to decode JSON for node '{current_node}'.")
        final_output_data[current_node] = {
            'documentation': state['documented_nodes'][current_node],
            'conceptual_data': None
        }

    return {
        "conceptual_graph": conceptual_graph,
        "final_output_data": final_output_data
    }

def update_documentation_queue(state: AgentState) -> dict:
    """
    Updates the documentation queue with new nodes that are now ready.
    """
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
    """
    Determines whether the agent should continue its work.
    """
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
