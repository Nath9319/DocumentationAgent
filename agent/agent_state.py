# File: agent/agent_state.py
#
# This file defines the structure of the state object for our LangGraph agent.
# ENHANCED VERSION: Added context metadata and quality tracking fields

from typing import TypedDict, List, Dict, Set, Any, Optional
import networkx as nx

class AgentState(TypedDict):
    """
    Defines the state of the documentation agent.
    
    ENHANCED: Added context_metadata field for tracking quality and confidence.

    Attributes:
        repo_graph (nx.MultiDiGraph): The original, AST-based code graph.
        conceptual_graph: (nx.MultiDiGraph): The new, LLM-generated conceptual graph.
        
        nodes_to_process (Set[str]): A master set of all nodes that need processing.
        nodes_to_document (List[str]): A queue of node names that are ready to be documented.
        documented_nodes (Dict[str, str]): A cache mapping a node's name to its documentation.
        
        # A dictionary to hold all final outputs before saving.
        final_output_data: Dict[str, Any]
        
        # Fields for the current loop iteration
        current_node_name (str): The name of the node currently being processed.
        current_node_info (dict): The full attribute dictionary for the current node.
        context_for_llm (str): The compiled context string to be sent to the LLM.
        
        # ENHANCED: New field for context quality metadata
        context_metadata (Dict[str, Any]): Metadata about gathered context including:
            - total_dependencies: number of dependencies identified
            - found: breakdown by source (documented, graph, search, external)
            - confidence_scores: list of confidence scores for each dependency
            - average_confidence: overall confidence in the context
            - validation: results from context validation if performed
        
        # A flag to signal the end of the process.
        is_finished (bool):
    """
    repo_graph: nx.MultiDiGraph
    conceptual_graph: nx.MultiDiGraph
    
    nodes_to_process: Set[str]
    nodes_to_document: List[str]
    documented_nodes: Dict[str, str]
    
    final_output_data: Dict[str, Any]
    
    current_node_name: str
    current_node_info: dict
    context_for_llm: str
    
    # ENHANCED: New metadata field
    context_metadata: Dict[str, Any]
    
    is_finished: bool