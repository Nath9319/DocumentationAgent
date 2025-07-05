# File: agent/agent_graph.py
#
# This file wires together all the agent nodes into a stateful graph
# using the LangGraph library. This version has a more robust control flow.
from langchain_core.runnables import RunnableLambda
from langgraph.graph import StateGraph, END
from .agent_state import AgentState
from .agent_nodes import (
    initialize_documentation_queue,
    select_next_node,
    gather_documentation_context,
    generate_documentation,
    generate_conceptual_graph_data,
    update_documentation_queue,
    should_continue
)

def create_agent_graph() -> StateGraph:
    """
    Creates and configures the LangGraph agent for dual graph generation.
    """
    graph = StateGraph(AgentState)

    # Define the Nodes
    graph.add_node("initialize_queue", initialize_documentation_queue)
    graph.add_node("select_node", select_next_node)
    graph.add_node("gather_context", gather_documentation_context)
    graph.add_node("generate_doc", generate_documentation)
    graph.add_node("generate_conceptual_data", generate_conceptual_graph_data)
    graph.add_node("update_queue", update_documentation_queue)

    # Define the Edges (Control Flow)
    graph.set_entry_point("initialize_queue")
    
    # After initialization, always try to select a node.
    graph.add_edge("initialize_queue", "select_node")
    
    # --- THIS IS THE FIX: The main control router ---
    # After selecting a node, decide if the process is finished or needs to continue.
    '''graph.add_conditional_edges(
        "select_node",
        # A simple router based on whether the 'is_finished' flag was set.
        lambda x: "end" if x.get("is_finished") else "continue",
        {
            "continue": "gather_context", # If not finished, proceed with documentation.
            "end": END,                   # If finished, terminate the graph.
        }
    )
    '''
    # Define the condition function
    def condition_router(state):
        return "end" if state.get("is_finished") else "continue"

    # Wrap it with RunnableLambda and give it a name
    condition_runnable = RunnableLambda(condition_router)
    condition_runnable.name = "condition_router"

    # Now use it in add_conditional_edges
    graph.add_conditional_edges(
        "select_node",
        condition_runnable,
        {
            "continue": "gather_context",
            "end": END,
        }
    )
    # Define the condition function

    graph.add_edge("gather_context", "generate_doc")
    graph.add_edge("generate_doc", "generate_conceptual_data")
    graph.add_edge("generate_conceptual_data", "update_queue")
    
    # After updating the queue, always loop back to select the next node.
    graph.add_edge("update_queue", "select_node")

    agent_app = graph.compile()
    return agent_app
