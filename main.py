# main.py
#
# This is the main entry point for the AI Documentation Agent.
# ENHANCED VERSION: Added quality indicators and metadata tracking

import os
import sys
import pickle
import json
import networkx as nx
from dotenv import load_dotenv
from datetime import datetime
from typing import Dict, Any
from core.construct_graph import CodeGraph
from agent.agent_graph import create_agent_graph

def run_documentation_agent(repo_path: str):
    """
    Sets up and runs the entire documentation and conceptual graph generation process.
    ENHANCED: Now tracks quality metrics and provides detailed output metadata.
    """
    print("--- AI Documentation Agent Initializing (Enhanced Version) ---")
    
    # --- Step 1: Environment Setup ---
    load_dotenv()
    if not os.getenv("AZURE_OPENAI_API_KEY") or not os.getenv("AZURE_OPENAI_ENDPOINT"):
        print("Error: AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT must be set in the .env file.")
        sys.exit(1)

    if not os.path.isdir(repo_path):
        print(f"Error: Repository path '{repo_path}' not found.")
        sys.exit(1)

    # --- Step 2: Construct or Load the AST Code Graph ---
    graph_file = "graph.pkl"
    if os.path.exists(graph_file):
        print(f"Found existing graph file: '{graph_file}'. Loading it.")
        with open(graph_file, 'rb') as f:
            repo_graph = pickle.load(f)
    else:
        print(f"No graph file found. Constructing new graph for '{repo_path}'...")
        code_graph_builder = CodeGraph(root=repo_path)
        repo_graph = code_graph_builder.build_graph()
        
        with open(graph_file, 'wb') as f:
            pickle.dump(repo_graph, f)
        print(f"Successfully constructed and saved graph to '{graph_file}'.")

    if not repo_graph.nodes():
        print("Error: The constructed graph has no nodes. Cannot proceed.")
        sys.exit(1)

    # --- Step 3: Set up Output Directory ---
    repo_name = os.path.basename(os.path.normpath(repo_path))
    output_dir = os.path.join("output", repo_name)
    os.makedirs(output_dir, exist_ok=True)
    print(f"Outputs will be saved in: '{output_dir}'")
    
    # --- Step 4: Create and Run the LangGraph Agent ---
    agent_app = create_agent_graph()
    
    # Initialize the state with all required keys including enhanced metadata
    initial_state = {
        "repo_graph": repo_graph,
        "conceptual_graph": nx.MultiDiGraph(),
        "final_output_data": {},
        "context_metadata": {}  # ENHANCED: Initialize context metadata
    }
    
    total_nodes = len(repo_graph.nodes())
    recursion_limit = total_nodes * 6
    config = {"recursion_limit": recursion_limit}
    
    print(f"\n--- Invoking Enhanced Agent ---")
    print(f"Total nodes: {total_nodes}")
    print(f"Recursion limit: {recursion_limit}")
    print(f"Features: Advanced search, fuzzy matching, context validation")
    print(f"{'='*60}\n")
    
    # Use .invoke() to run the agent to completion and get the final state.
    start_time = datetime.now()
    final_state = agent_app.invoke(initial_state, config=config)
    end_time = datetime.now()
    processing_time = (end_time - start_time).total_seconds()

    # --- Step 5: Save the Final Outputs with Enhanced Metadata ---
    if final_state:
        print("\n--- Agent finished. Saving enhanced outputs. ---")
        
        # 1. Save the LLM-generated conceptual graph
        conceptual_graph = final_state.get('conceptual_graph')
        if conceptual_graph:
            conceptual_graph_path = os.path.join(output_dir, "conceptual_graph.pkl")
            with open(conceptual_graph_path, 'wb') as f:
                pickle.dump(conceptual_graph, f)
            print(f"✓ Conceptual graph saved to: {conceptual_graph_path}")
        
        # 2. Save the consolidated documentation and graph data as JSON
        final_output_data = final_state.get('final_output_data', {})
        json_output_path = os.path.join(output_dir, "documentation_and_graph_data.json")
        with open(json_output_path, 'w', encoding='utf-8') as f:
            json.dump(final_output_data, f, indent=2)
        print(f"✓ Consolidated JSON data saved to: {json_output_path}")

        # 3. ENHANCED: Save generation metadata
        quality_metrics = calculate_quality_metrics(final_output_data)
        generation_metadata = {
            'generation_timestamp': datetime.now().isoformat(),
            'processing_time_seconds': processing_time,
            'repository_path': repo_path,
            'total_nodes': total_nodes,
            'documented_nodes': len(final_state.get('documented_nodes', {})),
            'quality_metrics': quality_metrics,
            'enhanced_features': [
                'fuzzy_dependency_matching',
                'context_validation',
                'multi_strategy_search',
                'confidence_scoring',
                'fallback_dependency_extraction'
            ]
        }
        
        metadata_path = os.path.join(output_dir, "generation_metadata.json")
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(generation_metadata, f, indent=2)
        print(f"✓ Generation metadata saved to: {metadata_path}")

        # 4. Save individual markdown files for each documented node
        print("\n--- Saving individual documentation files... ---")
        '''docs_output_dir = os.path.join(output_dir, "documentation")
        os.makedirs(docs_output_dir, exist_ok=True)

        low_confidence_count = 0
        for node_name, data in final_output_data.items():
            if 'documentation' in data and data['documentation']:
                # Sanitize the node name for use as a filename
                sanitized_name = "".join(c for c in node_name if c.isalnum() or c in ('_', '-')).rstrip()
                doc_path = os.path.join(docs_output_dir, f"{sanitized_name}.md")
                
                # Check context quality
                context_metadata = data.get('context_metadata', {})
                avg_confidence = context_metadata.get('average_confidence', 1.0)
                if avg_confidence < 0.7:
                    low_confidence_count += 1
                
                with open(doc_path, "w", encoding='utf-8') as f:
                    f.write(f"# Documentation for `{node_name}`\n\n")
                    
                    # Add metadata header if confidence is low
                    if avg_confidence < 0.7:
                        f.write(f"> ⚠️ **Quality Notice**: Documentation generated with "
                               f"{avg_confidence:.0%} confidence. Some dependencies could not be fully resolved.\n\n")
                    
                    f.write(data['documentation'])
                    
                    # Add metadata footer
                    f.write(f"\n\n---\n")
                    f.write(f"*Generated with {avg_confidence:.0%} context confidence*\n")
                    
        print(f"✓ Saved {len(final_output_data)} documentation files to: '{docs_output_dir}'")
        
        if low_confidence_count > 0:
            print(f"⚠️  {low_confidence_count} files generated with low confidence (<70%)")

        # 5. Generate summary report
        print("\n{'='*60}")
        print("DOCUMENTATION GENERATION SUMMARY")
        print(f"{'='*60}")
        print(f"Repository: {repo_name}")
        print(f"Total Nodes: {total_nodes}")
        print(f"Documented: {len(final_output_data)}")
        print(f"Processing Time: {processing_time:.2f} seconds")
        print(f"Average Context Quality: {quality_metrics['average_context_confidence']:.1%}")
        print(f"Nodes with High Confidence (>90%): {quality_metrics['high_confidence_nodes']}")
        print(f"Nodes with Medium Confidence (70-90%): {quality_metrics['medium_confidence_nodes']}")
        print(f"Nodes with Low Confidence (<70%): {quality_metrics['low_confidence_nodes']}")
        print(f"{'='*60}\n")

    else:
        print("\n--- Agent finished, but no final state was captured. Outputs not saved. ---")


def calculate_quality_metrics(final_output_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate quality metrics from the final output data.
    """
    total_nodes = len(final_output_data)
    confidence_scores = []
    high_confidence = 0
    medium_confidence = 0
    low_confidence = 0
    
    for node_name, data in final_output_data.items():
        context_metadata = data.get('context_metadata', {})
        avg_confidence = context_metadata.get('average_confidence', 1.0)
        confidence_scores.append(avg_confidence)
        
        if avg_confidence >= 0.9:
            high_confidence += 1
        elif avg_confidence >= 0.7:
            medium_confidence += 1
        else:
            low_confidence += 1
    
    avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
    
    return {
        'average_context_confidence': avg_confidence,
        'high_confidence_nodes': high_confidence,
        'medium_confidence_nodes': medium_confidence,
        'low_confidence_nodes': low_confidence,
        'total_documented': total_nodes
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <path_to_repository>")
        sys.exit(1)
        
    repository_path = sys.argv[1]
    run_documentation_agent(repository_path)