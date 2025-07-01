# File: agent/agent_nodes.py
#
# This file implements the core logic for each step in the agent's workflow.
# This version has been refactored to import prompts from the prompts.templates
# module for better organization and maintainability.

import os
import json
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
import networkx as nx
from .agent_state import AgentState
from core.graph_searcher import RepoSearcher

# --- Import all necessary prompts from the centralized templates file ---
from prompts.templates import (
    CODE_ANALYSIS_PROMPT_TEMPLATE,
    DOCUMENTATION_PROMPT_TEMPLATE,
    CONCEPTUAL_GRAPH_PROMPT_TEMPLATE
)


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
        "is_finished": False,
    }

def select_next_node(state: AgentState) -> dict:
    """
    Selects the next node to document from the queue.
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
        "nodes_to_document": nodes_to_document,
    }

def gather_documentation_context(state: AgentState) -> dict:
    """
    Analyzes the current node's code to find all dependencies, then gathers
    context for them from the graph or the documentation cache.
    """
    if state.get("is_finished"):
        return {}
    
    current_node_name = state['current_node_name']
    current_node_info = state['current_node_info']
    repo_graph = state['repo_graph']
    documented_nodes = state['documented_nodes']
    
    print(f"--- intelligently Gathering Context for '{current_node_name}' ---")

    # Step A: Use an LLM to find out what functions/classes are being called.
    print("Step A: Analyzing code to identify dependencies...")
    llm = AzureChatOpenAI(deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"), temperature=0.0, max_tokens=1024)
    prompt = PromptTemplate.from_template(CODE_ANALYSIS_PROMPT_TEMPLATE)
    chain = prompt | llm | JsonOutputParser()
    
    try:
        dependencies = chain.invoke({
            "source_code": current_node_info.get('info', '')
        })
        print(f"Identified dependencies: {dependencies}")
    except Exception as e:
        print(f"Warning: Failed to analyze code for dependencies: {e}")
        dependencies = []

    # Step B & C: Check for existing documentation and fetch missing info.
    print("Step B & C: Verifying context and fetching missing information...")
    context_str = ""
    if not dependencies:
        context_str = "This node has no identified internal dependencies."
    else:
        for dep_name in dependencies:
            context_block = ""
            # Check if the dependency has already been documented.
            if dep_name in documented_nodes:
                print(f"   - Found existing documentation for '{dep_name}'.")
                context_block = f"### Dependency: `{dep_name}` (Already Documented)\n\n{documented_nodes[dep_name]}\n\n---\n\n"
            # If not, check if it exists in our main code graph.
            elif repo_graph.has_node(dep_name):
                print(f"   - Fetching info for '{dep_name}' from the code graph.")
                dep_info = repo_graph.nodes[dep_name]
                dep_code = dep_info.get('info', '# Source code not available')
                dep_docstring = dep_info.get('docstring', 'No docstring available.')
                context_block = (
                    f"### Dependency: `{dep_name}` (From Source)\n\n"
                    f"**Docstring:**\n```\n{dep_docstring}\n```\n\n"
                    f"**Source Code:**\n```python\n{dep_code}\n```\n\n---\n\n"
                )
            # If it's not in the graph, it's likely an external library.
            else:
                print(f"   - Dependency '{dep_name}' is likely an external library or built-in.")
                context_block = f"### Dependency: `{dep_name}` (External or Built-in)\n\nThis is likely a call to an external library (e.g., os, pandas) or a Python built-in function.\n\n---\n\n"
            
            context_str += context_block

    # Step D: Send the complete context to the next nodes.
    print("Step D: Assembled comprehensive context for the next step.")
    return {"context_for_llm": context_str}


def generate_documentation(state: AgentState) -> dict:
    """
    Invokes the LLM to generate documentation for the current node.
    """
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

def generate_conceptual_graph_data(state: AgentState) -> dict:
    """
    Builds the conceptual graph by merging AST metadata with LLM-generated
    semantic metadata for the current node.
    """
    if state.get("is_finished"): return {}
    current_node = state['current_node_name']
    print(f"--- Generating Conceptual Graph Data for '{current_node}' ---")

    llm = AzureChatOpenAI(deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"), temperature=0.0, max_tokens=1024)
    prompt = PromptTemplate.from_template(CONCEPTUAL_GRAPH_PROMPT_TEMPLATE)
    chain = prompt | llm | JsonOutputParser()

    print("Invoking LLM for conceptual analysis...")
    
    final_output_data = state['final_output_data']
    
    try:
        response_data = chain.invoke({
            "node_name": current_node,
            "documentation": state['documented_nodes'][current_node],
            "dependencies_context": state['context_for_llm'],
            "source_code": state['current_node_info'].get('info', '# Source code not available')
        })

        conceptual_graph = state['conceptual_graph']
        
        base_metadata = state['repo_graph'].nodes[current_node]
        semantic_metadata = response_data.get('semantic_metadata', {})
        
        if not conceptual_graph.has_node(current_node):
            conceptual_graph.add_node(current_node, **base_metadata)
        
        nx.set_node_attributes(conceptual_graph, {current_node: semantic_metadata})

        for edge in response_data.get('semantic_edges', []):
            target_node = edge.get('target')
            if target_node and conceptual_graph.has_node(target_node):
                conceptual_graph.add_edge(current_node, target_node, label=edge.get('label', 'RELATED_TO'))

        final_output_data[current_node] = {
            'documentation': state['documented_nodes'][current_node],
            'conceptual_data': response_data
        }
    except Exception as e:
        print(f"Warning: Failed to process conceptual data for node '{current_node}': {e}")
        final_output_data[current_node] = {
            'documentation': state['documented_nodes'][current_node],
            'conceptual_data': {"error": str(e)}
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
    documented_nodes = state['documented_nodes']
    
    for node in potential_new_nodes:
        if node in documented_nodes or node in nodes_to_document:
            continue 

        dependencies = searcher.get_dependencies(node)
        if all(dep in documented_nodes for dep in dependencies):
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
