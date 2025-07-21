import os
import json
import pickle
import networkx as nx
import asyncio
import logging
import re
import sys
from datetime import datetime
from typing import TypedDict, List, Dict, Optional
from dotenv import load_dotenv
# --- tqdm for progress bar ---
from tqdm import tqdm

# Set UTF-8 encoding for Windows console to handle emojis
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

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

# --- Global progress bar variable ---
progress_bar = None

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
    # --- NEW: Architectural diagram fields ---
    architectural_components: Dict[str, Dict]  # Store component info for diagram
    architectural_relationships: List[Dict]  # Store relationships between components
    diagram_mermaid_code: str  # Current mermaid diagram code
    diagram_description: str  # Natural language description of architecture


# --- Helper Functions for Incremental Saving ---

# --- Sanitize filenames for Windows compatibility ---
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
        "scrapper_decision": state.get("scrapper_decision", ""),
        # Add architectural data to incremental saves
        "architectural_components_count": len(state.get("architectural_components", {})),
        "architectural_relationships_count": len(state.get("architectural_relationships", [])),
        "diagram_mermaid_lines": len(state.get("diagram_mermaid_code", "").split('\n')),
        "diagram_description_length": len(state.get("diagram_description", ""))
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

def save_llm_interaction(component_name: str, interaction_type: str, prompt: str, response: str, metadata: dict = None):
    """Save detailed LLM interaction for debugging and analysis."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_component = sanitize_filename(str(component_name))
    safe_interaction = sanitize_filename(str(interaction_type))
    
    # Create LLM-specific directory
    llm_dir = os.path.join(INCREMENTAL_SAVE_DIR, "llm_interactions", safe_component)
    os.makedirs(llm_dir, exist_ok=True)
    
    # Create detailed interaction record
    interaction_record = {
        "timestamp": timestamp,
        "component": component_name,
        "interaction_type": interaction_type,
        "metadata": metadata or {},
        "prompt": prompt,
        "response": response,
        "response_length": len(response),
        "prompt_length": len(prompt)
    }
    
    filename = f"{timestamp}_{safe_interaction}.json"
    filepath = os.path.join(llm_dir, filename)
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(interaction_record, f, indent=2, ensure_ascii=False)
        logger.info(f"🤖 LLM interaction saved: {filepath}")
    except Exception as e:
        logger.error(f"❌ Failed to save LLM interaction: {e}")

def log_processing_summary():
    """Log a comprehensive summary of all saved files and processing stats."""
    logger.info("📊 PROCESSING SUMMARY:")
    
    # Count files in incremental saves
    if os.path.exists(INCREMENTAL_SAVE_DIR):
        total_files = 0
        
        # Count main progress files
        progress_files = [f for f in os.listdir(INCREMENTAL_SAVE_DIR) if f.endswith('.json')]
        total_files += len(progress_files)
        logger.info(f"📄 Progress files: {len(progress_files)}")
        
        # Count section files
        sections_dir = os.path.join(INCREMENTAL_SAVE_DIR, "sections")
        if os.path.exists(sections_dir):
            section_count = 0
            for component_dir in os.listdir(sections_dir):
                comp_path = os.path.join(sections_dir, component_dir)
                if os.path.isdir(comp_path):
                    section_files = [f for f in os.listdir(comp_path) if f.endswith('.md')]
                    section_count += len(section_files)
            total_files += section_count
            logger.info(f"📝 Section files: {section_count}")
        
        # Count architectural files
        arch_dir = os.path.join(INCREMENTAL_SAVE_DIR, "architecture")
        if os.path.exists(arch_dir):
            arch_files = [f for f in os.listdir(arch_dir) if f.endswith('.json')]
            total_files += len(arch_files)
            logger.info(f"🏗️ Architectural files: {len(arch_files)}")
        
        # Count LLM interaction files
        llm_dir = os.path.join(INCREMENTAL_SAVE_DIR, "llm_interactions")
        if os.path.exists(llm_dir):
            llm_count = 0
            for component_dir in os.listdir(llm_dir):
                comp_path = os.path.join(llm_dir, component_dir)
                if os.path.isdir(comp_path):
                    llm_files = [f for f in os.listdir(comp_path) if f.endswith('.json')]
                    llm_count += len(llm_files)
            total_files += llm_count
            logger.info(f"🤖 LLM interaction files: {llm_count}")
        
        logger.info(f"📊 TOTAL INTERIM FILES SAVED: {total_files}")
        logger.info(f"📁 All files saved in: {INCREMENTAL_SAVE_DIR}")
    else:
        logger.warning(f"⚠️ Incremental save directory not found: {INCREMENTAL_SAVE_DIR}")

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
        logger.info("🔄 Node: component_loader | Status: completed | No more components to process")
        print("--- 🔄 Component Loader: All components processed ---")
        return state
    
    component_name = state["unprocessed_components"].pop(0)
    remaining = len(state["unprocessed_components"])
    total_components = len(state["all_data"])
    current_idx = total_components - remaining
    
    # Enhanced logging with node status
    logger.info(f"🚀 Node: component_loader | Status: started | Component: '{component_name}'")
    logger.info(f"📥 Loading component: '{component_name}' ({remaining} remaining - {current_idx}/{total_components})")
    print(f"\n--- 📂 Component Loader: Loading component '{component_name}' ({current_idx}/{total_components}) ---")
    
    # Update progress bar with detailed information
    global progress_bar
    if progress_bar:
        # Set the current position correctly
        progress_bar.n = current_idx - 1
        remaining_count = total_components - current_idx
        percentage = (current_idx / total_components) * 100
        
        # Update description with file details
        progress_bar.set_description(f"🔄 {component_name} | {remaining_count} left")
        
        # Update by 1 and refresh
        progress_bar.update(1)
        progress_bar.refresh()
        
        # Log progress without emojis to avoid interference
        print(f"Progress: {current_idx}/{total_components} ({percentage:.1f}%) - Processing: {component_name}")
    
    state["current_component_name"] = component_name
    component_data = state["all_data"][component_name]
    state["current_component_doc"] = component_data["documentation"]
    
    # Log component details
    doc_length = len(state["current_component_doc"].split()) if state["current_component_doc"] else 0
    logger.info(f"📄 Component details | Name: '{component_name}' | Document length: {doc_length} words")
    print(f"    - Document length: {doc_length} words")
    print(f"    - Component type: {component_data.get('type', 'Unknown')}")
    
    # Set simple context without connected nodes
    state["current_component_context"] = f"Processing component: {component_name}"
    
    # Store empty connected nodes info
    state["connected_nodes"] = []
    
    # Save incremental progress
    save_incremental_progress(state, "component_loaded")
    
    logger.info(f"✅ Node: component_loader | Status: completed | Component: '{component_name}' loaded successfully")
    print(f"--- ✅ Component Loader: Component '{component_name}' loaded successfully ---")
    return state

def scrapper_node(state: DocumentationState) -> dict:
    """Enhanced scrapper that filters out trivial components more effectively."""
    component_name = state['current_component_name']
    component_doc = state['current_component_doc']
    
    logger.info(f"� Node: scrapper | Status: started | Component: '{component_name}'")
    logger.info(f"�🗑️ Enhanced Scrapper: Analyzing component '{component_name}'")
    print(f"--- 🗑️ Enhanced Scrapper: Analyzing '{component_name}' ---")
    
    # Pre-filter checks based on component name patterns
    trivial_patterns = [
        r'__init__\.py$',
        r'import[s]?_',
        r'_import[s]?',
        r'^[A-Z_]+$',  # Constants like API_V1_STR, APP_NAME
        r'\.py$'  # Simple module references
    ]
    
    # Check if component name matches trivial patterns
    for pattern in trivial_patterns:
        if re.search(pattern, component_name, re.IGNORECASE):
            logger.info(f"❌ Scrapper Decision: REJECT | Reason: matches trivial pattern '{pattern}' | Component: '{component_name}'")
            logger.info(f"❌ Pre-filter Decision: SCRAP (matches trivial pattern: {pattern})")
            print(f"--- 🗑️ Enhanced Scrapper: Decision is to REJECT (trivial pattern: {pattern}). ---")
            save_incremental_progress(state, "scrapper_scrap")
            return {"scrapper_decision": "scrap"}
    
    # Word count check
    doc_length = len(component_doc.split())
    logger.info(f"📊 Document analysis | Component: '{component_name}' | Length: {doc_length} words")
    print(f"    - Analyzing document length: {doc_length} words")
    
    if doc_length < 15:  # Increased threshold
        logger.info(f"❌ Scrapper Decision: REJECT | Reason: document too short ({doc_length} words) | Component: '{component_name}'")
        logger.info(f"❌ Decision: SCRAP (document too short: {doc_length} words)")
        print(f"--- 🗑️ Enhanced Scrapper: Decision is to REJECT (too short: {doc_length} words). ---")
        save_incremental_progress(state, "scrapper_scrap")
        return {"scrapper_decision": "scrap"}
    
    # Content-based filtering
    doc_lower = component_doc.lower()
    
    # Check for import-only content
    lines = [line.strip() for line in component_doc.split('\n') if line.strip()]
    non_trivial_lines = []
    
    logger.info(f"🔍 Content analysis | Component: '{component_name}' | Total lines: {len(lines)}")
    print(f"    - Analyzing content structure: {len(lines)} total lines")
    
    for line in lines:
        line_lower = line.lower()
        # Skip trivial lines
        if any(trivial in line_lower for trivial in [
            'import ', 'from ', '__init__', 'pass', '"""', "'''",
            'coding:', 'encoding:', '#', 'type: ignore'
        ]):
            continue
        # Skip simple assignments without logic
        if re.match(r'^\s*\w+\s*=\s*["\'\w\.\[\]]+\s*$', line):
            continue
        non_trivial_lines.append(line)
    
    logger.info(f"📝 Content structure | Component: '{component_name}' | Non-trivial lines: {len(non_trivial_lines)}")
    print(f"    - Non-trivial lines found: {len(non_trivial_lines)}")
    
    # If less than 3 non-trivial lines, it's probably not substantial
    if len(non_trivial_lines) < 3:
        logger.info(f"❌ Scrapper Decision: REJECT | Reason: insufficient non-trivial content ({len(non_trivial_lines)} lines) | Component: '{component_name}'")
        logger.info(f"❌ Decision: SCRAP (insufficient non-trivial content: {len(non_trivial_lines)} lines)")
        print(f"--- 🗑️ Enhanced Scrapper: Decision is to REJECT (insufficient content: {len(non_trivial_lines)} lines). ---")
        save_incremental_progress(state, "scrapper_scrap")
        return {"scrapper_decision": "scrap"}
    
    # Check for specific trivial content indicators
    trivial_indicators = [
        'this module contains only imports',
        'simple import statement',
        'constant definition',
        'variable declaration',
        'basic configuration',
        'empty module',
        'placeholder'
    ]
    
    trivial_found = [indicator for indicator in trivial_indicators if indicator in doc_lower]
    if trivial_found:
        logger.info(f"❌ Scrapper Decision: REJECT | Reason: contains trivial indicators {trivial_found} | Component: '{component_name}'")
        logger.info(f"❌ Decision: SCRAP (contains trivial indicators)")
        print(f"--- 🗑️ Enhanced Scrapper: Decision is to REJECT (trivial indicators: {trivial_found}). ---")
        save_incremental_progress(state, "scrapper_scrap")
        return {"scrapper_decision": "scrap"}
    
    # Check for substantial content indicators
    substantial_indicators = [
        'class ', 'def ', 'function', 'method', 'algorithm', 'logic',
        'implementation', 'process', 'handle', 'manage', 'calculate',
        'validate', 'parse', 'transform', 'route', 'endpoint',
        'service', 'controller', 'model', 'schema', 'exception',
        'error handling', 'business logic', 'data processing'
    ]
    
    substantial_count = sum(1 for indicator in substantial_indicators if indicator in doc_lower)
    substantial_found = [indicator for indicator in substantial_indicators if indicator in doc_lower]
    
    logger.info(f"✨ Substantial content analysis | Component: '{component_name}' | Indicators found: {substantial_count} | Types: {substantial_found[:5]}")
    print(f"    - Substantial content indicators: {substantial_count} found")
    
    # If it has multiple substantial indicators, likely proceed
    if substantial_count >= 2:
        logger.info(f"✅ Scrapper Decision: ACCEPT | Reason: substantial indicators ({substantial_count}) | Component: '{component_name}'")
        logger.info(f"✅ Pre-approval: PROCEED (substantial indicators: {substantial_count})")
        print(f"--- 🗑️ Enhanced Scrapper: Decision is to ACCEPT (substantial content: {substantial_count} indicators). ---")
        save_incremental_progress(state, "scrapper_proceed")
        return {"scrapper_decision": "proceed"}
    
    # For borderline cases, use LLM with enhanced prompt
    logger.info(f"🤖 Scrapper LLM consultation | Component: '{component_name}' | Reason: borderline case")
    logger.info(f"🤖 Borderline case - consulting enhanced LLM for '{component_name}'")
    print(f"    - Borderline case: consulting LLM for final decision")
    
    enhanced_prompt = ChatPromptTemplate.from_template(
        """You are an expert code analyst tasked with determining if a component's documentation is substantial enough to include in technical documentation.

Component Name: `{component_name}`
Documentation: 
---
{component_doc}
---

CRITERIA FOR SUBSTANTIAL CONTENT:
- Contains actual business logic, algorithms, or meaningful functionality
- Describes classes, functions, methods with implementation details
- Explains API endpoints, services, or data processing
- Documents configuration, schemas, or architectural components
- Provides error handling, validation, or complex operations

CRITERIA FOR TRIVIAL CONTENT (should be SCRAPPED):
- Only import statements or module references
- Simple variable/constant declarations
- Empty modules or placeholder files
- Basic __init__.py files without logic
- Single-line configurations or aliases
- Documentation that just lists imports or basic assignments

ANALYSIS FACTORS:
1. Code complexity and functionality depth
2. Business value and technical significance  
3. Documentation detail and implementation insights
4. Architectural or design relevance

Respond with exactly one word: "Proceed" if the content is substantial and valuable for technical documentation, or "Scrap" if it's trivial and not worth including.

Decision:"""
    )
    
    chain = enhanced_prompt | llm | StrOutputParser()
    
    try:
        logger.info(f"🤖 LLM call initiated | Component: '{component_name}' | Type: enhanced_scrapper")
        llm_decision = chain.invoke({
            "component_name": component_name, 
            "component_doc": component_doc
        })
        
        logger.info(f"🤖 LLM response received | Component: '{component_name}' | Decision: '{llm_decision.strip()}'")
        
        # Save LLM interaction for debugging
        save_llm_interaction(
            component_name, 
            "enhanced_scrapper",
            f"Component: {component_name}\nDoc: {component_doc[:500]}...",
            llm_decision,
            {"doc_length": len(component_doc), "substantial_count": substantial_count}
        )
        
        decision_clean = llm_decision.strip().lower()
        
        if "scrap" in decision_clean:
            logger.info(f"❌ Scrapper Decision: REJECT | Reason: LLM decision ('{llm_decision.strip()}') | Component: '{component_name}'")
            logger.info(f"❌ Enhanced LLM Decision: SCRAP for '{component_name}'")
            print(f"--- 🗑️ Enhanced Scrapper: Decision is to REJECT (LLM decision). ---")
            save_incremental_progress(state, "scrapper_scrap")
            return {"scrapper_decision": "scrap"}
        else:
            logger.info(f"✅ Scrapper Decision: ACCEPT | Reason: LLM decision ('{llm_decision.strip()}') | Component: '{component_name}'")
            logger.info(f"✅ Enhanced LLM Decision: PROCEED for '{component_name}'")
            print(f"--- 🗑️ Enhanced Scrapper: Decision is to ACCEPT (LLM decision). ---")
            save_incremental_progress(state, "scrapper_proceed")
            return {"scrapper_decision": "proceed"}
            
    except Exception as e:
        logger.error(f"❌ LLM error | Component: '{component_name}' | Error: {e}")
        logger.error(f"❌ LLM error for '{component_name}': {e}")
        # Default to proceed on error to avoid losing potentially valuable content
        logger.info(f"⚠️ Scrapper Decision: ACCEPT (default) | Reason: LLM error fallback | Component: '{component_name}'")
        logger.info(f"⚠️ Defaulting to PROCEED due to LLM error")
        print(f"--- 🗑️ Enhanced Scrapper: Defaulting to ACCEPT (LLM error). ---")
        save_incremental_progress(state, "scrapper_proceed")
        return {"scrapper_decision": "proceed"}

def selector_node(state: DocumentationState) -> DocumentationState:
    """Selects which documentation sections are relevant for the current component and its connections."""
    component_name = state['current_component_name']
    
    logger.info(f"🚀 Node: selector | Status: started | Component: '{component_name}'")
    logger.info(f"🎯 Selector: Choosing sections for '{component_name}'")
    print(f"--- 🎯 Selector: Choosing sections for '{component_name}' ---")
    
    # Include connected nodes information in the selection process
    connected_nodes_summary = ""
    if state.get("connected_nodes"):
        connected_nodes_summary = f"\n\nConnected Components:\n"
        for node in state["connected_nodes"]:
            connected_nodes_summary += f"- {node['name']} ({node['type']}): {node['summary']}\n"
        logger.info(f"🔗 Connected components | Component: '{component_name}' | Count: {len(state['connected_nodes'])}")
        print(f"    - Found {len(state['connected_nodes'])} connected components")
    else:
        logger.info(f"🔗 Connected components | Component: '{component_name}' | Count: 0")
        print(f"    - No connected components found")
    
    logger.info(f"🤖 LLM call initiated | Component: '{component_name}' | Type: section_selector")
    logger.info(f"🤖 Consulting LLM for section selection for '{component_name}'")
    print(f"    - Consulting LLM for section selection")
    
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
    
    try:
        response = chain.invoke({
            "component_name": component_name, 
            "component_doc": state["current_component_doc"], 
            "connected_nodes_summary": connected_nodes_summary,
            "sections": section_list_str
        })
        
        logger.info(f"🤖 LLM response received | Component: '{component_name}' | Sections selected: {len(response.get('relevant_sections', []))}")
        
        # Save LLM interaction for section selection
        save_llm_interaction(
            component_name,
            "section_selector",
            f"Component: {component_name}\nSections: {section_list_str[:300]}...",
            str(response),
            {"available_sections": len(ALL_SECTIONS), "connected_nodes": len(state.get("connected_nodes", []))}
        )
        
        relevant_sections = response.get("relevant_sections", [])
        state["target_sections"] = [s for s in relevant_sections if s in ALL_SECTIONS]
        
        logger.info(f"✅ Section selection | Component: '{component_name}' | Selected: {len(state['target_sections'])} sections")
        logger.info(f"📋 Selected sections | Component: '{component_name}' | Sections: {state['target_sections']}")
        logger.info(f"✅ Selected {len(state['target_sections'])} sections for '{component_name}': {state['target_sections']}")
        print(f"--- 🎯 Selector: Chosen sections ({len(state['target_sections'])}): {state['target_sections']} ---")
        
        # Log each section selection decision
        for section in state['target_sections']:
            print(f"    - Selected: {section}")
        
    except Exception as e:
        logger.error(f"❌ Section selection failed | Component: '{component_name}' | Error: {e}")
        # Fallback to default sections
        state["target_sections"] = ["Project Introduction", "Code Documentation"]
        logger.info(f"⚠️ Fallback selection | Component: '{component_name}' | Using default sections: {state['target_sections']}")
        print(f"    - Using fallback sections due to error: {state['target_sections']}")
    
    # Save incremental progress
    save_incremental_progress(state, "sections_selected")
    
    logger.info(f"✅ Node: selector | Status: completed | Component: '{component_name}' | Sections: {len(state['target_sections'])}")
    
    return state

async def architectural_diagram_node(state: DocumentationState) -> DocumentationState:
    """Analyzes components and updates the architectural diagram in parallel with documentation writers."""
    component_name = state['current_component_name']
    component_doc = state['current_component_doc']
    
    logger.info(f"🚀 Node: architectural_diagram | Status: started | Component: '{component_name}'")
    logger.info(f"🏗️ Architectural Analyzer: Processing '{component_name}'")
    print(f"--- 🏗️ Architectural Analyzer: Analyzing '{component_name}' ---")
    
    # Initialize architectural data if not present
    if not state.get("architectural_components"):
        state["architectural_components"] = {}
        logger.info("🏗️ Initialized architectural components storage")
    if not state.get("architectural_relationships"):
        state["architectural_relationships"] = []
        logger.info("🏗️ Initialized architectural relationships storage")
    if not state.get("diagram_mermaid_code"):
        state["diagram_mermaid_code"] = "graph TD\n"
        logger.info("🏗️ Initialized mermaid diagram code")
    if not state.get("diagram_description"):
        state["diagram_description"] = "## System Architecture Overview\n\nThis diagram represents the architectural components and their relationships:\n\n"
        logger.info("🏗️ Initialized diagram description")
    
    # Log current architectural state
    existing_components = len(state["architectural_components"])
    existing_relationships = len(state["architectural_relationships"])
    logger.info(f"📊 Current architectural state | Components: {existing_components} | Relationships: {existing_relationships}")
    print(f"    - Current state: {existing_components} components, {existing_relationships} relationships")
    
    # Create architectural analysis prompt
    architectural_prompt = ChatPromptTemplate.from_template(
        """You are a software architect analyzing components for architectural diagram generation.

Component Name: `{component_name}`
Component Documentation:
---
{component_doc}
---

Existing Architectural Components: {existing_components}
Existing Relationships: {existing_relationships}

TASK: Analyze this component and extract architectural information.

EXTRACT THE FOLLOWING:
1. Component Type: (e.g., "API_ENDPOINT", "SERVICE", "DATABASE", "CONTROLLER", "MODEL", "UTILITY", "CONFIG", "MIDDLEWARE")
2. Component Layer: (e.g., "PRESENTATION", "BUSINESS", "DATA", "INFRASTRUCTURE", "EXTERNAL")
3. Key Responsibilities: Brief description of what this component does
4. Dependencies: What other components this one depends on
5. Dependents: What components depend on this one
6. Data Flow: How data flows through this component

Respond with a JSON object containing:
{{
    "component_info": {{
        "name": "{component_name}",
        "type": "COMPONENT_TYPE",
        "layer": "LAYER_NAME", 
        "responsibilities": "Brief description",
        "has_substantial_logic": true/false
    }},
    "relationships": [
        {{
            "from": "source_component",
            "to": "target_component", 
            "type": "DEPENDS_ON|CALLS|INHERITS|IMPLEMENTS|CONFIGURES",
            "description": "Brief description of relationship"
        }}
    ],
    "mermaid_update": "Any new mermaid diagram lines to add for this component"
}}

Focus on architectural significance. Only include substantial components and meaningful relationships."""
    )
    
    chain = architectural_prompt | llm | JsonOutputParser()
    
    try:
        logger.info(f"🤖 LLM call initiated | Component: '{component_name}' | Type: architectural_analyzer")
        
        # Get architectural analysis
        analysis = await chain.ainvoke({
            "component_name": component_name,
            "component_doc": component_doc,
            "existing_components": list(state["architectural_components"].keys()),
            "existing_relationships": [f"{r['from']} -> {r['to']}" for r in state["architectural_relationships"]]
        })
        
        logger.info(f"🤖 LLM response received | Component: '{component_name}' | Analysis completed")
        
        # Save LLM interaction for architectural analysis
        save_llm_interaction(
            component_name,
            "architectural_analyzer",
            f"Component: {component_name}\nDoc: {component_doc[:500]}...",
            str(analysis),
            {
                "existing_components_count": len(state["architectural_components"]),
                "existing_relationships_count": len(state["architectural_relationships"])
            }
        )
        
        # Update architectural components
        if analysis.get("component_info") and analysis["component_info"].get("has_substantial_logic"):
            component_info = analysis["component_info"]
            state["architectural_components"][component_name] = component_info
            comp_type = component_info.get('type', 'UNKNOWN')
            comp_layer = component_info.get('layer', 'UNKNOWN')
            logger.info(f"✅ Architectural component added | Component: '{component_name}' | Type: {comp_type} | Layer: {comp_layer}")
            logger.info(f"📊 Added architectural component: {component_name} ({comp_type})")
            print(f"    - Added component: {component_name} ({comp_type})")
        else:
            logger.info(f"⚠️ Component not substantial enough for architecture | Component: '{component_name}'")
            print(f"    - Component not added (insufficient architectural significance)")
        
        # Update relationships
        new_relationships = 0
        if analysis.get("relationships"):
            for relationship in analysis["relationships"]:
                # Avoid duplicate relationships
                relationship_key = f"{relationship['from']}-{relationship['to']}-{relationship['type']}"
                existing_keys = [f"{r['from']}-{r['to']}-{r['type']}" for r in state["architectural_relationships"]]
                if relationship_key not in existing_keys:
                    state["architectural_relationships"].append(relationship)
                    new_relationships += 1
                    logger.info(f"🔗 Relationship added | From: '{relationship['from']}' | To: '{relationship['to']}' | Type: {relationship['type']}")
                    logger.info(f"🔗 Added relationship: {relationship['from']} -> {relationship['to']}")
                    print(f"    - Added relationship: {relationship['from']} -> {relationship['to']}")
        
        if new_relationships == 0:
            logger.info(f"🔗 No new relationships found | Component: '{component_name}'")
            print(f"    - No new relationships identified")
        
        # Update mermaid diagram
        if analysis.get("mermaid_update"):
            state["diagram_mermaid_code"] += f"    {analysis['mermaid_update']}\n"
            logger.info(f"🎨 Mermaid diagram updated | Component: '{component_name}'")
            print(f"    - Updated mermaid diagram")
        
        # Save architectural progress
        save_architectural_progress(state, component_name)
        
        final_components = len(state["architectural_components"])
        final_relationships = len(state["architectural_relationships"])
        logger.info(f"📊 Architectural analysis completed | Component: '{component_name}' | Total components: {final_components} | Total relationships: {final_relationships}")
        logger.info(f"✅ Architectural analysis completed for '{component_name}'")
        print(f"--- 🏗️ Architectural Analyzer: Analysis completed (Total: {final_components} components, {final_relationships} relationships) ---")
        
    except Exception as e:
        logger.error(f"❌ Architectural analysis failed | Component: '{component_name}' | Error: {e}")
        logger.error(f"❌ Architectural analysis failed for '{component_name}': {e}")
        print(f"--- 🏗️ Architectural Analyzer: Analysis failed: {e} ---")
    
    logger.info(f"✅ Node: architectural_diagram | Status: completed | Component: '{component_name}'")
    
    return state

def save_architectural_progress(state: DocumentationState, component_name: str):
    """Save architectural diagram progress incrementally."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_component = sanitize_filename(str(component_name))
    
    # Create architecture-specific directory
    arch_dir = os.path.join(INCREMENTAL_SAVE_DIR, "architecture")
    os.makedirs(arch_dir, exist_ok=True)
    
    # Save current architectural state
    arch_state = {
        "timestamp": timestamp,
        "component": component_name,
        "components_count": len(state.get("architectural_components", {})),
        "relationships_count": len(state.get("architectural_relationships", [])),
        "architectural_components": state.get("architectural_components", {}),
        "architectural_relationships": state.get("architectural_relationships", []),
        "diagram_mermaid_code": state.get("diagram_mermaid_code", ""),
        "diagram_description": state.get("diagram_description", "")
    }
    
    filename = f"{timestamp}_arch_progress_{safe_component}.json"
    filepath = os.path.join(arch_dir, filename)
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(arch_state, f, indent=2, ensure_ascii=False)
        logger.info(f"🏗️ Architectural progress saved: {filepath}")
    except Exception as e:
        logger.error(f"❌ Failed to save architectural progress: {e}")

# Updated parallel processing to include architectural analysis
async def parallel_processing_node(state: DocumentationState) -> DocumentationState:
    """Runs both documentation writers and architectural analyzer in parallel."""
    component_name = state['current_component_name']
    total_sections = len(state["target_sections"])
    
    logger.info(f"🚀 Node: parallel_processing | Status: started | Component: '{component_name}' | Tasks: {total_sections + 1}")
    logger.info(f"🚀 Parallel Processing: Starting writers + architecture for '{component_name}'")
    print(f"--- 🚀 Parallel Processing: Starting {total_sections} writers + architecture ---")
    
    # Log what sections will be processed
    logger.info(f"📋 Processing sections | Component: '{component_name}' | Sections: {state['target_sections']}")
    for i, section in enumerate(state["target_sections"], 1):
        print(f"    - Task {i}: Documentation for '{section}'")
    print(f"    - Task {total_sections + 1}: Architectural analysis")
    
    # Create tasks for both documentation and architecture
    tasks = []
    
    # Add documentation writer tasks
    for section_name in state["target_sections"]:
        tasks.append(process_documentation_section(state, section_name))
    
    # Add architectural analysis task
    tasks.append(process_architectural_analysis(state))
    
    try:
        # Execute all tasks concurrently
        logger.info(f"🔄 Executing parallel tasks | Component: '{component_name}' | Total tasks: {len(tasks)} ({total_sections} docs + 1 architecture)")
        logger.info(f"🔄 Executing {len(tasks)} parallel tasks ({total_sections} docs + 1 architecture)")
        print(f"    - Executing {len(tasks)} tasks concurrently...")
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process documentation results
        successful_sections = 0
        failed_sections = 0
        
        for i, result in enumerate(results[:-1]):  # All except the last (architecture) result
            section_name = state["target_sections"][i]
            if isinstance(result, Exception):
                logger.error(f"❌ Documentation task failed | Component: '{component_name}' | Section: '{section_name}' | Error: {result}")
                logger.error(f"❌ Documentation writer exception: {result}")
                print(f"    - ❌ Failed: '{section_name}' - {result}")
                failed_sections += 1
            else:
                section_name, content = result
                state["document_content"][section_name] = content
                logger.info(f"✅ Documentation task completed | Component: '{component_name}' | Section: '{section_name}' | Length: {len(content)} chars")
                print(f"    - ✅ Completed: '{section_name}' ({len(content)} chars)")
                successful_sections += 1
        
        # Process architectural result
        arch_result = results[-1]
        if isinstance(arch_result, Exception):
            logger.error(f"❌ Architectural task failed | Component: '{component_name}' | Error: {arch_result}")
            logger.error(f"❌ Architectural analysis exception: {arch_result}")
            print(f"    - ❌ Architecture analysis failed: {arch_result}")
        else:
            # Architectural analysis updates state in-place
            logger.info(f"✅ Architectural task completed | Component: '{component_name}'")
            logger.info(f"✅ Architectural analysis completed successfully")
            print(f"    - ✅ Architecture analysis completed")
        
        logger.info(f"📊 Parallel processing summary | Component: '{component_name}' | Successful docs: {successful_sections} | Failed docs: {failed_sections}")
        logger.info(f"📊 Parallel processing completed: {successful_sections} docs successful, {failed_sections} docs failed")
        print(f"--- 📊 Summary: {successful_sections} successful, {failed_sections} failed ---")
        
    except Exception as exc:
        logger.error(f"❌ Parallel processing failed | Component: '{component_name}' | Error: {exc}")
        logger.error(f"❌ Parallel processing failed: {exc}")
        print(f"--- ❌ Parallel processing failed: {exc} ---")
    
    # Save incremental progress
    save_incremental_progress(state, "parallel_processing_completed")
    
    logger.info(f"✅ Node: parallel_processing | Status: completed | Component: '{component_name}'")
    
    return state

async def process_documentation_section(state: DocumentationState, section_name: str) -> tuple[str, str]:
    """Process a single documentation section."""
    component_name = state['current_component_name']
    
    logger.info(f"📝 Processing documentation section | Component: '{component_name}' | Section: '{section_name}'")
    
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
        Respond with the complete, updated markdown for the \"{section_name}\" section. Do NOT wrap the entire output in triple backticks or code blocks. Only use code blocks for actual code, not for the whole section."""
    )
    
    existing_content = state["document_content"].get(section_name, "")
    existing_length = len(existing_content or "")
    
    logger.info(f"📄 Section context | Component: '{component_name}' | Section: '{section_name}' | Existing content: {existing_length} chars")
    
    prompt = ChatPromptTemplate.from_template(writer_prompt_template)
    chain = prompt | llm | StrOutputParser()
    
    try:
        logger.info(f"🤖 LLM call initiated | Component: '{component_name}' | Section: '{section_name}' | Type: documentation_writer")
        
        updated_section_content = await chain.ainvoke({
            "section_name": section_name,
            "existing_content": existing_content or "This section is empty. Please start it.",
            "component_name": component_name,
            "component_doc": state["current_component_doc"],
            "component_context": state["current_component_context"]
        })
        
        new_length = len(updated_section_content)
        
        logger.info(f"🤖 LLM response received | Component: '{component_name}' | Section: '{section_name}' | New content: {new_length} chars")
        logger.info(f"✅ Section processing completed | Component: '{component_name}' | Section: '{section_name}' | Content generated: {new_length} chars")
        
        # Save LLM interaction for documentation section
        save_llm_interaction(
            component_name,
            f"doc_writer_{section_name.replace(' ', '_')}",
            f"Section: {section_name}\nComponent: {component_name}\nDoc: {state['current_component_doc'][:500]}...",
            updated_section_content,
            {
                "section_name": section_name,
                "existing_content_length": existing_length,
                "new_content_length": new_length
            }
        )
        
        # Save section content
        save_section_content(component_name, section_name, updated_section_content)
        return section_name, updated_section_content
        
    except Exception as e:
        logger.error(f"❌ Section processing failed | Component: '{component_name}' | Section: '{section_name}' | Error: {e}")
        logger.error(f"❌ Error processing section '{section_name}': {e}")
        error_content = f"Error generating content for {section_name}: {str(e)}"
        return section_name, error_content

async def process_architectural_analysis(state: DocumentationState) -> DocumentationState:
    """Process architectural analysis for the current component."""
    return await architectural_diagram_node(state)

def parallel_processing_node_sync(state: DocumentationState) -> DocumentationState:
    """Synchronous wrapper for parallel processing."""
    return asyncio.run(parallel_processing_node(state))

# Updated parallel_writer_node with integrated progress tracking
async def parallel_writer_node(state: DocumentationState) -> DocumentationState:
    """Invokes the specialist writer agents in parallel for the selected sections using async/await."""
    component_name = state['current_component_name']
    total_sections = len(state["target_sections"])
    logger.info(f"✍️ Parallel Writers: Starting for '{component_name}' with {total_sections} sections")
    print(f"--- ✍️ Parallel Writers: Starting for '{component_name}' ---")
    
    # Global progress tracking
    completed_sections = 0
    
    async def process_section(section_name: str) -> tuple[str, str]:
        """Process a single section asynchronously and return (section_name, content)."""
        nonlocal completed_sections
        completed_sections += 1
        
        logger.info(f"🔄 Processing section: '{section_name}' for component '{component_name}' ({completed_sections}/{total_sections})")
        print(f"    - Invoking writer for section: '{section_name}' ({completed_sections}/{total_sections})")
        
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
            Respond with the complete, updated markdown for the \"{section_name}\" section. Do NOT wrap the entire output in triple backticks or code blocks. Only use code blocks for actual code, not for the whole section."""
        )
        
        existing_content = state["document_content"].get(section_name, "")
        prompt = ChatPromptTemplate.from_template(writer_prompt_template)
        chain = prompt | llm | StrOutputParser()
        
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
            
            logger.info(f"✅ Section '{section_name}' completed for component '{component_name}' ({completed_sections}/{total_sections})")
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

# Remove the duplicate patching code and use the consolidated version
def parallel_writer_node_sync(state: DocumentationState) -> DocumentationState:
    """Synchronous wrapper for the async parallel_writer_node function."""
    return asyncio.run(parallel_writer_node(state))

def compiler_node(state: DocumentationState) -> DocumentationState:
    """Assembles all the final sections into the complete, hierarchical document."""
    logger.info("� Node: compiler | Status: started")
    logger.info("�📚 Compiler: Starting document assembly")
    print("--- 📚 Compiler: Assembling Final Document ---")

    def strip_triple_backticks(text: str) -> str:
        # Remove wrapping triple backticks (with or without language) from the whole section
        pattern = r"^```[a-zA-Z]*\n([\s\S]*?)\n```$"
        return re.sub(pattern, r"\1", text.strip(), flags=re.MULTILINE)

    final_doc_parts = []
    sections_included = 0
    total_sections_available = sum(len(subsections) for subsections in HIERARCHICAL_STRUCTURE.values())
    sections_with_content = 0

    # First pass: count sections with content
    for main_section, subsections in HIERARCHICAL_STRUCTURE.items():
        for subsection_name in subsections:
            content = state["document_content"].get(subsection_name, "").strip()
            if content:
                sections_with_content += 1

    logger.info(f"📊 Document assembly analysis | Total available sections: {total_sections_available} | Sections with content: {sections_with_content}")
    print(f"    - Sections available: {total_sections_available}")
    print(f"    - Sections with content: {sections_with_content}")

    for main_section, subsections in HIERARCHICAL_STRUCTURE.items():
        # Check if any subsection within this main section has content
        section_has_content = any(state["document_content"].get(sub, "").strip() for sub in subsections)

        # Only add the main section header if it has content
        if section_has_content:
            final_doc_parts.append(f"# {main_section}")
            logger.info(f"📝 Adding main section: {main_section}")
            print(f"    - Adding main section: {main_section}")

            for subsection_name in subsections:
                content = state["document_content"].get(subsection_name, "").strip()
                if content:
                    # Remove wrapping triple backticks if present
                    cleaned_content = strip_triple_backticks(content)
                    content_length = len(cleaned_content)
                    final_doc_parts.append(f"## {subsection_name}\n\n{cleaned_content}")
                    sections_included += 1
                    logger.info(f"📄 Added subsection: {subsection_name} | Length: {content_length} chars")
                    logger.info(f"📄 Added subsection: {subsection_name}")
                    print(f"      - Added: {subsection_name} ({content_length} chars)")
                else:
                    logger.info(f"⚠️ Skipped subsection (empty): {subsection_name}")
        else:
            logger.info(f"⚠️ Skipped main section (no content): {main_section}")
            print(f"    - Skipped main section: {main_section} (no content)")

    state["final_document"] = "\n\n---\n\n".join(final_doc_parts)
    final_doc_length = len(state["final_document"])

    logger.info(f"📊 Document assembly completed | Sections included: {sections_included}/{sections_with_content} | Total length: {final_doc_length} chars")
    logger.info(f"✅ Compiler: Document assembled with {sections_included} sections")
    print("--- 🎉 Compiler: Final document assembled! ---")
    print(f"    - Final document: {sections_included} sections, {final_doc_length} characters")

    # Save final document progress
    save_incremental_progress(state, "final_document_compiled")

    logger.info("✅ Node: compiler | Status: completed")

    return state

def diagram_finalizer_node(state: DocumentationState) -> DocumentationState:
    """Finalizes the architectural diagram and generates the final version."""
    logger.info("🎨 Diagram Finalizer: Creating final architectural diagram")
    print("--- 🎨 Diagram Finalizer: Generating final diagram ---")
    
    try:
        # Generate comprehensive mermaid diagram
        final_mermaid = generate_final_mermaid_diagram(state)
        
        # Generate description
        final_description = generate_architectural_description(state)
        
        # Save basic diagram files
        save_basic_diagram_files(state, final_mermaid, final_description)
        
        # Create beautification script
        create_beautification_script(state)
        
        logger.info("✅ Diagram Finalizer: Basic diagram generated successfully")
        print("--- 🎨 Diagram Finalizer: Basic diagram completed ---")
        
    except Exception as e:
        logger.error(f"❌ Diagram Finalizer failed: {e}")
        print(f"--- 🎨 Diagram Finalizer: Failed - {e} ---")
    
    return state

def generate_final_mermaid_diagram(state: DocumentationState) -> str:
    """Generate a comprehensive mermaid diagram from collected architectural data."""
    components = state.get("architectural_components", {})
    relationships = state.get("architectural_relationships", [])
    
    if not components:
        return "graph TD\n    A[No Components Found]"
    
    # Group components by layer
    layers = {}
    for comp_name, comp_info in components.items():
        layer = comp_info.get("layer", "UNKNOWN")
        if layer not in layers:
            layers[layer] = []
        layers[layer].append((comp_name, comp_info))
    
    # Build mermaid diagram
    mermaid_lines = ["graph TD"]
    
    # Add subgraphs for each layer
    for layer_name, layer_components in layers.items():
        mermaid_lines.append(f"    subgraph {layer_name}_LAYER[\"{layer_name} Layer\"]")
        
        for comp_name, comp_info in layer_components:
            comp_type = comp_info.get("type", "COMPONENT")
            safe_name = sanitize_mermaid_id(comp_name)
            
            # Choose shape based on component type
            if comp_type in ["API_ENDPOINT", "CONTROLLER"]:
                shape = f"{safe_name}([{comp_name}])"
            elif comp_type in ["DATABASE", "DATA"]:
                shape = f"{safe_name}[(Database: {comp_name})]"
            elif comp_type in ["SERVICE", "BUSINESS"]:
                shape = f"{safe_name}[{comp_name}]"
            else:
                shape = f"{safe_name}{{{comp_name}}}"
            
            mermaid_lines.append(f"        {shape}")
        
        mermaid_lines.append("    end")
    
    # Add relationships
    for rel in relationships:
        from_safe = sanitize_mermaid_id(rel["from"])
        to_safe = sanitize_mermaid_id(rel["to"])
        rel_type = rel.get("type", "DEPENDS_ON")
        
        # Choose arrow style based on relationship type
        if rel_type == "CALLS":
            arrow = "-->"
        elif rel_type == "INHERITS":
            arrow = "-..->"
        elif rel_type == "IMPLEMENTS":
            arrow = "==>"
        else:
            arrow = "-->"
        
        mermaid_lines.append(f"    {from_safe} {arrow} {to_safe}")
    
    return "\n".join(mermaid_lines)

def sanitize_mermaid_id(name: str) -> str:
    """Sanitize component names for mermaid diagram IDs."""
    return re.sub(r'[^a-zA-Z0-9_]', '_', name)

def generate_architectural_description(state: DocumentationState) -> str:
    """Generate a natural language description of the architecture."""
    components = state.get("architectural_components", {})
    relationships = state.get("architectural_relationships", [])
    
    if not components:
        return "No architectural components were identified in the codebase."
    
    description = ["# System Architecture Overview\n"]
    description.append(f"The system consists of **{len(components)}** main components with **{len(relationships)}** identified relationships.\n")
    
    # Group by layers
    layers = {}
    for comp_name, comp_info in components.items():
        layer = comp_info.get("layer", "UNKNOWN")
        if layer not in layers:
            layers[layer] = []
        layers[layer].append((comp_name, comp_info))
    
    # Describe each layer
    for layer_name, layer_components in layers.items():
        description.append(f"## {layer_name} Layer\n")
        
        for comp_name, comp_info in layer_components:
            comp_type = comp_info.get("type", "COMPONENT")
            responsibilities = comp_info.get("responsibilities", "No description available")
            description.append(f"### {comp_name} ({comp_type})\n")
            description.append(f"{responsibilities}\n")
    
    # Describe relationships
    if relationships:
        description.append("## Component Relationships\n")
        for rel in relationships:
            description.append(f"- **{rel['from']}** {rel['type'].lower().replace('_', ' ')} **{rel['to']}**: {rel.get('description', 'No description')}")
    
    return "\n".join(description)

def save_basic_diagram_files(state: DocumentationState, mermaid_code: str, description: str):
    """Save basic diagram files before beautification."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create diagrams directory
    diagrams_dir = os.path.join(FINAL_DOC_DIR, "diagrams")
    os.makedirs(diagrams_dir, exist_ok=True)
    
    # Save mermaid diagram
    mermaid_file = os.path.join(diagrams_dir, f"architecture_diagram_{timestamp}.mmd")
    with open(mermaid_file, 'w', encoding='utf-8') as f:
        f.write(mermaid_code)
    
    # Save architectural description
    desc_file = os.path.join(diagrams_dir, f"architecture_description_{timestamp}.md")
    with open(desc_file, 'w', encoding='utf-8') as f:
        f.write(description)
    
    # Save architectural data as JSON
    arch_data_file = os.path.join(diagrams_dir, f"architecture_data_{timestamp}.json")
    arch_data = {
        "timestamp": timestamp,
        "components": state.get("architectural_components", {}),
        "relationships": state.get("architectural_relationships", []),
        "mermaid_code": mermaid_code,
        "description": description
    }
    
    with open(arch_data_file, 'w', encoding='utf-8') as f:
        json.dump(arch_data, f, indent=2, ensure_ascii=False)
    
    logger.info(f"💾 Basic diagram files saved in: {diagrams_dir}")

def create_beautification_script(state: DocumentationState):
    """Create a script to beautify the architectural diagram."""
    script_content = '''
import json
import os
import subprocess
import sys
from datetime import datetime

def beautify_architecture_diagram():
    """Beautify the architectural diagram using mermaid-cli and additional processing."""
    print("🎨 Starting diagram beautification process...")
    
    # Find the latest architecture data file
    diagrams_dir = "final_docs/diagrams"
    if not os.path.exists(diagrams_dir):
        print("❌ Diagrams directory not found!")
        return
    
    # Get the most recent architecture data file
    arch_files = [f for f in os.listdir(diagrams_dir) if f.startswith("architecture_data_")]
    if not arch_files:
        print("❌ No architecture data files found!")
        return
    
    latest_file = max(arch_files, key=lambda x: os.path.getctime(os.path.join(diagrams_dir, x)))
    arch_data_path = os.path.join(diagrams_dir, latest_file)
    
    print(f"📊 Processing: {arch_data_path}")
    
    # Load architectural data
    with open(arch_data_path, 'r', encoding='utf-8') as f:
        arch_data = json.load(f)
    
    # Create enhanced mermaid diagram
    enhanced_mermaid = create_enhanced_mermaid_diagram(arch_data)
    
    # Save enhanced diagram
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    enhanced_file = os.path.join(diagrams_dir, f"enhanced_architecture_{timestamp}.mmd")
    
    with open(enhanced_file, 'w', encoding='utf-8') as f:
        f.write(enhanced_mermaid)
    
    print(f"✅ Enhanced mermaid diagram saved: {enhanced_file}")
    
    # Try to generate PNG using mermaid-cli if available
    try:
        png_file = enhanced_file.replace('.mmd', '.png')
        subprocess.run([
            'mmdc', '-i', enhanced_file, '-o', png_file,
            '--theme', 'default', '--backgroundColor', 'white',
            '--width', '1200', '--height', '800'
        ], check=True)
        print(f"🖼️ PNG diagram generated: {png_file}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️ mermaid-cli not found. Install with: npm install -g @mermaid-js/mermaid-cli")
        print("📝 Enhanced mermaid file created. You can manually convert it to PNG.")
    
    # Create HTML preview
    create_html_preview(enhanced_mermaid, diagrams_dir, timestamp)
    
    print("🎉 Diagram beautification completed!")

def create_enhanced_mermaid_diagram(arch_data):
    """Create an enhanced version of the mermaid diagram with better styling."""
    components = arch_data.get('components', {})
    relationships = arch_data.get('relationships', [])
    
    # Enhanced mermaid with styling
    lines = [
        "graph TB",
        "    %% Enhanced Architecture Diagram",
        "    %% Generated automatically from code analysis",
        ""
    ]
    
    # Define colors for different component types
    style_definitions = [
        "    classDef apiClass fill:#e1f5fe,stroke:#01579b,stroke-width:2px",
        "    classDef serviceClass fill:#f3e5f5,stroke:#4a148c,stroke-width:2px", 
        "    classDef dataClass fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px",
        "    classDef configClass fill:#fff3e0,stroke:#e65100,stroke-width:2px",
        "    classDef utilClass fill:#fafafa,stroke:#424242,stroke-width:2px",
        ""
    ]
    
    # Group components by layer for better organization
    layers = {}
    for comp_name, comp_info in components.items():
        layer = comp_info.get("layer", "UNKNOWN")
        if layer not in layers:
            layers[layer] = []
        layers[layer].append((comp_name, comp_info))
    
    # Add subgraphs for each layer
    for layer_name, layer_components in layers.items():
        lines.append(f'    subgraph {layer_name}["{layer_name} Layer"]')
        
        for comp_name, comp_info in layer_components:
            comp_type = comp_info.get("type", "COMPONENT")
            safe_name = comp_name.replace('.', '_').replace('-', '_')
            safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', safe_name)
            
            # Enhanced shapes based on component type
            if comp_type in ["API_ENDPOINT", "CONTROLLER"]:
                shape = f'{safe_name}(["{comp_name}<br/>{comp_type}"])'
                style_class = "apiClass"
            elif comp_type in ["DATABASE", "DATA"]:
                shape = f'{safe_name}[("{comp_name}<br/>{comp_type}")]'
                style_class = "dataClass"
            elif comp_type in ["SERVICE", "BUSINESS"]:
                shape = f'{safe_name}["{comp_name}<br/>{comp_type}"]'
                style_class = "serviceClass"
            elif comp_type in ["CONFIG", "CONFIGURATION"]:
                shape = f'{safe_name}{{{"{comp_name}<br/>{comp_type}"}}}' 
                style_class = "configClass"
            else:
                shape = f'{safe_name}("{comp_name}<br/>{comp_type}")'
                style_class = "utilClass"
            
            lines.append(f"        {shape}")
            lines.append(f"        class {safe_name} {style_class}")
        
        lines.append("    end")
        lines.append("")
    
    # Add relationships with enhanced styling
    for rel in relationships:
        from_safe = re.sub(r'[^a-zA-Z0-9_]', '_', rel["from"])
        to_safe = re.sub(r'[^a-zA-Z0-9_]', '_', rel["to"])
        rel_type = rel.get("type", "DEPENDS_ON")
        description = rel.get("description", "")
        
        # Choose arrow style and label based on relationship type
        if rel_type == "CALLS":
            arrow = f'-->{"|calls|"}'
        elif rel_type == "INHERITS":
            arrow = f'-..->{"|extends|"}'
        elif rel_type == "IMPLEMENTS":
            arrow = f'==>{"|implements|"}'
        elif rel_type == "CONFIGURES":
            arrow = f'-->{"|configures|"}'
        else:
            arrow = f'-->{"|depends on|"}'
        
        lines.append(f"    {from_safe} {arrow} {to_safe}")
    
    # Add style definitions
    lines.extend(style_definitions)
    
    return "\\n".join(lines)

def create_html_preview(mermaid_code, diagrams_dir, timestamp):
    """Create an HTML preview of the diagram."""
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Architecture Diagram Preview</title>
    <script src="https://unpkg.com/mermaid/dist/mermaid.min.js"></script>
    <style>
        body {{ 
            font-family: Arial, sans-serif; 
            margin: 20px; 
            background-color: #f5f5f5;
        }}
        .container {{ 
            background: white; 
            padding: 20px; 
            border-radius: 8px; 
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{ color: #333; }}
        .diagram {{ 
            text-align: center; 
            margin: 20px 0;
            background: white;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 20px;
        }}
        .info {{
            background: #e8f4fd;
            border-left: 4px solid #2196f3;
            padding: 10px;
            margin: 10px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>System Architecture Diagram</h1>
        <div class="info">
            <strong>Generated:</strong> {timestamp}<br>
            <strong>Components:</strong> {len(arch_data.get('components', {}))}<br>
            <strong>Relationships:</strong> {len(arch_data.get('relationships', []))}
        </div>
        <div class="diagram">
            <div class="mermaid">
{mermaid_code}
            </div>
        </div>
    </div>
    <script>
        mermaid.initialize({{ startOnLoad: true, theme: 'default' }});
    </script>
</body>
</html>
"""
    
    html_file = os.path.join(diagrams_dir, f"architecture_preview_{timestamp}.html")
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"🌐 HTML preview created: {html_file}")

if __name__ == "__main__":
    beautify_architecture_diagram()
'''
    
    # Save the beautification script
    script_file = os.path.join(FINAL_DOC_DIR, "beautify_diagram.py")
    with open(script_file, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    logger.info(f"🎨 Beautification script created: {script_file}")
    print(f"--- 🎨 Beautification script saved: {script_file} ---")

# --- 5. Define Graph Edges & Control Flow ---

def should_continue_processing(state: DocumentationState) -> str:
    """Determines if there are more components to process."""
    return "continue" if state["unprocessed_components"] else "end"

# --- 6. Build and Run the Graph ---

workflow = StateGraph(DocumentationState)
workflow.add_node("loader", component_loader_node)
workflow.add_node("scrapper", scrapper_node)
workflow.add_node("selector", selector_node)
workflow.add_node("parallel_processing", parallel_processing_node_sync)
workflow.add_node("compiler", compiler_node)
workflow.add_node("diagram_finalizer", diagram_finalizer_node)

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
workflow.add_edge("compiler", "diagram_finalizer")
workflow.add_edge("diagram_finalizer", END)

app = workflow.compile()

# --- Main execution block ---
if __name__ == "__main__":
    start_time = datetime.now()
    progress_bar = None

    JSON_FILE = "output/CalculatorCode/documentation_and_graph_data.json"
    GRAPH_FILE = "output/CalculatorCode/conceptual_graph.pkl"
    FINAL_DOC_DIR = "final_docs"
    os.makedirs(FINAL_DOC_DIR, exist_ok=True)
    OUTPUT_FILE_BASE = "Complete_Technical_Documentation.md"
    OUTPUT_FILE = os.path.join(FINAL_DOC_DIR, OUTPUT_FILE_BASE)

    logger.info("🚀 DOCUMENTATION GENERATION STARTED")
    logger.info(f"⏰ Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("🚀 AI DOCUMENTATION GENERATOR")
    print("=" * 80)
    print(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

    logger.info("📁 File validation:")
    logger.info(f"📁 JSON file: {JSON_FILE}")
    logger.info(f"📁 Graph file: {GRAPH_FILE}")
    logger.info(f"📁 Output file: {OUTPUT_FILE}")
    print(f"Input files:")
    print(f"  - JSON: {JSON_FILE}")
    print(f"  - Graph: {GRAPH_FILE}")
    print(f"  - Output: {OUTPUT_FILE}")

    try:
        logger.info("🔄 Loading initial data...")
        print("\n🔄 Loading initial data...")
        
        initial_data = load_all_data(JSON_FILE, GRAPH_FILE)
        if initial_data:
            total_components = len(initial_data["all_data"])
            logger.info(f"📊 Data loaded successfully")
            logger.info(f"📊 Total components to process: {total_components}")
            print(f"✅ Data loaded: {total_components} components found")

            # Use tqdm to show progress of component processing
            component_names = sorted(initial_data["all_data"].keys())
            progress_bar = tqdm(total=total_components, desc="Initializing...", unit="component", 
                               bar_format='{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]')

            logger.info("🏗️ Initializing documentation state...")
            print("🏗️ Initializing documentation state...")
            
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
                connected_nodes=[],
                # Initialize architectural diagram fields
                architectural_components={},
                architectural_relationships=[],
                diagram_mermaid_code="graph TD\n",
                diagram_description="## System Architecture Overview\n\nThis diagram represents the architectural components and their relationships:\n\n"
            )

            config = {"recursion_limit": total_components * 4 + 15}
            logger.info(f"⚙️ Graph configuration:")
            logger.info(f"⚙️ Graph recursion limit set to: {config['recursion_limit']}")
            logger.info(f"📝 Available documentation sections: {len(ALL_SECTIONS)}")
            print(f"⚙️ Graph recursion limit: {config['recursion_limit']}")
            print(f"📝 Documentation sections: {len(ALL_SECTIONS)}")
            print(f"--- ⚙️ Running graph with recursion limit: {config['recursion_limit']} ---")

            logger.info("🚀 Starting documentation generation pipeline...")
            print("\n🚀 STARTING DOCUMENTATION GENERATION PIPELINE")
            print("=" * 60)
            
            final_state = app.invoke(initial_state, config=config)
            
            logger.info("🎯 Pipeline execution completed")
            print("\n🎯 PIPELINE EXECUTION COMPLETED")
            print("=" * 60)
            
            if final_state and final_state.get("final_document"):
                # --- Save final document in versioned manner ---
                logger.info("💾 Saving final documentation...")
                print("💾 Saving final documentation...")
                
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

                # Log comprehensive statistics
                doc_length = len(final_state['final_document'])
                char_count = doc_length
                word_count = len(final_state['final_document'].split())
                line_count = final_state['final_document'].count('\n') + 1
                
                logger.info("🎉 DOCUMENTATION GENERATION COMPLETED SUCCESSFULLY")
                logger.info(f"⏰ End time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
                logger.info(f"⏱️ Total duration: {duration}")
                logger.info(f"📝 Final document saved to: {save_path}")
                logger.info(f"📊 Document statistics:")
                logger.info(f"📊   - Length: {char_count} characters")
                logger.info(f"📊   - Words: {word_count}")
                logger.info(f"📊   - Lines: {line_count}")
                logger.info(f"📁 Incremental saves stored in: {INCREMENTAL_SAVE_DIR}")
                
                # Log comprehensive processing summary
                log_processing_summary()

                print("\n" + "=" * 80)
                print("🎉 SUCCESS! DOCUMENTATION GENERATION COMPLETED")
                print("=" * 80)
                print(f"📝 Document saved to: {save_path}")
                print(f"⏱️ Total processing time: {duration}")
                print(f"� Document statistics:")
                print(f"   - Characters: {char_count:,}")
                print(f"   - Words: {word_count:,}")
                print(f"   - Lines: {line_count:,}")
                print(f"�📁 Incremental saves: {INCREMENTAL_SAVE_DIR}")
                
                # Run diagram beautification
                print("\n🎨 Running diagram beautification...")
                logger.info("🎨 Starting diagram beautification...")
                try:
                    import subprocess
                    beautify_script = os.path.join(FINAL_DOC_DIR, "beautify_diagram.py")
                    if os.path.exists(beautify_script):
                        logger.info(f"🎨 Executing beautification script: {beautify_script}")
                        result = subprocess.run([sys.executable, beautify_script], 
                                              capture_output=True, text=True, cwd=os.getcwd())
                        if result.returncode == 0:
                            logger.info("✅ Diagram beautification completed successfully")
                            print("✅ Diagram beautification completed successfully!")
                            print(result.stdout)
                        else:
                            logger.warning(f"⚠️ Diagram beautification had issues: {result.stderr}")
                            print(f"⚠️ Diagram beautification had issues: {result.stderr}")
                    else:
                        logger.warning(f"⚠️ Beautification script not found: {beautify_script}")
                        print("⚠️ Beautification script not found")
                except Exception as e:
                    logger.error(f"❌ Could not run beautification automatically: {e}")
                    print(f"⚠️ Could not run beautification automatically: {e}")
                    print(f"💡 You can run it manually: python {os.path.join(FINAL_DOC_DIR, 'beautify_diagram.py')}")

            else:
                logger.error("❌ FAILURE: The final document could not be generated")
                print("\n" + "=" * 80)
                print("❌ FAILURE: THE FINAL DOCUMENT COULD NOT BE GENERATED")
                print("=" * 80)
        
        else:
            logger.error("❌ Failed to load initial data")
            print("❌ Failed to load initial data")
            
    except Exception as e:
        logger.error(f"❌ CRITICAL ERROR during documentation generation: {e}")
        print(f"\n❌ CRITICAL ERROR: {e}")
        print("=" * 80)
    
    finally:
        # Ensure progress bar is always closed
        if progress_bar:
            progress_bar.close()
        
        end_time = datetime.now()
        total_duration = end_time - start_time
        logger.info(f"🏁 Process ended at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"🏁 Total execution time: {total_duration}")
        print(f"\n🏁 Process ended at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🏁 Total execution time: {total_duration}")
        print("=" * 80)