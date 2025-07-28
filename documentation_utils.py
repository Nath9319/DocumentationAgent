from datetime import datetime
from documentation_state import DocumentationState
import os
import re
import json
from config import logger, INCREMENTAL_SAVE_DIR

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
        logger.info(f" Incremental progress saved: {filepath}")
    except Exception as e:
        logger.error(f" Failed to save incremental progress: {e}")

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
        logger.info(f" Section content saved: {filepath}")
    except Exception as e:
        logger.error(f" Failed to save section content: {e}")

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
        logger.info(f" LLM interaction saved: {filepath}")
    except Exception as e:
        logger.error(f" Failed to save LLM interaction: {e}")

def log_processing_summary():
    """Log a comprehensive summary of all saved files and processing stats."""
    logger.info(" PROCESSING SUMMARY:")
    
    # Count files in incremental saves
    if os.path.exists(INCREMENTAL_SAVE_DIR):
        total_files = 0
        
        # Count main progress files
        progress_files = [f for f in os.listdir(INCREMENTAL_SAVE_DIR) if f.endswith('.json')]
        total_files += len(progress_files)
        logger.info(f" Progress files: {len(progress_files)}")
        
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
            logger.info(f" Section files: {section_count}")
        
        # Count architectural files
        arch_dir = os.path.join(INCREMENTAL_SAVE_DIR, "architecture")
        if os.path.exists(arch_dir):
            arch_files = [f for f in os.listdir(arch_dir) if f.endswith('.json')]
            total_files += len(arch_files)
            logger.info(f" Architectural files: {len(arch_files)}")
        
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
            logger.info(f" LLM interaction files: {llm_count}")
        
        logger.info(f" TOTAL INTERIM FILES SAVED: {total_files}")
        logger.info(f" All files saved in: {INCREMENTAL_SAVE_DIR}")
    else:
        logger.warning(f" Incremental save directory not found: {INCREMENTAL_SAVE_DIR}")