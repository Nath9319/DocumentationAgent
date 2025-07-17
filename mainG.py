
import os
import json
import pickle
import networkx as nx
import asyncio
import logging
from datetime import datetime
from typing import TypedDict, List, Dict, Optional
from dotenv import load_dotenv
# --- tqdm for progress bar ---
from tqdm import tqdm

# Load environment variables from .env file
load_dotenv()

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers.string import StrOutputParser
from langchain_core.output_parsers.json import JsonOutputParser
from langchain_openai import AzureChatOpenAI
from langgraph.graph import StateGraph, END

# --- Configure logging ---

# --- Custom StreamHandler with UTF-8 encoding for emoji support ---
import sys
class StreamHandlerUTF8(logging.StreamHandler):
    def __init__(self, stream=None):
        if stream is None:
            stream = sys.stdout
        # Wrap the stream with UTF-8 encoding if possible
        try:
            stream = open(stream.fileno(), mode='w', encoding='utf-8', buffering=1)
        except Exception:
            pass  # fallback to default if not possible
        super().__init__(stream)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('documentation_generation.log', encoding='utf-8'),
        StreamHandlerUTF8()
    ]
)
logger = logging.getLogger(__name__)

# --- Create output directory for incremental saves ---
INCREMENTAL_SAVE_DIR = "incremental_saves"
os.makedirs(INCREMENTAL_SAVE_DIR, exist_ok=True)

# --- 1. Environment Setup & Model Initialization ---
llm = AzureChatOpenAI(
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("OPENAI_API_VERSION", "2024-02-01"),
    temperature=0.1, # Increased for more creative and better-structured writing
    # max_tokens=40000
)

# --- 2. Define the Hierarchical Documentation Structure & Agent Prompts ---

HIERARCHICAL_STRUCTURE = {
    "Core Repository Documentation": [
        "Project Introduction",
        "Installation & Setup",
    ],
    "Architecture & Design Documentation": [
        "System Architecture",
        # "Design Decision Logs",
        "Logical Architecture",
        # "Physical Architecture",
        "Data Architecture",
        # "Security Architecture",
    ],
    "Development & Operations Documentation": [
        "Code Documentation",
        # "Contributing Guide",
        # "Build & Deployment",
        # "Development Environment",
        # "Code Review Process",
    ],
    "API & Integration Documentation": [
        "API Documentation",
        "Integration Guide",
        # "Sequence Diagrams",
    ],
    "Technical Implementation Details": [
        "Implementation View",
        "Database Schemas",
        # "Error Handling",
        # "Performance Considerations",
    ]
}

ALL_SECTIONS = [subsection for section_list in HIERARCHICAL_STRUCTURE.values() for subsection in section_list]

# --- NEW: Hyper-specific, format-aware prompts ---
AGENT_PROMPTS = {
    "Project Introduction": """
        You are an expert technical writer creating the "Project Introduction". Your tone is engaging and clear.
        Your task is to UPDATE the existing introduction by integrating insights from the component `{component_name}`.
        
        **PRIMARY FOCUS**: Analyze `{component_name}` thoroughly and focus on its high-level purpose, scope, and problem-solving capabilities.
        **REFERENCE CONTEXT**: Use connected components as contextual reference only: {component_context}
        
        **CRITICAL INFORMATION POLICY**:
        - ONLY include information that is explicitly present in the provided documents
        - DO NOT create, infer, or assume any information that is not directly stated
        - If you are uncertain about any detail, it is better to OMIT it rather than include potentially incorrect information
        - Base your documentation strictly on the factual content provided in the component documentation and connected components
        
        **ITERATIVE INTEGRATION POLICY**:
        - This is an ITERATIVE process - preserve all existing valuable information
        - DO NOT overwrite or remove important segments from existing content
        - INTEGRATE new information seamlessly with existing content
        - AVOID creating contradictory information - if there's a conflict, prioritize the most recent and specific information
        - ENHANCE and EXPAND existing sections rather than replacing them
        - Maintain consistency across all iterations
        
        **Output Requirements**:
        - Produce articulated, detailed, technical documentation
        - Use precise technical terminology and industry-standard language
        - Be comprehensive yet concise, covering all relevant aspects
        - Integrate information from all important connected components as supporting context

        **Formatting Instructions:**
        - Use bold (`**...**`) for the project name and key concepts.
        - Use bulleted lists (`- ...`) to highlight primary objectives or features.
        - Keep paragraphs concise and easy to read.

        EXISTING INTRODUCTION:
        ---
        {existing_content}
        ---

        Respond with the complete, updated markdown for the "Project Introduction" section. Do NOT wrap the entire output in triple backticks or code blocks. Only use code blocks for actual code, not for the whole section.
    """,
    "Installation & Setup": """
        You are a technical writer creating a crystal-clear "Installation & Setup" guide.
        
        **PRIMARY FOCUS**: Analyze `{component_name}` for prerequisites, dependencies, environment variables, and setup commands.
        **REFERENCE CONTEXT**: Use connected components as contextual reference only: {component_context}
        
        **CRITICAL INFORMATION POLICY**:
        - ONLY include information that is explicitly present in the provided documents
        - DO NOT create, infer, or assume any information that is not directly stated
        - If you are uncertain about any detail, it is better to OMIT it rather than include potentially incorrect information
        - Base your documentation strictly on the factual content provided in the component documentation and connected components
        
        **ITERATIVE INTEGRATION POLICY**:
        - This is an ITERATIVE process - preserve all existing valuable information
        - DO NOT overwrite or remove important segments from existing content
        - INTEGRATE new information seamlessly with existing content
        - AVOID creating contradictory information - if there's a conflict, prioritize the most recent and specific information
        - ENHANCE and EXPAND existing sections rather than replacing them
        - Maintain consistency across all iterations
        
        **Output Requirements**:
        - Produce articulated, detailed, technical documentation
        - Use precise technical terminology for all setup procedures
        - Be comprehensive yet concise, covering all installation aspects
        - Integrate information from all important connected components as supporting context

        **Formatting Instructions:**
        - Use subheadings like `### Prerequisites` and `### Installation Steps`.
        - Use numbered lists for sequential steps.
        - **ALL** shell commands **MUST** be in code blocks (e.g., ```bash\nnpm install\n```).
        - **ALL** package names, filenames, and environment variables **MUST** be in inline code (e.g., `requests`, `.env`, `DATABASE_URL`).

        EXISTING SETUP GUIDE:
        ---
        {existing_content}
        ---

        Respond with the complete, updated markdown for the "Installation & Setup" section. Do NOT wrap the entire output in triple backticks or code blocks. Only use code blocks for actual code, not for the whole section.
    """,
    "System Architecture": """
        You are a system architect documenting the "System Architecture".
        
        **PRIMARY FOCUS**: Analyze `{component_name}` and explain its architectural role, patterns, and design principles.
        **REFERENCE CONTEXT**: Use connected components as contextual reference only: {component_context}
        
        **CRITICAL INFORMATION POLICY**:
        - ONLY include information that is explicitly present in the provided documents
        - DO NOT create, infer, or assume any information that is not directly stated
        - If you are uncertain about any detail, it is better to OMIT it rather than include potentially incorrect information
        - Base your documentation strictly on the factual content provided in the component documentation and connected components
        
        **ITERATIVE INTEGRATION POLICY**:
        - This is an ITERATIVE process - preserve all existing valuable information
        - DO NOT overwrite or remove important segments from existing content
        - INTEGRATE new information seamlessly with existing content
        - AVOID creating contradictory information - if there's a conflict, prioritize the most recent and specific information
        - ENHANCE and EXPAND existing sections rather than replacing them
        - Maintain consistency across all iterations
        
        **Output Requirements**:
        - Produce articulated, detailed, technical documentation
        - Use precise architectural terminology and design patterns
        - Be comprehensive yet concise, covering all architectural aspects
        - Integrate information from all important connected components as supporting context

        **Formatting Instructions:**
        - Use subheadings (`###`) for each major component or architectural pattern.
        - Use bold (`**...**`) to emphasize key architectural terms (e.g., **Microservices**, **API Gateway**).
        - Use bullet points to describe relationships between components.
        - Use blockquotes (`> **Architectural Note:** ...`) to add rationale or important notes.

        EXISTING ARCHITECTURE DOCUMENTATION:
        ---
        {existing_content}
        ---

        Respond with the complete, updated markdown for the "System Architecture" section. Do NOT wrap the entire output in triple backticks or code blocks. Only use code blocks for actual code, not for the whole section.
    """,
    "API Documentation": """
        You are a meticulous API documentarian creating the "API Documentation".
        
        **PRIMARY FOCUS**: Analyze `{component_name}` for endpoint details, methods, parameters, request/response schemas, and API contracts.
        **REFERENCE CONTEXT**: Use connected components as contextual reference only: {component_context}
        
        **CRITICAL INFORMATION POLICY**:
        - ONLY include information that is explicitly present in the provided documents
        - DO NOT create, infer, or assume any information that is not directly stated
        - If you are uncertain about any detail, it is better to OMIT it rather than include potentially incorrect information
        - Base your documentation strictly on the factual content provided in the component documentation and connected components
        
        **ITERATIVE INTEGRATION POLICY**:
        - This is an ITERATIVE process - preserve all existing valuable information
        - DO NOT overwrite or remove important segments from existing content
        - INTEGRATE new information seamlessly with existing content
        - AVOID creating contradictory information - if there's a conflict, prioritize the most recent and specific information
        - ENHANCE and EXPAND existing sections rather than replacing them
        - Maintain consistency across all iterations
        
        **Output Requirements**:
        - Produce articulated, detailed, technical documentation
        - Use precise API terminology and HTTP standards
        - Be comprehensive yet concise, covering all API aspects
        - Integrate information from all important connected components as supporting context

        **Formatting Instructions:**
        - Use a main subheading (`###`) for the component/endpoint (e.g., `### POST /api/v1/calculate`).
        - **MUST** use a Markdown table for parameters with headers: `| Parameter | Type | Description |`.
        - **MUST** use code blocks with language identifiers for examples (e.g., ```json\n{{"key": "value"}}\n```).
        - Use blockquotes (`> **Note:**`) for important implementation details.
        - Include information about connected components and their relationships.

        EXISTING API DOCUMENTATION:
        ---
        {existing_content}
        ---

        Respond with the complete, updated markdown for the "API Documentation" section. Do NOT wrap the entire output in triple backticks or code blocks. Only use code blocks for actual code, not for the whole section.
    """,
    "Code Documentation": """
        You are a senior developer documenting the codebase in the "Code Documentation" section.
        
        **PRIMARY FOCUS**: Analyze `{component_name}` for its logic, class structure, key functions, algorithms, and implementation details.
        **REFERENCE CONTEXT**: Use connected components as contextual reference only: {component_context}
        
        **CRITICAL INFORMATION POLICY**:
        - ONLY include information that is explicitly present in the provided documents
        - DO NOT create, infer, or assume any information that is not directly stated
        - If you are uncertain about any detail, it is better to OMIT it rather than include potentially incorrect information
        - Base your documentation strictly on the factual content provided in the component documentation and connected components
        
        **ITERATIVE INTEGRATION POLICY**:
        - This is an ITERATIVE process - preserve all existing valuable information
        - DO NOT overwrite or remove important segments from existing content
        - INTEGRATE new information seamlessly with existing content
        - AVOID creating contradictory information - if there's a conflict, prioritize the most recent and specific information
        - ENHANCE and EXPAND existing sections rather than replacing them
        - Maintain consistency across all iterations
        
        **Output Requirements**:
        - Produce articulated, detailed, technical documentation
        - Use precise programming terminology and software engineering concepts
        - Be comprehensive yet concise, covering all code aspects
        - Integrate information from all important connected components as supporting context

        **Formatting Instructions:**
        - Use a subheading (`###`) for the component/module name (e.g., `### Module: 'stats_service.py'`).
        - For key functions, use smaller subheadings (`####`) and describe their purpose.
        - **MUST** use a Markdown table for parameters and return values.
        - **MUST** include well-commented code snippets in code blocks (e.g., ```python\n# code here\n```).

        EXISTING CODE DOCUMENTATION:
        ---
        {existing_content}
        ---

        Respond with the complete, updated markdown for the "Code Documentation" section. Do NOT wrap the entire output in triple backticks or code blocks. Only use code blocks for actual code, not for the whole section.
    """,
    "Data Architecture": """
        You are a data architect documenting the "Data Architecture".
        
        **PRIMARY FOCUS**: Analyze `{component_name}` for database interactions, schemas, data models, data flow, and storage patterns.
        **REFERENCE CONTEXT**: Use connected components as contextual reference only: {component_context}
        
        **CRITICAL INFORMATION POLICY**:
        - ONLY include information that is explicitly present in the provided documents
        - DO NOT create, infer, or assume any information that is not directly stated
        - If you are uncertain about any detail, it is better to OMIT it rather than include potentially incorrect information
        - Base your documentation strictly on the factual content provided in the component documentation and connected components
        
        **ITERATIVE INTEGRATION POLICY**:
        - This is an ITERATIVE process - preserve all existing valuable information
        - DO NOT overwrite or remove important segments from existing content
        - INTEGRATE new information seamlessly with existing content
        - AVOID creating contradictory information - if there's a conflict, prioritize the most recent and specific information
        - ENHANCE and EXPAND existing sections rather than replacing them
        - Maintain consistency across all iterations
        
        **Output Requirements**:
        - Produce articulated, detailed, technical documentation
        - Use precise data architecture terminology and database concepts
        - Be comprehensive yet concise, covering all data aspects
        - Integrate information from all important connected components as supporting context

        **Formatting Instructions:**
        - Use subheadings (`###`) for different data models or database tables.
        - **MUST** use Markdown tables to describe table schemas with headers: `| Column | Type | Constraints | Description |`.
        - **MUST** use code blocks (```sql ... ```) for SQL schema definitions or important queries.

        EXISTING DATA ARCHITECTURE DOCUMENTATION:
        ---
        {existing_content}
        ---

        Respond with the complete, updated markdown for the "Data Architecture" section. Do NOT wrap the entire output in triple backticks or code blocks. Only use code blocks for actual code, not for the whole section.
    """,
    "Logical Architecture": """
        You are a software architect documenting the "Logical Architecture".
        
        **PRIMARY FOCUS**: Analyze `{component_name}` for its logical structure, component relationships, interfaces, and architectural patterns.
        **REFERENCE CONTEXT**: Use connected components as contextual reference only: {component_context}
        
        **CRITICAL INFORMATION POLICY**:
        - ONLY include information that is explicitly present in the provided documents
        - DO NOT create, infer, or assume any information that is not directly stated
        - If you are uncertain about any detail, it is better to OMIT it rather than include potentially incorrect information
        - Base your documentation strictly on the factual content provided in the component documentation and connected components
        
        **ITERATIVE INTEGRATION POLICY**:
        - This is an ITERATIVE process - preserve all existing valuable information
        - DO NOT overwrite or remove important segments from existing content
        - INTEGRATE new information seamlessly with existing content
        - AVOID creating contradictory information - if there's a conflict, prioritize the most recent and specific information
        - ENHANCE and EXPAND existing sections rather than replacing them
        - Maintain consistency across all iterations
        
        **Output Requirements**:
        - Produce articulated, detailed, technical documentation
        - Use precise logical architecture terminology and design patterns
        - Be comprehensive yet concise, covering all logical aspects
        - Integrate information from all important connected components as supporting context

        **Formatting Instructions:**
        - Use subheadings (`###`) for logical components and layers.
        - Use bullet points to describe component interactions and data flow.
        - Use blockquotes (`> **Design Principle:** ...`) for architectural decisions.

        EXISTING LOGICAL ARCHITECTURE DOCUMENTATION:
        ---
        {existing_content}
        ---

        Respond with the complete, updated markdown for the "Logical Architecture" section. Do NOT wrap the entire output in triple backticks or code blocks. Only use code blocks for actual code, not for the whole section.
    """,
    "Integration Guide": """
        You are an integration specialist documenting the "Integration Guide".
        
        **PRIMARY FOCUS**: Analyze `{component_name}` for integration patterns, APIs, protocols, and connectivity requirements.
        **REFERENCE CONTEXT**: Use connected components as contextual reference only: {component_context}
        
        **CRITICAL INFORMATION POLICY**:
        - ONLY include information that is explicitly present in the provided documents
        - DO NOT create, infer, or assume any information that is not directly stated
        - If you are uncertain about any detail, it is better to OMIT it rather than include potentially incorrect information
        - Base your documentation strictly on the factual content provided in the component documentation and connected components
        
        **ITERATIVE INTEGRATION POLICY**:
        - This is an ITERATIVE process - preserve all existing valuable information
        - DO NOT overwrite or remove important segments from existing content
        - INTEGRATE new information seamlessly with existing content
        - AVOID creating contradictory information - if there's a conflict, prioritize the most recent and specific information
        - ENHANCE and EXPAND existing sections rather than replacing them
        - Maintain consistency across all iterations
        
        **Output Requirements**:
        - Produce articulated, detailed, technical documentation
        - Use precise integration terminology and protocol specifications
        - Be comprehensive yet concise, covering all integration aspects
        - Integrate information from all important connected components as supporting context

        **Formatting Instructions:**
        - Use subheadings (`###`) for different integration scenarios.
        - Use code blocks for configuration examples and API calls.
        - Use bullet points for step-by-step integration procedures.

        EXISTING INTEGRATION GUIDE:
        ---
        {existing_content}
        ---

        Respond with the complete, updated markdown for the "Integration Guide" section. Do NOT wrap the entire output in triple backticks or code blocks. Only use code blocks for actual code, not for the whole section.
    """,
    "Implementation View": """
        You are a technical architect documenting the "Implementation View".
        
        **PRIMARY FOCUS**: Analyze `{component_name}` for implementation details, deployment patterns, runtime behavior, and technical specifications.
        **REFERENCE CONTEXT**: Use connected components as contextual reference only: {component_context}
        
        **CRITICAL INFORMATION POLICY**:
        - ONLY include information that is explicitly present in the provided documents
        - DO NOT create, infer, or assume any information that is not directly stated
        - If you are uncertain about any detail, it is better to OMIT it rather than include potentially incorrect information
        - Base your documentation strictly on the factual content provided in the component documentation and connected components
        
        **ITERATIVE INTEGRATION POLICY**:
        - This is an ITERATIVE process - preserve all existing valuable information
        - DO NOT overwrite or remove important segments from existing content
        - INTEGRATE new information seamlessly with existing content
        - AVOID creating contradictory information - if there's a conflict, prioritize the most recent and specific information
        - ENHANCE and EXPAND existing sections rather than replacing them
        - Maintain consistency across all iterations
        
        **Output Requirements**:
        - Produce articulated, detailed, technical documentation
        - Use precise implementation terminology and technical specifications
        - Be comprehensive yet concise, covering all implementation aspects
        - Integrate information from all important connected components as supporting context

        **Formatting Instructions:**
        - Use subheadings (`###`) for implementation aspects and deployment scenarios.
        - Use code blocks for configuration and deployment scripts.
        - Use tables for technical specifications and requirements.

        EXISTING IMPLEMENTATION VIEW:
        ---
        {existing_content}
        ---

        Respond with the complete, updated markdown for the "Implementation View" section. Do NOT wrap the entire output in triple backticks or code blocks. Only use code blocks for actual code, not for the whole section.
    """,
    "Database Schemas": """
        You are a database architect documenting the "Database Schemas".
        
        **PRIMARY FOCUS**: Analyze `{component_name}` for database schemas, table structures, relationships, and data constraints.
        **REFERENCE CONTEXT**: Use connected components as contextual reference only: {component_context}
        
        **CRITICAL INFORMATION POLICY**:
        - ONLY include information that is explicitly present in the provided documents
        - DO NOT create, infer, or assume any information that is not directly stated
        - If you are uncertain about any detail, it is better to OMIT it rather than include potentially incorrect information
        - Base your documentation strictly on the factual content provided in the component documentation and connected components
        
        **Output Requirements**:
        - Produce articulated, detailed, technical documentation
        - Use precise database terminology and schema specifications
        - Be comprehensive yet concise, covering all database aspects
        - Integrate information from all important connected components as supporting context

        **Formatting Instructions:**
        - Use subheadings (`###`) for different schemas and table groups.
        - **MUST** use Markdown tables for schema definitions with headers: `| Column | Type | Constraints | Description |`.
        - Use code blocks (```sql ... ```) for DDL statements and important queries.

        EXISTING DATABASE SCHEMAS:
        ---
        {existing_content}
        ---

        Respond with the complete, updated markdown for the "Database Schemas" section. Do NOT wrap the entire output in triple backticks or code blocks. Only use code blocks for actual code, not for the whole section.
    """
}


# --- 3. Define the Graph's State ---
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


# --- Helper Functions for Incremental Saving ---

# --- Sanitize filenames for Windows compatibility ---
import re
def sanitize_filename(name: str) -> str:
    """Replace invalid filename characters with underscores."""
    return re.sub(r'[:\\/*?"<>|]', '_', name)

def save_incremental_progress(state: DocumentationState, operation: str):
    """Save incremental progress after each major operation."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    current_component = state.get("current_component_name", "unknown")
    safe_component = sanitize_filename(str(current_component))
    safe_operation = sanitize_filename(str(operation))
    # Create filename with timestamp and operation, sanitized
    filename = f"{timestamp}_{safe_operation}_{safe_component}.json"
    filepath = os.path.join(INCREMENTAL_SAVE_DIR, filename)
    
    # Create a serializable version of the state
    serializable_state = {
        "timestamp": timestamp,
        "operation": operation,
        "current_component_name": state.get("current_component_name"),
        "processed_components": len(state.get("all_data", {})) - len(state.get("unprocessed_components", [])),
        "total_components": len(state.get("all_data", {})),
        "target_sections": state.get("target_sections", []),
        "document_content": state.get("document_content", {}),
        "connected_nodes_count": len(state.get("connected_nodes", [])),
        "scrapper_decision": state.get("scrapper_decision", "")
    }
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(serializable_state, f, indent=2, ensure_ascii=False)
        logger.info(f"💾 Incremental progress saved: {filepath}")
    except Exception as e:
        logger.error(f"❌ Failed to save incremental progress: {e}")

def save_section_content(component_name: str, section_name: str, content: str):
    """Save individual section content after each LLM call."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_component = sanitize_filename(str(component_name))
    safe_section = sanitize_filename(str(section_name.replace(' ', '_')))
    # Create section-specific directory (sanitized)
    section_dir = os.path.join(INCREMENTAL_SAVE_DIR, "sections", safe_component)
    os.makedirs(section_dir, exist_ok=True)
    # Save section content (sanitized)
    filename = f"{timestamp}_{safe_section}.md"
    filepath = os.path.join(section_dir, filename)
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# {section_name}\n\n")
            f.write(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
            f.write(f"*Component: {component_name}*\n\n")
            f.write("---\n\n")
            f.write(content)
        logger.info(f"💾 Section content saved: {filepath}")
    except Exception as e:
        logger.error(f"❌ Failed to save section content: {e}")

# --- 4. Agent Node Functions ---

def load_all_data(json_path: str, graph_path: str) -> Dict:
    """Loads all initial data."""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            doc_data = json.load(f)
        with open(graph_path, 'rb') as f:
            graph_data = pickle.load(f)
        return {"all_data": doc_data, "nx_graph": graph_data}
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return {}

def component_loader_node(state: DocumentationState) -> DocumentationState:
    """Pops the next component and loads its data including connected nodes into the state."""
    if not state["unprocessed_components"]:
        logger.info("🔄 No more components to process")
        return state
    
    component_name = state["unprocessed_components"].pop(0)
    logger.info(f"📥 Loading component: '{component_name}' ({len(state['unprocessed_components'])} remaining)")
    print(f"\n--- 📥 Loader: Loading component '{component_name}' ---")
    
    state["current_component_name"] = component_name
    component_data = state["all_data"][component_name]
    state["current_component_doc"] = component_data["documentation"]
    
    # Extract connected nodes from the graph
    graph = state["nx_graph"]
    connected_nodes_info = []
    
    if component_name in graph:
        # Get all neighbors (connected nodes)
        neighbors = list(nx.all_neighbors(graph, component_name))
        logger.info(f"🔗 Found {len(neighbors)} connected nodes for '{component_name}'")
        
        for neighbor in neighbors:
            if neighbor in state['all_data']:
                neighbor_data = state['all_data'][neighbor]
                
                # Get edge information between current node and neighbor
                edge_data = graph.get_edge_data(component_name, neighbor)
                edge_label = edge_data.get('label', 'RELATED_TO') if edge_data else 'RELATED_TO'
                
                # Extract neighbor's key information
                neighbor_info = {
                    'name': neighbor,
                    'relationship': edge_label,
                    'summary': neighbor_data.get('conceptual_data', {}).get('semantic_metadata', {}).get('summary', 'No summary available'),
                    'type': neighbor_data.get('conceptual_data', {}).get('semantic_metadata', {}).get('type', 'Unknown'),
                    'documentation': neighbor_data.get('documentation', ''),
                    'confidence': neighbor_data.get('context_metadata', {}).get('average_confidence', 0.0)
                }
                connected_nodes_info.append(neighbor_info)
    
    # Build enhanced context with connected nodes
    if connected_nodes_info:
        context_parts = [f"**Connected Components ({len(connected_nodes_info)} found):**\n"]
        
        for node_info in connected_nodes_info:
            context_parts.append(f"- **{node_info['name']}** ({node_info['type']})")
            context_parts.append(f"  - *Relationship*: {node_info['relationship']}")
            context_parts.append(f"  - *Summary*: {node_info['summary']}")
            context_parts.append(f"  - *Confidence*: {node_info['confidence']:.2f}")
            
            # Include brief documentation if available
            if node_info['documentation'] and len(node_info['documentation']) > 50:
                doc_preview = node_info['documentation'][:200] + "..." if len(node_info['documentation']) > 200 else node_info['documentation']
                context_parts.append(f"  - *Documentation*: {doc_preview}")
            context_parts.append("")
        
        context = "\n".join(context_parts)
    else:
        context = "This component operates independently with no direct connections found in the graph."
        logger.info(f"🔍 No connected nodes found for '{component_name}'")
    
    state["current_component_context"] = context
    
    # Store connected nodes info for use in other agents
    state["connected_nodes"] = connected_nodes_info
    
    # Save incremental progress
    save_incremental_progress(state, "component_loaded")
    
    logger.info(f"✅ Component '{component_name}' loaded successfully with {len(connected_nodes_info)} connected nodes")
    print(f"--- 📥 Loader: Found {len(connected_nodes_info)} connected nodes ---")
    return state

def scrapper_node(state: DocumentationState) -> dict:
    """Decides if the component's documentation is substantial and updates the state with the decision."""
    component_name = state['current_component_name']
    logger.info(f"🗑️ Scrapper: Analyzing component '{component_name}'")
    print(f"--- 🗑️ Scrapper: Analyzing '{component_name}' ---")
    
    doc_length = len(state['current_component_doc'].split())
    logger.info(f"📊 Document length: {doc_length} words")
    
    decision = "proceed"  # Default decision
    if doc_length < 10:
        logger.info(f"❌ Decision: SCRAP (document too short: {doc_length} words)")
        print(f"--- 🗑️ Scrapper: Decision is to SCRAP (too short). ---")
        decision = "scrap"
    else:
        logger.info(f"🤖 Consulting LLM for decision on '{component_name}'")
        prompt = ChatPromptTemplate.from_template(
            """Analyze the documentation for component `{component_name}`. Is it trivial (e.g., a simple import, a variable declaration) or substantial (describes logic, a class, a function, configuration)?
            Documentation: --- {component_doc} ---
            Respond with a single word: "Proceed" if substantial, or "Scrap" if trivial."""
        )
        chain = prompt | llm | StrOutputParser()
        llm_decision = chain.invoke({"component_name": component_name, "component_doc": state["current_component_doc"]})
        
        if "Scrap" in llm_decision:
            logger.info(f"❌ LLM Decision: SCRAP for '{component_name}'")
            print(f"--- 🗑️ Scrapper: Decision is to SCRAP. ---")
            decision = "scrap"
        else:
            logger.info(f"✅ LLM Decision: PROCEED for '{component_name}'")
            print(f"--- 🗑️ Scrapper: Decision is to PROCEED. ---")
            decision = "proceed"
    
    # Save incremental progress
    save_incremental_progress(state, f"scrapper_{decision}")
    
    # Return a dictionary to update the state, this is the main fix.
    return {"scrapper_decision": decision}

def selector_node(state: DocumentationState) -> DocumentationState:
    """Selects which documentation sections are relevant for the current component and its connections."""
    component_name = state['current_component_name']
    logger.info(f"🎯 Selector: Choosing sections for '{component_name}'")
    print(f"--- 🎯 Selector: Choosing sections for '{component_name}' ---")
    
    # Include connected nodes information in the selection process
    connected_nodes_summary = ""
    if state.get("connected_nodes"):
        connected_nodes_summary = f"\n\nConnected Components:\n"
        for node in state["connected_nodes"]:
            connected_nodes_summary += f"- {node['name']} ({node['type']}): {node['summary']}\n"
    
    logger.info(f"🤖 Consulting LLM for section selection for '{component_name}'")
    prompt = ChatPromptTemplate.from_template(
        """You are a document routing expert. Based on the documentation for component `{component_name}` and its connected components, select ALL sections where this information would be relevant.
        
        Component Documentation: --- {component_doc} ---
        {connected_nodes_summary}
        Available Sections: {sections}
        
        Consider the relationships and dependencies when selecting sections. For example:
        - If connected to API endpoints, include "API Documentation"
        - If connected to database operations, include "Data Architecture"
        - If connected to error handling, include "Error Handling"
        
        Respond with a JSON object containing a single key "relevant_sections" which is a list of strings from the available sections.
        Example: {{"relevant_sections": ["API Documentation", "Error Handling"]}}"""
    )
    
    section_list_str = "\n".join([f"- {s}" for s in ALL_SECTIONS])
    chain = prompt | llm | JsonOutputParser()
    
    response = chain.invoke({
        "component_name": component_name, 
        "component_doc": state["current_component_doc"], 
        "connected_nodes_summary": connected_nodes_summary,
        "sections": section_list_str
    })
    
    relevant_sections = response.get("relevant_sections", [])
    state["target_sections"] = [s for s in relevant_sections if s in ALL_SECTIONS]
    
    logger.info(f"✅ Selected {len(state['target_sections'])} sections for '{component_name}': {state['target_sections']}")
    print(f"--- 🎯 Selector: Chosen sections: {state['target_sections']} ---")
    
    # Save incremental progress
    save_incremental_progress(state, "sections_selected")
    
    return state

async def parallel_writer_node(state: DocumentationState) -> DocumentationState:
    """Invokes the specialist writer agents in parallel for the selected sections using async/await."""
    component_name = state['current_component_name']
    logger.info(f"✍️ Parallel Writers: Starting for '{component_name}' with {len(state['target_sections'])} sections")
    print(f"--- ✍️ Parallel Writers: Starting for '{component_name}' ---")
    
    async def process_section(section_name: str) -> tuple[str, str]:
        """Process a single section asynchronously and return (section_name, content)."""
        logger.info(f"🔄 Processing section: '{section_name}' for component '{component_name}'")
        print(f"    - Invoking writer for section: '{section_name}'")
        
        writer_prompt_template = AGENT_PROMPTS.get(section_name, 
            """You are a technical writer. Your task is to update the \"{section_name}\" section.
            
            **CRITICAL INFORMATION POLICY**:
            - ONLY include information that is explicitly present in the provided documents
            - DO NOT create, infer, or assume any information that is not directly stated
            - If you are uncertain about any detail, it is better to OMIT it rather than include potentially incorrect information
            - Base your documentation strictly on the factual content provided in the component documentation
            
            Analyze `{component_name}` and integrate any relevant information into the existing content.
            Use rich markdown like code blocks, tables, and lists to format the information clearly.
            EXISTING CONTENT: --- {existing_content} ---
            NEW INFORMATION: --- {component_doc} ---
            Respond with the complete, updated markdown for the \"{section_name}\" section."""
        )
        
        existing_content = state["document_content"].get(section_name, "")
        prompt = ChatPromptTemplate.from_template(writer_prompt_template)
        chain = prompt | llm | StrOutputParser()
        
        # Use async invoke for concurrent LLM calls
        try:
            logger.info(f"🤖 Calling LLM for section '{section_name}' in component '{component_name}'")
            updated_section_content = await chain.ainvoke({
                "section_name": section_name,
                "existing_content": existing_content or "This section is empty. Please start it.",
                "component_name": component_name,
                "component_doc": state["current_component_doc"],
                "component_context": state["current_component_context"]
            })
            
            # Save section content after LLM call
            save_section_content(component_name, section_name, updated_section_content)
            
            logger.info(f"✅ Section '{section_name}' completed for component '{component_name}'")
            print(f"    - ✅ Writer for '{section_name}' finished.")
            return section_name, updated_section_content
            
        except Exception as e:
            logger.error(f"❌ Error processing section '{section_name}' for component '{component_name}': {e}")
            print(f"    - ❌ Error in writer for '{section_name}': {e}")
            return section_name, f"Error generating content for {section_name}: {str(e)}"
    
    # Use asyncio.gather for concurrent execution of all sections
    try:
        # Create tasks for all sections
        tasks = [process_section(section_name) for section_name in state["target_sections"]]
        
        # Execute all tasks concurrently
        logger.info(f"🚀 Executing {len(tasks)} LLM calls concurrently for '{component_name}'")
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results and handle any exceptions
        successful_sections = 0
        failed_sections = 0
        
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"❌ Writer exception for '{component_name}': {result}")
                print(f"    - ❌ Writer generated an exception: {result}")
                failed_sections += 1
            else:
                section_name, content = result
                state["document_content"][section_name] = content
                successful_sections += 1
                
        logger.info(f"📊 Parallel Writers completed for '{component_name}': {successful_sections} successful, {failed_sections} failed")
                
    except Exception as exc:
        logger.error(f"❌ Parallel writers failed for '{component_name}': {exc}")
        print(f"    - ❌ Parallel writers failed with exception: {exc}")
    
    # Save incremental progress
    save_incremental_progress(state, "parallel_writers_completed")
    
    logger.info(f"✅ Parallel Writers: Completed all {len(state['target_sections'])} sections for '{component_name}'")
    print(f"--- ✍️ Parallel Writers: Completed all {len(state['target_sections'])} sections ---")
    return state

def parallel_writer_node_sync(state: DocumentationState) -> DocumentationState:
    """Synchronous wrapper for the async parallel_writer_node function."""
    return asyncio.run(parallel_writer_node(state))

def compiler_node(state: DocumentationState) -> DocumentationState:
    """Assembles all the final sections into the complete, hierarchical document."""
    logger.info("📚 Compiler: Starting document assembly")
    print("--- 📚 Compiler: Assembling Final Document ---")

    import re
    def strip_triple_backticks(text: str) -> str:
        # Remove wrapping triple backticks (with or without language) from the whole section
        pattern = r"^```[a-zA-Z]*\n([\s\S]*?)\n```$"
        return re.sub(pattern, r"\1", text.strip(), flags=re.MULTILINE)

    final_doc_parts = []
    sections_included = 0

    for main_section, subsections in HIERARCHICAL_STRUCTURE.items():
        # Check if any subsection within this main section has content
        section_has_content = any(state["document_content"].get(sub, "").strip() for sub in subsections)

        # Only add the main section header if it has content
        if section_has_content:
            final_doc_parts.append(f"# {main_section}")
            logger.info(f"📝 Adding main section: {main_section}")

            for subsection_name in subsections:
                content = state["document_content"].get(subsection_name, "").strip()
                if content:
                    # Remove wrapping triple backticks if present
                    cleaned_content = strip_triple_backticks(content)
                    final_doc_parts.append(f"## {subsection_name}\n\n{cleaned_content}")
                    sections_included += 1
                    logger.info(f"📄 Added subsection: {subsection_name}")

    state["final_document"] = "\n\n---\n\n".join(final_doc_parts)

    logger.info(f"✅ Compiler: Document assembled with {sections_included} sections")
    print("--- 🎉 Compiler: Final document assembled! ---")

    # Save final document progress
    save_incremental_progress(state, "final_document_compiled")

    return state

# --- 5. Define Graph Edges & Control Flow ---

def should_continue_processing(state: DocumentationState) -> str:
    """Determines if there are more components to process."""
    return "continue" if state["unprocessed_components"] else "end"

# --- 6. Build and Run the Graph ---

workflow = StateGraph(DocumentationState)
workflow.add_node("loader", component_loader_node)
workflow.add_node("scrapper", scrapper_node)
workflow.add_node("selector", selector_node)
workflow.add_node("parallel_writers", parallel_writer_node_sync)
workflow.add_node("compiler", compiler_node)

workflow.set_entry_point("loader")
workflow.add_conditional_edges("loader", should_continue_processing, {"continue": "scrapper", "end": "compiler"})

# --- FIX: Update the conditional edge to read the decision from the state ---
workflow.add_conditional_edges(
    "scrapper",
    lambda state: state["scrapper_decision"], # Read the decision from the state key
    {"scrap": "loader", "proceed": "selector"}
)

workflow.add_edge("selector", "parallel_writers")
workflow.add_edge("parallel_writers", "loader")
workflow.add_edge("compiler", END)

app = workflow.compile()

# --- Main execution block ---
if __name__ == "__main__":
    start_time = datetime.now()

    JSON_FILE = "output/CalculatorCode/documentation_and_graph_data.json"
    GRAPH_FILE = "output/CalculatorCode/conceptual_graph.pkl"
    FINAL_DOC_DIR = "final_docs"
    os.makedirs(FINAL_DOC_DIR, exist_ok=True)
    OUTPUT_FILE_BASE = "Complete_Technical_Documentation.md"
    OUTPUT_FILE = os.path.join(FINAL_DOC_DIR, OUTPUT_FILE_BASE)

    logger.info("🚀 Starting documentation generation process")
    logger.info(f"📁 JSON file: {JSON_FILE}")
    logger.info(f"📁 Graph file: {GRAPH_FILE}")
    logger.info(f"📁 Output file: {OUTPUT_FILE}")

    initial_data = load_all_data(JSON_FILE, GRAPH_FILE)
    if initial_data:
        total_components = len(initial_data["all_data"])
        logger.info(f"📊 Total components to process: {total_components}")

        # Use tqdm to show progress of component processing
        component_names = sorted(initial_data["all_data"].keys())
        progress_bar = tqdm(component_names, desc="Processing components", unit="component")


        # We'll update the progress bar in the loader node
        # Patch the loader node to update tqdm and show current file/component
        original_loader = component_loader_node
        def loader_with_progress(state):
            # Show the current component name in the tqdm bar
            next_component = None
            if state["unprocessed_components"]:
                next_component = state["unprocessed_components"][0]
            else:
                # If none left, show last processed
                next_component = state.get("current_component_name", "Done")
            progress_bar.set_description(f"Processing: {next_component} ({progress_bar.n+1}/{progress_bar.total})")
            result = original_loader(state)
            if progress_bar.n < progress_bar.total:
                progress_bar.update(1)
            return result

        # Patch the workflow node
        workflow.update_node("loader", loader_with_progress)

        initial_state = DocumentationState(
            unprocessed_components=component_names.copy(),
            all_data=initial_data["all_data"],
            nx_graph=initial_data["nx_graph"],
            document_content={section: "" for section in ALL_SECTIONS},
            current_component_name=None,
            current_component_doc=None,
            current_component_context=None,
            target_sections=[],
            final_document=None,
            scrapper_decision="",
            connected_nodes=[]
        )

        config = {"recursion_limit": total_components * 4 + 15}
        logger.info(f"⚙️ Graph recursion limit set to: {config['recursion_limit']}")
        print(f"--- ⚙️ Running graph with recursion limit: {config['recursion_limit']} ---")

        try:
            final_state = app.invoke(initial_state, config=config)
            progress_bar.close()


            if final_state and final_state.get("final_document"):
                # --- Save final document in versioned manner ---
                def get_versioned_filename(base_path):
                    base_dir, base_name = os.path.split(base_path)
                    name, ext = os.path.splitext(base_name)
                    version = 1
                    candidate = os.path.join(base_dir, base_name)
                    while os.path.exists(candidate):
                        candidate = os.path.join(base_dir, f"{name}_v{version}{ext}")
                        version += 1
                    return candidate

                save_path = get_versioned_filename(OUTPUT_FILE)
                with open(save_path, "w", encoding="utf-8") as f:
                    f.write(final_state["final_document"])

                # Save final state as JSON
                final_state_file = os.path.join(INCREMENTAL_SAVE_DIR, f"final_state_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
                save_incremental_progress(final_state, "final_completion")

                end_time = datetime.now()
                duration = end_time - start_time

                logger.info(f"🎉 Success! Documentation generation completed in {duration}")
                logger.info(f"📝 Final document saved to: {save_path}")
                logger.info(f"📊 Document length: {len(final_state['final_document'])} characters")
                logger.info(f"📁 Incremental saves stored in: {INCREMENTAL_SAVE_DIR}")

                print(f"\n🚀 Success! Documentation saved to '{save_path}'")
                print(f"⏱️ Total processing time: {duration}")
                print(f"📁 Incremental saves: {INCREMENTAL_SAVE_DIR}")

            else:
                logger.error("❌ Failure: The final document could not be generated")
                print("\n❌ Failure: The final document could not be generated.")

        except Exception as e:
            logger.error(f"❌ Critical error during documentation generation: {e}")
            print(f"\n❌ Critical error: {e}")

    else:
        logger.error("❌ Failed to load initial data")
        print("❌ Failed to load initial data")