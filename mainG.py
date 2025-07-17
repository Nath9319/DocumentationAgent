import os
import json
import pickle
import networkx as nx
from typing import TypedDict, List, Dict, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers.string import StrOutputParser
from langchain_core.output_parsers.json import JsonOutputParser
from langchain_openai import AzureChatOpenAI
from langgraph.graph import StateGraph, END

# --- 1. Environment Setup & Model Initialization ---
llm = AzureChatOpenAI(
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("OPENAI_API_VERSION", "2024-02-01"),
    temperature=0.1, # Increased for more creative and better-structured writing
    max_tokens=40000
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

        Respond with the complete, updated markdown for the "Project Introduction" section.
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

        Respond with the complete, updated markdown for the "Installation & Setup" section.
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

        Respond with the complete, updated markdown for the "System Architecture" section.
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

        Respond with the complete, updated markdown for the "API Documentation" section.
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

        Respond with the complete, updated markdown for the "Code Documentation" section.
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

        Respond with the complete, updated markdown for the "Data Architecture" section.
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

        Respond with the complete, updated markdown for the "Logical Architecture" section.
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

        Respond with the complete, updated markdown for the "Integration Guide" section.
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

        Respond with the complete, updated markdown for the "Implementation View" section.
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

        Respond with the complete, updated markdown for the "Database Schemas" section.
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
        return state
    
    component_name = state["unprocessed_components"].pop(0)
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
    
    state["current_component_context"] = context
    
    # Store connected nodes info for use in other agents
    state["connected_nodes"] = connected_nodes_info
    
    print(f"--- 📥 Loader: Found {len(connected_nodes_info)} connected nodes ---")
    return state

# --- FIX: Modify scrapper_node to return a dictionary for state update ---
def scrapper_node(state: DocumentationState) -> dict:
    """Decides if the component's documentation is substantial and updates the state with the decision."""
    print(f"--- 🗑️ Scrapper: Analyzing '{state['current_component_name']}' ---")
    doc_length = len(state['current_component_doc'].split())
    
    decision = "proceed" # Default decision
    if doc_length < 10:
        print(f"--- 🗑️ Scrapper: Decision is to SCRAP (too short). ---")
        decision = "scrap"
    else:
        prompt = ChatPromptTemplate.from_template(
            """Analyze the documentation for component `{component_name}`. Is it trivial (e.g., a simple import, a variable declaration) or substantial (describes logic, a class, a function, configuration)?
            Documentation: --- {component_doc} ---
            Respond with a single word: "Proceed" if substantial, or "Scrap" if trivial."""
        )
        chain = prompt | llm | StrOutputParser()
        llm_decision = chain.invoke({"component_name": state["current_component_name"], "component_doc": state["current_component_doc"]})
        
        if "Scrap" in llm_decision:
            print(f"--- 🗑️ Scrapper: Decision is to SCRAP. ---")
            decision = "scrap"
        else:
            print(f"--- 🗑️ Scrapper: Decision is to PROCEED. ---")
            decision = "proceed"
            
    # Return a dictionary to update the state, this is the main fix.
    return {"scrapper_decision": decision}

def selector_node(state: DocumentationState) -> DocumentationState:
    """Selects which documentation sections are relevant for the current component and its connections."""
    print(f"--- 🎯 Selector: Choosing sections for '{state['current_component_name']}' ---")
    
    # Include connected nodes information in the selection process
    connected_nodes_summary = ""
    if state.get("connected_nodes"):
        connected_nodes_summary = f"\n\nConnected Components:\n"
        for node in state["connected_nodes"]:
            connected_nodes_summary += f"- {node['name']} ({node['type']}): {node['summary']}\n"
    
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
        "component_name": state["current_component_name"], 
        "component_doc": state["current_component_doc"], 
        "connected_nodes_summary": connected_nodes_summary,
        "sections": section_list_str
    })
    
    relevant_sections = response.get("relevant_sections", [])
    state["target_sections"] = [s for s in relevant_sections if s in ALL_SECTIONS]
    print(f"--- 🎯 Selector: Chosen sections: {state['target_sections']} ---")
    return state

def sequential_writer_node(state: DocumentationState) -> DocumentationState:
    """Invokes the specialist writer agents sequentially for the selected sections."""
    print(f"--- ✍️ Sequential Writers: Starting for '{state['current_component_name']}' ---")
    for section_name in state["target_sections"]:
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
        updated_section_content = chain.invoke({
            "section_name": section_name,
            "existing_content": existing_content or "This section is empty. Please start it.",
            "component_name": state["current_component_name"],
            "component_doc": state["current_component_doc"],
            "component_context": state["current_component_context"]
        })
        state["document_content"][section_name] = updated_section_content
        print(f"    - ✅ Writer for '{section_name}' finished.")
    return state

def compiler_node(state: DocumentationState) -> DocumentationState:
    """Assembles all the final sections into the complete, hierarchical document."""
    print("--- 📚 Compiler: Assembling Final Document ---")
    final_doc_parts = []
    for main_section, subsections in HIERARCHICAL_STRUCTURE.items():
        # Check if any subsection within this main section has content
        section_has_content = any(state["document_content"].get(sub, "").strip() for sub in subsections)
        
        # Only add the main section header if it has content
        if section_has_content:
            final_doc_parts.append(f"# {main_section}")
            for subsection_name in subsections:
                content = state["document_content"].get(subsection_name, "").strip()
                if content:
                    final_doc_parts.append(f"## {subsection_name}\n\n{content}")
    
    state["final_document"] = "\n\n---\n\n".join(final_doc_parts)
    print("--- 🎉 Compiler: Final document assembled! ---")
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
workflow.add_node("sequential_writers", sequential_writer_node)
workflow.add_node("compiler", compiler_node)

workflow.set_entry_point("loader")
workflow.add_conditional_edges("loader", should_continue_processing, {"continue": "scrapper", "end": "compiler"})

# --- FIX: Update the conditional edge to read the decision from the state ---
workflow.add_conditional_edges(
    "scrapper",
    lambda state: state["scrapper_decision"], # Read the decision from the state key
    {"scrap": "loader", "proceed": "selector"}
)

workflow.add_edge("selector", "sequential_writers")
workflow.add_edge("sequential_writers", "loader")
workflow.add_edge("compiler", END)

app = workflow.compile()

# --- Main execution block ---
if __name__ == "__main__":
    JSON_FILE = "output/CalculatorCode/documentation_and_graph_data.json"
    GRAPH_FILE = "output/CalculatorCode/conceptual_graph.pkl"
    OUTPUT_FILE = "Complete_Technical_Documentation_v5.md"
    initial_data = load_all_data(JSON_FILE, GRAPH_FILE)
    if initial_data:
        initial_state = DocumentationState(
            unprocessed_components=sorted(initial_data["all_data"].keys()),
            all_data=initial_data["all_data"],
            nx_graph=initial_data["nx_graph"],
            document_content={section: "" for section in ALL_SECTIONS},
            current_component_name=None,
            current_component_doc=None,
            current_component_context=None,
            target_sections=[],
            final_document=None,
            # --- FIX: Initialize the new state key ---
            scrapper_decision="",
            connected_nodes=[]  # Initialize connected nodes list
        )
        num_components = len(initial_data["all_data"])
        config = {"recursion_limit": num_components * 4 + 15}
        print(f"--- ⚙️ Running graph with recursion limit: {config['recursion_limit']} ---")
        final_state = app.invoke(initial_state, config=config)
        if final_state and final_state.get("final_document"):
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                f.write(final_state["final_document"])
            print(f"\n🚀 Success! Documentation saved to '{OUTPUT_FILE}'")
        else:
            print("\n❌ Failure: The final document could not be generated.")