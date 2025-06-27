# This file defines the structure of the state object for our LangGraph agent.
# The state is a critical component that gets passed between each node (step)
# in the graph, carrying all the necessary information for the agent to do its work.

from typing import TypedDict, List, Dict, Any
import networkx as nx

class AgentState(TypedDict):
    """
    Defines the state of the documentation agent.

    Attributes:
        repo_graph (nx.MultiDiGraph): The complete code graph of the repository.
        nodes_to_document (List[str]): A queue of node names that are ready to be documented.
                                       A node is ready when all its dependencies are documented.
        documented_nodes (Dict[str, str]): A cache mapping a documented node's name
                                           to its generated documentation.
        current_node_name (str): The name of the node currently being processed.
        current_node_info (dict): The full attribute dictionary for the current node.
        context_for_llm (str): The compiled context string (including dependency docs)
                               to be sent to the language model.
        output_dir (str): The directory where documentation files should be saved.
    """
    repo_graph: nx.MultiDiGraph
    nodes_to_document: List[str]
    documented_nodes: Dict[str, str]
    current_node_name: str
    current_node_info: dict
    context_for_llm: str
    output_dir: str