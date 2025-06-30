# This file wires together all the agent nodes into a stateful graph
# using the LangGraph library. It defines the control flow of the agent.

from langgraph.graph import StateGraph, END
from .agent_state import AgentState
from .agent_nodes import (
    initialize_documentation_queue,
    select_next_node,
    gather_documentation_context,
    generate_documentation,
    save_documentation_and_update_queue,
    should_continue
)

def create_agent_graph() -> StateGraph:
    """
    Creates and configures the LangGraph agent for generating documentation.

    Returns:
        StateGraph: A compiled LangGraph application ready to be invoked.
    """
    # Instantiate the state machine graph.
    graph = StateGraph(AgentState)

    # --- Define the Nodes (Steps) of the Agent ---
    # Each node is a function that modifies the agent's state.
    graph.add_node("initialize_queue", initialize_documentation_queue)
    graph.add_node("select_node", select_next_node)
    graph.add_node("gather_context", gather_documentation_context)
    graph.add_node("generate_doc", generate_documentation)
    graph.add_node("save_and_update", save_documentation_and_update_queue)

    # --- Define the Edges (Control Flow) of the Agent ---

    # 1. Start by initializing the documentation queue.
    graph.set_entry_point("initialize_queue")

    # 2. After initialization, check if there's work to do.
    graph.add_edge("initialize_queue", "select_node")

    # 3. After selecting a node, gather its context.
    graph.add_edge("select_node", "gather_context")

    # 4. After gathering context, generate the documentation.
    graph.add_edge("gather_context", "generate_doc")

    # 5. After generating the documentation, save it and update the queue.
    graph.add_edge("generate_doc", "save_and_update")
    
    # 6. After saving, decide whether to continue or end.
    graph.add_conditional_edges(
        "save_and_update",
        should_continue,
        {
            "continue": "select_node", # Loop back to select the next node.
            "end": END                 # Terminate the process.
        }
    )

    # Compile the graph into a runnable application.
    agent_app = graph.compile()
    
    return agent_app