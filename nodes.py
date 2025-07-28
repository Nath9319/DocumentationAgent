from typing import TypedDict, List, Dict, Any
from documentation_state import DocumentationState
from datetime import datetime, timedelta
import os
import sys
import re
from config import logger, INCREMENTAL_SAVE_DIR, llm
from documentation_utils import save_incremental_progress, save_section_content, save_llm_interaction, sanitize_filename
from langchain_core.output_parsers.string import StrOutputParser
from langchain_core.output_parsers.json import JsonOutputParser
from langchain_openai import AzureChatOpenAI
from system_prompts import ALL_SECTIONS, HIERARCHICAL_STRUCTURE, AGENT_PROMPTS
from langchain_core.prompts import ChatPromptTemplate
import pickle
import json
import threading
import asyncio
from diagrams import Diagram
from diagrams.programming.language import Python
from diagrams.generic.compute import Rack
from config import StreamHandlerUTF8, progress_bar
from diagrams import Diagram
from diagrams.programming.language import Python
from diagrams.generic.compute import Rack
from diagrams import Diagram, Cluster, Edge
from diagrams.azure.compute import AppServices, FunctionApps
from diagrams.azure.database import SQLDatabases
from diagrams.azure.integration import APIManagement
from diagrams.programming.language import Python

FINAL_DOC_DIR = "final_docs"
os.makedirs(FINAL_DOC_DIR, exist_ok=True)


def find_strategic_files(repo_path: str) -> List[str]:
    """
    Scans the repository and returns a list of architecturally significant files.
    """
    strategic_files = []
    
    # Define files and patterns to look for
    exact_matches = [
        'docker-compose.yml', 'Dockerfile', 'requirements.txt', 
        'pyproject.toml', 'package.json'
    ]
    extension_matches = ['.tf'] # For Terraform
    
    logger.info(f" Searching for strategic files in '{repo_path}'...")
    for root, dirs, files in os.walk(repo_path):
        # Exclude common non-source directories
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules', 'venv']]
        
        for file in files:
            file_path = os.path.join(root, file)
            
            if file in exact_matches:
                strategic_files.append(file_path)
                continue

            if any(file.endswith(ext) for ext in extension_matches):
                strategic_files.append(file_path)
                continue

            if file.endswith('.py'):
                # Prioritize key files that define structure and entrypoints
                if file in ['main.py', 'app.py', 'settings.py', 'config.py', 'server.py', 'function_app.py']:
                    strategic_files.append(file_path)
                elif any(keyword in root for keyword in ['models', 'schemas', 'routers', 'controllers', 'api']):
                    strategic_files.append(file_path)

    logger.info(f" Found {len(strategic_files)} strategic files for analysis.")
    return strategic_files


def analyze_files_to_data(file_paths: List[str], repo_root: str) -> Dict[str, Any]:
    """
    Analyzes the content of strategic files to create a low-level data dictionary.
    """
    logger.info("  Extracting content from strategic files...")
    analyzed_data = {}
    for file_path in file_paths:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                relative_path = os.path.relpath(file_path, repo_root)
                analyzed_data[relative_path] = {
                    "content": f.read(),
                    "path": relative_path,
                }
        except Exception as e:
            logger.warning(f"Could not read file {file_path}: {e}")
            continue
    return analyzed_data


def synthesize_architecture_model(analyzed_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Uses a two-step AI agent process to create a high-level conceptual architecture model.
    Step 1: Identify components.
    Step 2: Map relationships between them.
    """
    logger.info(" Starting advanced two-step architecture synthesis...")

    # Prepare a consolidated text block of all strategic file contents
    condensed_context = ""
    for path, data in analyzed_data.items():
        condensed_context += f"--- FILE: {path} ---\n{data['content']}\n\n"

    # --- Step 1: Identify Components ---
    logger.info(" Step 1: Identifying high-level components...")
    component_prompt = ChatPromptTemplate.from_template(
        """
        You are an expert System Architect. Your first task is to identify the primary, high-level components from the provided source code.
        Analyze the file contents and list all logical components. A component could be a user-facing API, a backend service, a data processing worker, or a database.

        Think step-by-step:
        1.  Scan for entrypoints like `main.py` or `app.py` to find APIs.
        2.  Look for files in `services`, `workers`, or `tasks` folders to identify backend services.
        3.  Identify database models or connection strings to find data stores.
        4.  Look at `Dockerfile` or `docker-compose.yml` to see how services are containerized.

        Based on your analysis, provide a JSON list of these components with a unique `id`, a clear `label`, a `type` (API, Service, Worker, Database), and a `group` (e.g., 'API Layer', 'Backend Services', 'Data Tier').

        SOURCE CODE CONTEXT:
        ---
        {context}
        ---

        Respond with a JSON object containing a single key "components" like this:
        {{
            "components": [
                {{
                    "id": "api_gateway",
                    "label": "API Gateway",
                    "type": "API",
                    "group": "API Layer"
                }},
                {{
                    "id": "user_service",
                    "label": "User Service",
                    "type": "Service",
                    "group": "Backend Services"
                }}
            ]
        }}
        """
    )
    
    component_chain = component_prompt | llm | JsonOutputParser()
    try:
        component_result = component_chain.invoke({"context": condensed_context})
        components = component_result.get("components", [])
        if not components:
            logger.error("AI failed to identify any components.")
            return {}
        logger.info(f" Identified {len(components)} components.")
    except Exception as e:
        logger.error(f" AI component identification failed: {e}")
        return {}

    # --- Step 2: Map Relationships ---
    logger.info(" Step 2: Mapping relationships between components...")
    relationship_prompt = ChatPromptTemplate.from_template(
        """
        You are an expert System Architect. You have been given a list of identified system components and the full source code context.
        Your second task is to determine the relationships and data flow between these components.

        Think step-by-step for each component:
        1.  Read the code associated with the component.
        2.  Identify function calls, API requests, or database queries it makes to OTHER components in the list.
        3.  For each interaction, describe it with a concise label (e.g., "Sends validation request to", "Fetches user data from", "Pushes job to").

        SOURCE CODE CONTEXT:
        ---
        {context}
        ---

        IDENTIFIED COMPONENTS:
        ---
        {components}
        ---

        Based on the source code, map the connections between the components. Respond with a JSON object containing a single key "relationships".
        {{
            "relationships": [
                {{
                    "from": "source_component_id",
                    "to": "target_component_id",
                    "label": "Description of the interaction"
                }}
            ]
        }}
        """
    )

    relationship_chain = relationship_prompt | llm | JsonOutputParser()
    try:
        relationship_result = relationship_chain.invoke({
            "context": condensed_context,
            "components": json.dumps(components, indent=2)
        })
        relationships = relationship_result.get("relationships", [])
        logger.info(f" Mapped {len(relationships)} relationships.")
    except Exception as e:
        logger.error(f" AI relationship mapping failed: {e}")
        relationships = []

    return {"components": components, "relationships": relationships}


def generate_diagram(model: Dict[str, Any], output_filename: str):
    """
    Generates and saves a professional architecture diagram from the high-level model.
    """
    logger.info(f" Generating diagram at {output_filename}.png...")
    
    components = model.get("components", [])
    relationships = model.get("relationships", [])

    if not components:
        logger.warning("No components in the model. Cannot generate diagram.")
        return

    icon_map = {
        "API": APIManagement,
        "Service": AppServices,
        "Worker": FunctionApps,
        "Database": SQLDatabases,
        "DEFAULT": Python
    }

    with Diagram("System Architecture (Azure)", filename=output_filename, show=False, direction="TB"):
        nodes = {}
        grouped_nodes = {}

        for comp_info in components:
            group = comp_info.get("group", "Default Group")
            if group not in grouped_nodes:
                grouped_nodes[group] = []
            grouped_nodes[group].append(comp_info)
        
        for group_name, component_list in grouped_nodes.items():
            with Cluster(group_name):
                for comp_info in component_list:
                    node_id = comp_info.get("id")
                    node_label = comp_info.get("label")
                    node_type = comp_info.get("type", "DEFAULT")
                    
                    Icon = icon_map.get(node_type, icon_map["DEFAULT"])
                    nodes[node_id] = Icon(node_label)

        for rel in relationships:
            from_node = rel.get("from")
            to_node = rel.get("to")
            rel_label = rel.get("label", "")
            
            if from_node in nodes and to_node in nodes:
                nodes[from_node] >> Edge(label=rel_label) >> nodes[to_node]
    
    logger.info(" Diagram generated successfully.")


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
        print(f" Error loading data: {e}")
        return {}

def component_loader_node(state: DocumentationState) -> DocumentationState:
    """Pops the next component and loads its data including connected nodes into the state."""
    if not state["unprocessed_components"]:
        logger.info(" Node: component_loader | Status: completed | No more components to process")
        print("--- Component Loader: All components processed ---")
        return state
    
    component_name = state["unprocessed_components"].pop(0)
    remaining = len(state["unprocessed_components"])
    total_components = len(state["all_data"])
    current_idx = total_components - remaining
    
    # Enhanced logging with node status
    logger.info(f" Node: component_loader | Status: started | Component: '{component_name}'")
    logger.info(f" Loading component: '{component_name}' ({remaining} remaining - {current_idx}/{total_components})")
    print(f"\n--- Component Loader: Loading component '{component_name}' ({current_idx}/{total_components}) ---")
    
    # Update progress bar with detailed information
    global progress_bar
    if progress_bar and threading.current_thread() is threading.main_thread():
        # Set the current position correctly
        progress_bar.n = current_idx - 1
        remaining_count = total_components - current_idx
        percentage = (current_idx / total_components) * 100
        
        # Update description with file details
        progress_bar.set_description(f" {component_name} | {remaining_count} left")
        
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
    logger.info(f" Component details | Name: '{component_name}' | Document length: {doc_length} words")
    print(f"    - Document length: {doc_length} words")
    print(f"    - Component type: {component_data.get('type', 'Unknown')}")
    
    # Set simple context without connected nodes
    state["current_component_context"] = f"Processing component: {component_name}"
    
    # Store empty connected nodes info
    state["connected_nodes"] = []
    
    # Save incremental progress
    save_incremental_progress(state, "component_loaded")
    
    logger.info(f" Node: component_loader | Status: completed | Component: '{component_name}' loaded successfully")
    print(f"--- Component Loader: Component '{component_name}' loaded successfully ---")
    return state

def scrapper_node(state: DocumentationState) -> dict:
    """Enhanced scrapper that filters out trivial components more effectively."""
    component_name = state['current_component_name']
    component_doc = state['current_component_doc']
    
    logger.info(f" Node: scrapper | Status: started | Component: '{component_name}'")
    logger.info(f" Enhanced Scrapper: Analyzing component '{component_name}'")
    print(f"--- Enhanced Scrapper: Analyzing '{component_name}' ---")
    
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
            logger.info(f" Scrapper Decision: REJECT | Reason: matches trivial pattern '{pattern}' | Component: '{component_name}'")
            logger.info(f" Pre-filter Decision: SCRAP (matches trivial pattern: {pattern})")
            print(f"--- Enhanced Scrapper: Decision is to REJECT (trivial pattern: {pattern}). ---")
            save_incremental_progress(state, "scrapper_scrap")
            return {"scrapper_decision": "scrap"}
    
    # Word count check
    doc_length = len(component_doc.split())
    logger.info(f" Document analysis | Component: '{component_name}' | Length: {doc_length} words")
    print(f"    - Analyzing document length: {doc_length} words")
    
    if doc_length < 15:  # Increased threshold
        logger.info(f" Scrapper Decision: REJECT | Reason: document too short ({doc_length} words) | Component: '{component_name}'")
        logger.info(f" Decision: SCRAP (document too short: {doc_length} words)")
        print(f"--- Enhanced Scrapper: Decision is to REJECT (too short: {doc_length} words). ---")
        save_incremental_progress(state, "scrapper_scrap")
        return {"scrapper_decision": "scrap"}
    
    # Content-based filtering
    doc_lower = component_doc.lower()
    
    # Check for import-only content
    lines = [line.strip() for line in component_doc.split('\n') if line.strip()]
    non_trivial_lines = []
    
    logger.info(f" Content analysis | Component: '{component_name}' | Total lines: {len(lines)}")
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
    
    logger.info(f" Content structure | Component: '{component_name}' | Non-trivial lines: {len(non_trivial_lines)}")
    print(f"    - Non-trivial lines found: {len(non_trivial_lines)}")
    
    # If less than 3 non-trivial lines, it's probably not substantial
    if len(non_trivial_lines) < 3:
        logger.info(f" Scrapper Decision: REJECT | Reason: insufficient non-trivial content ({len(non_trivial_lines)} lines) | Component: '{component_name}'")
        logger.info(f" Decision: SCRAP (insufficient non-trivial content: {len(non_trivial_lines)} lines)")
        print(f"--- Enhanced Scrapper: Decision is to REJECT (insufficient content: {len(non_trivial_lines)} lines). ---")
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
        logger.info(f" Scrapper Decision: REJECT | Reason: contains trivial indicators {trivial_found} | Component: '{component_name}'")
        logger.info(f" Decision: SCRAP (contains trivial indicators)")
        print(f"--- Enhanced Scrapper: Decision is to REJECT (trivial indicators: {trivial_found}). ---")
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
    
    logger.info(f" Substantial content analysis | Component: '{component_name}' | Indicators found: {substantial_count} | Types: {substantial_found[:5]}")
    print(f"    - Substantial content indicators: {substantial_count} found")
    
    # If it has multiple substantial indicators, likely proceed
    if substantial_count >= 2:
        logger.info(f" Scrapper Decision: ACCEPT | Reason: substantial indicators ({substantial_count}) | Component: '{component_name}'")
        logger.info(f" Pre-approval: PROCEED (substantial indicators: {substantial_count})")
        print(f"--- Enhanced Scrapper: Decision is to ACCEPT (substantial content: {substantial_count} indicators). ---")
        save_incremental_progress(state, "scrapper_proceed")
        return {"scrapper_decision": "proceed"}
    
    # For borderline cases, use LLM with enhanced prompt
    logger.info(f" Scrapper LLM consultation | Component: '{component_name}' | Reason: borderline case")
    logger.info(f" Borderline case - consulting enhanced LLM for '{component_name}'")
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
        logger.info(f" LLM call initiated | Component: '{component_name}' | Type: enhanced_scrapper")
        llm_decision = llm.invoke({
            "component_name": component_name, 
            "component_doc": component_doc
        })
        
        logger.info(f" LLM response received | Component: '{component_name}' | Decision: '{llm_decision.strip()}'")
        
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
            logger.info(f" Scrapper Decision: REJECT | Reason: LLM decision ('{llm_decision.strip()}') | Component: '{component_name}'")
            logger.info(f" Enhanced LLM Decision: SCRAP for '{component_name}'")
            print(f"--- Enhanced Scrapper: Decision is to REJECT (LLM decision). ---")
            save_incremental_progress(state, "scrapper_scrap")
            return {"scrapper_decision": "scrap"}
        else:
            logger.info(f" Scrapper Decision: ACCEPT | Reason: LLM decision ('{llm_decision.strip()}') | Component: '{component_name}'")
            logger.info(f" Enhanced LLM Decision: PROCEED for '{component_name}'")
            print(f"--- Enhanced Scrapper: Decision is to ACCEPT (LLM decision). ---")
            save_incremental_progress(state, "scrapper_proceed")
            return {"scrapper_decision": "proceed"}
            
    except Exception as e:
        logger.error(f" LLM error | Component: '{component_name}' | Error: {e}")
        logger.error(f" LLM error for '{component_name}': {e}")
        # Default to proceed on error to avoid losing potentially valuable content
        logger.info(f" Scrapper Decision: ACCEPT (default) | Reason: LLM error fallback | Component: '{component_name}'")
        logger.info(f" Defaulting to PROCEED due to LLM error")
        print(f"--- Enhanced Scrapper: Defaulting to ACCEPT (LLM error). ---")
        save_incremental_progress(state, "scrapper_proceed")
        return {"scrapper_decision": "proceed"}

def selector_node(state: DocumentationState) -> DocumentationState:
    """Selects which documentation sections are relevant for the current component and its connections."""
    component_name = state['current_component_name']
    
    logger.info(f" Node: selector | Status: started | Component: '{component_name}'")
    logger.info(f" Selector: Choosing sections for '{component_name}'")
    print(f"--- Selector: Choosing sections for '{component_name}' ---")
    
    # Include connected nodes information in the selection process
    connected_nodes_summary = ""
    if state.get("connected_nodes"):
        connected_nodes_summary = f"\n\nConnected Components:\n"
        for node in state["connected_nodes"]:
            connected_nodes_summary += f"- {node['name']} ({node['type']}): {node['summary']}\n"
        logger.info(f" Connected components | Component: '{component_name}' | Count: {len(state['connected_nodes'])}")
        print(f"    - Found {len(state['connected_nodes'])} connected components")
    else:
        logger.info(f" Connected components | Component: '{component_name}' | Count: 0")
        print(f"    - No connected components found")
    
    logger.info(f" LLM call initiated | Component: '{component_name}' | Type: section_selector")
    logger.info(f" Consulting LLM for section selection for '{component_name}'")
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
        
        logger.info(f" LLM response received | Component: '{component_name}' | Sections selected: {len(response.get('relevant_sections', []))}")
        
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
        
        logger.info(f" Section selection | Component: '{component_name}' | Selected: {len(state['target_sections'])} sections")
        logger.info(f" Selected sections | Component: '{component_name}' | Sections: {state['target_sections']}")
        logger.info(f" Selected {len(state['target_sections'])} sections for '{component_name}': {state['target_sections']}")
        print(f"--- Selector: Chosen sections ({len(state['target_sections'])}): {state['target_sections']} ---")
        
        # Log each section selection decision
        for section in state['target_sections']:
            print(f"    - Selected: {section}")
        
    except Exception as e:
        logger.error(f" Section selection failed | Component: '{component_name}' | Error: {e}")
        # Fallback to default sections
        state["target_sections"] = ["Project Introduction", "Code Documentation"]
        logger.info(f" Fallback selection | Component: '{component_name}' | Using default sections: {state['target_sections']}")
        print(f"    - Using fallback sections due to error: {state['target_sections']}")
    
    # Save incremental progress
    save_incremental_progress(state, "sections_selected")
    
    logger.info(f" Node: selector | Status: completed | Component: '{component_name}' | Sections: {len(state['target_sections'])}")
    
    return state
# Updated parallel processing to include architectural analysis
async def parallel_processing_node(state: DocumentationState) -> DocumentationState:
    """Runs both documentation writers and architectural analyzer in parallel."""
    component_name = state['current_component_name']
    total_sections = len(state["target_sections"])
    
    logger.info(f" Node: parallel_processing | Status: started | Component: '{component_name}' | Tasks: {total_sections + 1}")
    logger.info(f" Parallel Processing: Starting writers + architecture for '{component_name}'")
    print(f"--- Parallel Processing: Starting {total_sections} writers + architecture ---")
    
    # Log what sections will be processed
    logger.info(f" Processing sections | Component: '{component_name}' | Sections: {state['target_sections']}")
    for i, section in enumerate(state["target_sections"], 1):
        print(f"    - Task {i}: Documentation for '{section}'")
    print(f"    - Task {total_sections + 1}: Architectural analysis")
    
    # Create tasks for both documentation and architecture
    tasks = []
    
    # Add documentation writer tasks
    for section_name in state["target_sections"]:
        tasks.append(process_documentation_section(state, section_name))
    
    # Add architectural analysis task
    #tasks.append(process_architectural_analysis(state))
    
    try:
        # Execute all tasks concurrently
        logger.info(f" Executing parallel tasks | Component: '{component_name}' | Total tasks: {len(tasks)} ({total_sections} docs + 1 architecture)")
        logger.info(f" Executing {len(tasks)} parallel tasks ({total_sections} docs + 1 architecture)")
        print(f"    - Executing {len(tasks)} tasks concurrently...")
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process documentation results
        successful_sections = 0
        failed_sections = 0
        
        for i, result in enumerate(results[:-1]):  # All except the last (architecture) result
            section_name = state["target_sections"][i]
            if isinstance(result, Exception):
                logger.error(f" Documentation task failed | Component: '{component_name}' | Section: '{section_name}' | Error: {result}")
                logger.error(f" Documentation writer exception: {result}")
                print(f"    - Failed: '{section_name}' - {result}")
                failed_sections += 1
            else:
                section_name, content = result
                state["document_content"][section_name] = content
                logger.info(f" Documentation task completed | Component: '{component_name}' | Section: '{section_name}' | Length: {len(content)} chars")
                print(f"    - Completed: '{section_name}' ({len(content)} chars)")
                successful_sections += 1
        
        # Process architectural result
        arch_result = results[-1]
        if isinstance(arch_result, Exception):
            logger.error(f" Architectural task failed | Component: '{component_name}' | Error: {arch_result}")
            logger.error(f" Architectural analysis exception: {arch_result}")
            print(f"    - Architecture analysis failed: {arch_result}")
        else:
            # Architectural analysis updates state in-place
            logger.info(f" Architectural task completed | Component: '{component_name}'")
            logger.info(f" Architectural analysis completed successfully")
            print(f"    - Architecture analysis completed")
        
        logger.info(f" Parallel processing summary | Component: '{component_name}' | Successful docs: {successful_sections} | Failed docs: {failed_sections}")
        logger.info(f" Parallel processing completed: {successful_sections} docs successful, {failed_sections} docs failed")
        print(f"--- Summary: {successful_sections} successful, {failed_sections} failed ---")
        
    except Exception as exc:
        logger.error(f" Parallel processing failed | Component: '{component_name}' | Error: {exc}")
        logger.error(f" Parallel processing failed: {exc}")
        print(f"--- Parallel processing failed: {exc} ---")
    
    # Save incremental progress
    save_incremental_progress(state, "parallel_processing_completed")
    
    logger.info(f" Node: parallel_processing | Status: completed | Component: '{component_name}'")
    
    return state

async def process_documentation_section(state: DocumentationState, section_name: str) -> tuple[str, str]:
    """Process a single documentation section."""
    component_name = state['current_component_name']
    
    logger.info(f" Processing documentation section | Component: '{component_name}' | Section: '{section_name}'")
    
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
    
    logger.info(f" Section context | Component: '{component_name}' | Section: '{section_name}' | Existing content: {existing_length} chars")
    
    prompt = ChatPromptTemplate.from_template(writer_prompt_template)
    chain = prompt | llm | StrOutputParser()
    
    try:
        logger.info(f" LLM call initiated | Component: '{component_name}' | Section: '{section_name}' | Type: documentation_writer")
        
        updated_section_content = chain.ainvoke({
            "section_name": section_name,
            "existing_content": existing_content or "This section is empty. Please start it.",
            "component_name": component_name,
            "component_doc": state["current_component_doc"],
            "component_context": state["current_component_context"]
        })
        
        new_length = len(updated_section_content)
        
        logger.info(f" LLM response received | Component: '{component_name}' | Section: '{section_name}' | New content: {new_length} chars")
        logger.info(f" Section processing completed | Component: '{component_name}' | Section: '{section_name}' | Content generated: {new_length} chars")
        
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
        logger.error(f" Section processing failed | Component: '{component_name}' | Section: '{section_name}' | Error: {e}")
        logger.error(f" Error processing section '{section_name}': {e}")
        error_content = f"Error generating content for {section_name}: {str(e)}"
        return section_name, error_content

# def parallel_processing_node_sync(state: DocumentationState) -> DocumentationState:
#     """Synchronous wrapper for parallel processing."""
#     return asyncio.run(parallel_processing_node(state))

# Updated parallel_writer_node with integrated progress tracking
async def parallel_writer_node(state: DocumentationState) -> DocumentationState:
    """Invokes the specialist writer agents in parallel for the selected sections using async/await."""
    component_name = state['current_component_name']
    total_sections = len(state["target_sections"])
    logger.info(f" Parallel Writers: Starting for '{component_name}' with {total_sections} sections")
    print(f"--- Parallel Writers: Starting for '{component_name}' ---")
    
    # Global progress tracking
    completed_sections = 0
    
    async def process_section(section_name: str) -> tuple[str, str]:
        """Process a single section asynchronously and return (section_name, content)."""
        nonlocal completed_sections
        completed_sections += 1
        
        logger.info(f" Processing section: '{section_name}' for component '{component_name}' ({completed_sections}/{total_sections})")
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
            logger.info(f" Calling LLM for section '{section_name}' in component '{component_name}'")
            updated_section_content = await chain.ainvoke({
                "section_name": section_name,
                "existing_content": existing_content or "This section is empty. Please start it.",
                "component_name": component_name,
                "component_doc": state["current_component_doc"],
                "component_context": state["current_component_context"]
            })
            
            # Save section content after LLM call
            save_section_content(component_name, section_name, updated_section_content)
            
            logger.info(f" Section '{section_name}' completed for component '{component_name}' ({completed_sections}/{total_sections})")
            print(f"    - Writer for '{section_name}' finished.")
            return section_name, updated_section_content
            
        except Exception as e:
            logger.error(f" Error processing section '{section_name}' for component '{component_name}': {e}")
            print(f"    - Error in writer for '{section_name}': {e}")
            return section_name, f"Error generating content for {section_name}: {str(e)}"
    
    # Use asyncio.gather for concurrent execution of all sections
    try:
        # Create tasks for all sections
        tasks = [process_section(section_name) for section_name in state["target_sections"]]

         # --- FIX: ADD THIS LINE ---
        # Add the architectural analysis task to run in parallel
        #tasks.append(process_architectural_analysis(state))
        # -------------------------
        
        # Execute all tasks concurrently
        logger.info(f" Executing {len(tasks)} LLM calls concurrently for '{component_name}'")
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results and handle any exceptions
        successful_sections = 0
        failed_sections = 0
        
        for result in results[:-1]:
            if isinstance(result, Exception):
                logger.error(f" Writer exception for '{component_name}': {result}")
                print(f"    - Writer generated an exception: {result}")
                failed_sections += 1
            else:
                section_name, content = result
                state["document_content"][section_name] = content
                successful_sections += 1
                 
        # Optional: Check if the architecture task failed
        arch_result = results[-1]
        if isinstance(arch_result, Exception):
            logger.error(f" Architectural analysis exception for '{component_name}': {arch_result}")
            print(f"     - Architecture analysis failed: {arch_result}")
                
        logger.info(f" Parallel Writers completed for '{component_name}': {successful_sections} successful, {failed_sections} failed")
                
    except Exception as exc:
        logger.error(f" Parallel writers failed for '{component_name}': {exc}")
        print(f"    - Parallel writers failed with exception: {exc}")
    
    # Save incremental progress
    save_incremental_progress(state, "parallel_writers_completed")
    
    logger.info(f" Parallel Writers: Completed all {len(state['target_sections'])} sections for '{component_name}'")
    print(f"--- Parallel Writers: Completed all {len(state['target_sections'])} sections ---")
    return state

# Remove the duplicate patching code and use the consolidated version
# def parallel_writer_node_sync(state: DocumentationState) -> DocumentationState:
#     """Synchronous wrapper for the async parallel_writer_node function."""
#     return asyncio.run(parallel_writer_node(state))

def parallel_writer_node_sync(state: DocumentationState) -> DocumentationState:
    """Synchronous wrapper for the async parallel_writer_node function."""
    try:
        # Add timeout to prevent hanging
        return asyncio.run(asyncio.wait_for(parallel_writer_node(state), timeout=300))  # 5 minutes timeout
    except asyncio.TimeoutError:
        logger.error(f" Parallel processing timed out for component: {state.get('current_component_name')}")
        return state
    except Exception as e:
        logger.error(f" Parallel processing failed: {e}")
        return state
    
def compiler_node(state: DocumentationState) -> DocumentationState:
    """Assembles all the final sections into the complete, hierarchical document."""
    logger.info("� Node: compiler | Status: started")
    logger.info("� Compiler: Starting document assembly")
    print("--- Compiler: Assembling Final Document ---")

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

    logger.info(f" Document assembly analysis | Total available sections: {total_sections_available} | Sections with content: {sections_with_content}")
    print(f"    - Sections available: {total_sections_available}")
    print(f"    - Sections with content: {sections_with_content}")

    for main_section, subsections in HIERARCHICAL_STRUCTURE.items():
        # Check if any subsection within this main section has content
        section_has_content = any(state["document_content"].get(sub, "").strip() for sub in subsections)

        # Only add the main section header if it has content
        if section_has_content:
            final_doc_parts.append(f"# {main_section}")
            logger.info(f" Adding main section: {main_section}")
            print(f"    - Adding main section: {main_section}")

            for subsection_name in subsections:
                content = state["document_content"].get(subsection_name, "").strip()
                if content:
                    # Remove wrapping triple backticks if present
                    cleaned_content = strip_triple_backticks(content)
                    content_length = len(cleaned_content)
                    final_doc_parts.append(f"## {subsection_name}\n\n{cleaned_content}")
                    sections_included += 1
                    logger.info(f" Added subsection: {subsection_name} | Length: {content_length} chars")
                    logger.info(f" Added subsection: {subsection_name}")
                    print(f"      - Added: {subsection_name} ({content_length} chars)")
                else:
                    logger.info(f" Skipped subsection (empty): {subsection_name}")
        else:
            logger.info(f" Skipped main section (no content): {main_section}")
            print(f"    - Skipped main section: {main_section} (no content)")

    state["final_document"] = "\n\n---\n\n".join(final_doc_parts)
    final_doc_length = len(state["final_document"])

    logger.info(f" Document assembly completed | Sections included: {sections_included}/{sections_with_content} | Total length: {final_doc_length} chars")
    logger.info(f" Compiler: Document assembled with {sections_included} sections")
    print("--- Compiler: Final document assembled! ---")
    print(f"    - Final document: {sections_included} sections, {final_doc_length} characters")

    # Save final document progress
    save_incremental_progress(state, "final_document_compiled")

    logger.info(" Node: compiler | Status: completed")

    return state


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
    
    logger.info(f" Basic diagram files saved in: {diagrams_dir}")

def check_and_recover_state():
    """Check for hanging state and provide recovery options."""
    latest_save = None
    if os.path.exists(INCREMENTAL_SAVE_DIR):
        save_files = [f for f in os.listdir(INCREMENTAL_SAVE_DIR) if f.endswith('.json')]
        if save_files:
            latest_save = max(save_files, key=lambda x: os.path.getctime(os.path.join(INCREMENTAL_SAVE_DIR, x)))
            save_time = datetime.fromtimestamp(os.path.getctime(os.path.join(INCREMENTAL_SAVE_DIR, latest_save)))
            if datetime.now() - save_time > timedelta(minutes=10):
                logger.warning(f" Last save was {datetime.now() - save_time} ago. Possible hang detected.")
                return os.path.join(INCREMENTAL_SAVE_DIR, latest_save)
    return None

def generate_final_diagrams_diagram(state: DocumentationState) -> str:
    """
    Generates a professional architecture diagram using Azure icons.
    """
    from diagrams.azure.compute import AppServices, FunctionApps, VM
    from diagrams.azure.database import SQLDatabases
    from diagrams.azure.integration import APIManagement
    from diagrams.azure.storage import BlobStorage
    from diagrams import Diagram, Cluster, Edge

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    diagrams_dir = os.path.join(FINAL_DOC_DIR, "diagrams")
    os.makedirs(diagrams_dir, exist_ok=True)
    output_filename = os.path.join(diagrams_dir, f"azure_architecture_{timestamp}")

    components = state.get("architectural_components", [])
    relationships = state.get("architectural_relationships", [])

    if not components:
        return "No architectural components found to generate a diagram."

    # --- UPDATED AZURE ICON MAPPING ---
    icon_map = {
        "API": APIManagement,
        "Service": AppServices,
        "Worker": FunctionApps,
        "Database": SQLDatabases,
        "DEFAULT": Python # Fallback icon
    }

    with Diagram("System Architecture (Azure)", filename=output_filename, show=False):
        nodes = {}
        grouped_nodes = {}

        for comp_info in components:
            group = comp_info.get("group", "Default Group")
            if group not in grouped_nodes:
                grouped_nodes[group] = []
            grouped_nodes[group].append(comp_info)
        
        for group_name, component_list in grouped_nodes.items():
            with Cluster(group_name):
                for comp_info in component_list:
                    node_id = comp_info.get("id")
                    node_label = comp_info.get("label")
                    node_type = comp_info.get("type", "DEFAULT")
                    
                    Icon = icon_map.get(node_type, icon_map["DEFAULT"])
                    nodes[node_id] = Icon(node_label)

        for rel in relationships:
            from_node = rel.get("from")
            to_node = rel.get("to")
            rel_label = rel.get("label", "")
            
            if from_node in nodes and to_node in nodes:
                nodes[from_node] >> Edge(label=rel_label) >> nodes[to_node]
    
    return f"Azure diagram generated at {output_filename}.png"


def run_architecture_generation_node(state: DocumentationState) -> DocumentationState:
    """Runs the standalone architecture generation process as the final step."""
    logger.info(" Starting standalone architecture diagram generation...")
    
    if len(sys.argv) < 2:
        logger.error(" Architecture generation requires a repository path argument.")
        print("Usage: python main2.py <path_to_repository>")
        return state
        
    repo_path = sys.argv[1]
    if not os.path.isdir(repo_path):
        logger.error(f" Repository path '{repo_path}' not found for architecture generation.")
        return state

    # Execute the sequence from the first script
    strategic_files = find_strategic_files(repo_path)
    if not strategic_files:
        print("Could not find any strategic files to generate architecture diagram.")
        return state

    analyzed_data = analyze_files_to_data(strategic_files, repo_path)
    architecture_model = synthesize_architecture_model(analyzed_data)
    
    if not architecture_model.get("components"):
        print("Failed to create an architectural model. Exiting diagram generation.")
        return state

    repo_name = os.path.basename(os.path.normpath(repo_path))
    output_dir = os.path.join("final_docs", "diagrams")
    os.makedirs(output_dir, exist_ok=True)
    
    # Save the intermediate JSON model for debugging in the new directory
    model_path = os.path.join(output_dir, "architecture_model.json")
    with open(model_path, 'w', encoding='utf-8') as f:
        json.dump(architecture_model, f, indent=2)
    logger.info(f" Intermediate architecture model saved to: {model_path}")
    
    # Define the new base filename for the diagram
    diagram_filename_base = os.path.join(output_dir, "final_architecture")
    generate_diagram(architecture_model, diagram_filename_base)
        
    # Update the success message to reflect the new path
    print(f"\n Success! Advanced system architecture diagram saved in: {output_dir}")
    logger.info(" Standalone architecture diagram generation complete.")
    
    return state

# --- 5. Define Graph Edges & Control Flow ---


def should_continue_processing(state: DocumentationState) -> str:
    """Determines if there are more components to process."""
    return "continue" if state["unprocessed_components"] else "end"
