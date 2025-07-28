from datetime import datetime
import os
import re
from documentation_state import DocumentationState
import json
from config import logger, INCREMENTAL_SAVE_DIR
from nodes import run_architecture_generation_node, component_loader_node, scrapper_node, selector_node, parallel_writer_node_sync, compiler_node, should_continue_processing
from langgraph.graph import StateGraph, END



workflow = StateGraph(DocumentationState)
workflow.add_node("loader", component_loader_node)
workflow.add_node("scrapper", scrapper_node)
workflow.add_node("selector", selector_node)
# workflow.add_node("parallel_processing", parallel_processing_node_sync)
workflow.add_node("parallel_processing", parallel_writer_node_sync)
workflow.add_node("compiler", compiler_node)
workflow.add_node("architecture_generator", run_architecture_generation_node)
#workflow.add_node("system_synthesis", system_synthesis_node) # Add the new node
#workflow.add_node("diagram_finalizer", diagram_finalizer_node)

workflow.set_entry_point("loader")
workflow.add_conditional_edges("loader", should_continue_processing, {"continue": "scrapper", "end": "compiler"})

# --- FIX: Update the conditional edge to read the decision from the state ---
workflow.add_conditional_edges(
    "scrapper",
    lambda state: state["scrapper_decision"], # Read the decision from the state key
    {"scrap": "loader", "proceed": "selector"}
)

workflow.add_edge("selector", "parallel_processing")
workflow.add_edge("parallel_processing", "loader")
#workflow.add_edge("compiler", "diagram_finalizer")
# --- FIX: Define the final sequence of nodes ---
# This ensures a path exists to your new synthesis node.
workflow.add_edge("compiler", "architecture_generator") # Generate architecture diagram
#workflow.add_edge("system_synthesis", "diagram_finalizer") # Run finalizer with the new model
workflow.add_edge("architecture_generator", END)

app = workflow.compile()
