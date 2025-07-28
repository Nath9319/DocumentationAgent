from typing import TypedDict, List, Dict, Optional
import networkx as nx
class DocumentationState(TypedDict):
    unprocessed_components: List[str]
    all_data: Dict
    nx_graph: nx.Graph
    document_content: Dict[str, str]
    current_component_name: Optional[str]
    current_component_doc: Optional[str]
    current_component_context: Optional[str]
    target_sections: List[str]
    final_document: Optional[str]
    # --- FIX: Add a key to store the scrapper's decision ---
    scrapper_decision: str
    connected_nodes: List[Dict]  # New field for connected nodes information
    # --- NEW: Architectural diagram fields ---
    architectural_components: Dict[str, Dict]  # Store component info for diagram
    architectural_relationships: List[Dict]  # Store relationships between components
    diagram_mermaid_code: str  # Current mermaid diagram code
    diagram_description: str  # Natural language description of architecture

