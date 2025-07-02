# File: agent/agent_nodes.py
#
# This file implements the core logic for each step in the agent's workflow.
# ENHANCED VERSION: Added advanced search, validation, and error handling

import os
import json
import re
from typing import Dict, List, Tuple, Any, Optional
from difflib import SequenceMatcher
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
import networkx as nx
from .agent_state import AgentState
from core.graph_searcher import RepoSearcher

# --- Import all necessary prompts from the centralized templates file ---
from prompts.templates import (
    CODE_ANALYSIS_PROMPT_TEMPLATE,
    DOCUMENTATION_PROMPT_TEMPLATE,
    CONCEPTUAL_GRAPH_PROMPT_TEMPLATE
)


class EnhancedDependencySearcher:
    """Advanced searcher for finding dependencies in the code graph"""
    
    def __init__(self, graph: nx.MultiDiGraph):
        self.graph = graph
        self.searcher = RepoSearcher(graph)
        # Build search indices for faster lookups
        self._build_search_indices()
    
    def _build_search_indices(self):
        """Build various indices for efficient searching"""
        self.name_index = {}  # Maps lowercase names to actual node names
        self.file_index = {}  # Maps file paths to nodes
        self.method_index = {}  # Maps method names to their full qualified names
        
        for node, data in self.graph.nodes(data=True):
            # Name index
            self.name_index[node.lower()] = node
            
            # File index
            fname = data.get('fname', '')
            if fname:
                if fname not in self.file_index:
                    self.file_index[fname] = []
                self.file_index[fname].append(node)
            
            # Method index for class.method patterns
            if '.' in node:
                parts = node.split('.')
                method_name = parts[-1]
                if method_name not in self.method_index:
                    self.method_index[method_name] = []
                self.method_index[method_name].append(node)
    
    def search_dependency(self, dep_name: str) -> List[Dict[str, Any]]:
        """
        Search for a dependency using multiple strategies.
        Returns list of potential matches with confidence scores.
        """
        results = []
        
        # Strategy 1: Exact match
        if self.graph.has_node(dep_name):
            results.append({
                'node': dep_name,
                'confidence': 1.0,
                'strategy': 'exact_match',
                'data': self.graph.nodes[dep_name]
            })
            return results
        
        # Strategy 2: Case-insensitive match
        lower_dep = dep_name.lower()
        if lower_dep in self.name_index:
            actual_name = self.name_index[lower_dep]
            results.append({
                'node': actual_name,
                'confidence': 0.95,
                'strategy': 'case_insensitive',
                'data': self.graph.nodes[actual_name]
            })
        
        # Strategy 3: Partial match with fuzzy matching
        for node in self.graph.nodes():
            similarity = SequenceMatcher(None, dep_name.lower(), node.lower()).ratio()
            if similarity > 0.8:  # High similarity threshold
                results.append({
                    'node': node,
                    'confidence': similarity,
                    'strategy': 'fuzzy_match',
                    'data': self.graph.nodes[node]
                })
        
        # Strategy 4: Method name search (for unqualified method calls)
        if dep_name in self.method_index:
            for full_name in self.method_index[dep_name]:
                results.append({
                    'node': full_name,
                    'confidence': 0.7,
                    'strategy': 'method_match',
                    'data': self.graph.nodes[full_name]
                })
        
        # Strategy 5: Import alias resolution
        common_aliases = {
            'np': 'numpy',
            'pd': 'pandas',
            'plt': 'matplotlib.pyplot',
            'tf': 'tensorflow',
            'nn': 'torch.nn'
        }
        if dep_name in common_aliases:
            results.append({
                'node': None,
                'confidence': 0.9,
                'strategy': 'known_alias',
                'data': {'external': True, 'actual_name': common_aliases[dep_name]}
            })
        
        # Sort results by confidence
        results.sort(key=lambda x: x['confidence'], reverse=True)
        return results[:5]  # Return top 5 matches


def initialize_documentation_queue(state: AgentState) -> dict:
    """
    Initializes the agent's state by identifying all "leaf" nodes and
    setting up the master tracking set.
    """
    print("--- Initializing Documentation Queue ---")
    repo_graph = state['repo_graph']
    all_nodes = set(repo_graph.nodes())
    
    leaf_nodes = [node for node in repo_graph.nodes() if repo_graph.out_degree(node) == 0]

    print(f"Found {len(leaf_nodes)} leaf nodes to start with across all components.")
    
    return {
        "nodes_to_process": all_nodes,
        "documented_nodes": {},
        "nodes_to_document": leaf_nodes,
        "is_finished": False,
    }

def select_next_node(state: AgentState) -> dict:
    """
    Selects the next node to document from the queue.
    """
    print("\n--- Selecting Next Node to Document ---")
    
    nodes_to_document = state['nodes_to_document']
    
    if not nodes_to_document:
        print("Primary queue is empty. Checking for remaining undocumented nodes...")
        remaining_nodes = state['nodes_to_process'] - set(state['documented_nodes'].keys())
        if not remaining_nodes:
            print("No remaining nodes to document.")
            return {"is_finished": True}
        
        next_node_name = list(remaining_nodes)[0]
        print(f"Force-selecting '{next_node_name}' to break a cycle or start a new component.")
    else:
        next_node_name = nodes_to_document.pop(0)

    node_info = state['repo_graph'].nodes[next_node_name]
    print(f"Selected: '{next_node_name}' (Category: {node_info.get('category')})")

    return {
        "current_node_name": next_node_name,
        "current_node_info": node_info,
        "nodes_to_document": nodes_to_document,
    }

def gather_documentation_context(state: AgentState) -> dict:
    """
    ENHANCED VERSION: Analyzes the current node's code to find all dependencies,
    then gathers context for them using advanced search strategies.
    """
    if state.get("is_finished"):
        return {}
    
    current_node_name = state['current_node_name']
    current_node_info = state['current_node_info']
    repo_graph = state['repo_graph']
    documented_nodes = state['documented_nodes']
    
    print(f"\n{'='*60}")
    print(f"ENHANCED CONTEXT GATHERING FOR: '{current_node_name}'")
    print(f"{'='*60}")
    
    # Initialize enhanced searcher
    enhanced_searcher = EnhancedDependencySearcher(repo_graph)
    
    # Step A: Use an LLM to find out what functions/classes are being called.
    print("\n[STEP A] Analyzing code to identify dependencies...")
    llm = AzureChatOpenAI(deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"), temperature=0.0, max_tokens=1024)
    prompt = PromptTemplate.from_template(CODE_ANALYSIS_PROMPT_TEMPLATE)
    chain = prompt | llm | JsonOutputParser()
    
    dependencies = []
    try:
        analysis_result = chain.invoke({
            "source_code": current_node_info.get('info', '')
        })
        
        # Handle different response formats
        if isinstance(analysis_result, list):
            dependencies = analysis_result
        elif isinstance(analysis_result, dict) and 'dependencies' in analysis_result:
            dependencies = analysis_result['dependencies']
        else:
            dependencies = []
            
        print(f"✓ Identified {len(dependencies)} dependencies: {dependencies}")
        
    except Exception as e:
        print(f"✗ Error in dependency analysis: {str(e)}")
        print("  Attempting fallback regex-based extraction...")
        
        # Fallback: Simple regex-based extraction
        source_code = current_node_info.get('info', '')
        patterns = [
            r'(\w+)\s*\(',  # Function calls
            r'(\w+\.\w+)\s*\(',  # Method calls
            r'(\w+)\s*=\s*(\w+)\(',  # Assignments with calls
            r'from\s+\w+\s+import\s+(\w+)',  # Imports
            r'import\s+(\w+)'  # Direct imports
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, source_code)
            dependencies.extend([m if isinstance(m, str) else m[-1] for m in matches])
        
        # Remove duplicates and filter out common keywords
        keywords = {'self', 'def', 'class', 'return', 'if', 'else', 'for', 'while', 'in', 'and', 'or', 'not'}
        dependencies = list(set(dep for dep in dependencies if dep not in keywords))
        print(f"✓ Fallback extraction found {len(dependencies)} potential dependencies")

    # Step B & C: Check for existing documentation and fetch missing info using enhanced search
    print("\n[STEP B & C] Verifying context and fetching missing information...")
    context_str = ""
    available_context = {}
    search_required = []
    
    # First check what's immediately available
    for dep_name in dependencies:
        if dep_name in documented_nodes:
            print(f"  ✓ '{dep_name}' - Found in documented nodes")
            available_context[dep_name] = {
                'source': 'documented',
                'content': documented_nodes[dep_name],
                'confidence': 1.0
            }
        elif repo_graph.has_node(dep_name):
            print(f"  ✓ '{dep_name}' - Found in repository graph")
            available_context[dep_name] = {
                'source': 'graph',
                'content': repo_graph.nodes[dep_name],
                'confidence': 1.0
            }
        else:
            print(f"  ✗ '{dep_name}' - Not found, search required")
            search_required.append(dep_name)
    
    # Enhanced search for missing dependencies
    if search_required:
        print(f"\n[ENHANCED SEARCH] Searching for {len(search_required)} missing dependencies...")
        
        for dep_name in search_required:
            print(f"\n  🔍 Searching for '{dep_name}'...")
            search_results = enhanced_searcher.search_dependency(dep_name)
            
            if search_results:
                best_match = search_results[0]
                print(f"    ✓ Found match: {best_match['node']} "
                      f"(confidence: {best_match['confidence']:.2f}, "
                      f"strategy: {best_match['strategy']})")
                
                if best_match['node']:  # Internal dependency found
                    available_context[dep_name] = {
                        'source': f"search_{best_match['strategy']}",
                        'content': best_match['data'],
                        'actual_name': best_match['node'],
                        'confidence': best_match['confidence']
                    }
                else:  # External dependency
                    available_context[dep_name] = {
                        'source': 'external',
                        'content': best_match['data'],
                        'confidence': best_match['confidence']
                    }
                
                # Show alternative matches if any
                if len(search_results) > 1:
                    print("    Alternative matches:")
                    for alt in search_results[1:3]:  # Show up to 2 alternatives
                        print(f"      - {alt['node']} (confidence: {alt['confidence']:.2f})")
            else:
                print(f"    ✗ No matches found - marking as external/unknown")
                available_context[dep_name] = {
                    'source': 'external',
                    'content': None,
                    'confidence': 0.0
                }
    
    # Step D: Compile comprehensive context with metadata
    print("\n[STEP D] Compiling comprehensive context for documentation...")
    
    context_metadata = {
        'total_dependencies': len(dependencies),
        'found': {
            'documented': sum(1 for v in available_context.values() if v['source'] == 'documented'),
            'graph': sum(1 for v in available_context.values() if v['source'] == 'graph'),
            'search': sum(1 for v in available_context.values() if v['source'].startswith('search_')),
            'external': sum(1 for v in available_context.values() if v['source'] == 'external')
        },
        'confidence_scores': [],
        'average_confidence': 1.0
    }
    
    # Build context string
    if not dependencies:
        context_str = "This node has no identified internal dependencies."
    else:
        for dep_name, dep_info in available_context.items():
            confidence = dep_info.get('confidence', 1.0)
            context_metadata['confidence_scores'].append(confidence)
            context_block = ""
            
            if dep_info['source'] == 'documented':
                context_block = f"### Dependency: `{dep_name}` [Documented]\n\n{dep_info['content']}\n\n---\n\n"
            elif dep_info['source'] == 'graph':
                dep_data = dep_info['content']
                dep_code = dep_data.get('info', '# Source code not available')
                dep_docstring = dep_data.get('docstring', 'No docstring available.')
                context_block = (
                    f"### Dependency: `{dep_name}` [From Source]\n\n"
                    f"**Docstring:**\n```\n{dep_docstring}\n```\n\n"
                    f"**Source Code:**\n```python\n{dep_code}\n```\n\n---\n\n"
                )
            elif dep_info['source'].startswith('search_'):
                actual_name = dep_info.get('actual_name', dep_name)
                dep_data = dep_info['content']
                strategy = dep_info['source'].replace('search_', '').replace('_', ' ').title()
                context_block = (
                    f"### Dependency: `{dep_name}` → `{actual_name}` [Found via {strategy}] (Confidence: {confidence:.0%})\n\n"
                    f"**Docstring:**\n```\n{dep_data.get('docstring', 'No docstring available.')}\n```\n\n"
                    f"**Source Code:**\n```python\n{dep_data.get('info', '# Source code not available')}\n```\n\n---\n\n"
                )
            else:  # external
                actual_name = dep_info.get('content', {}).get('actual_name', dep_name) if dep_info.get('content') else dep_name
                context_block = f"### Dependency: `{dep_name}` [External Library]\n\n"
                context_block += f"This appears to be an external library"
                if actual_name != dep_name:
                    context_block += f" (likely `{actual_name}`)"
                context_block += ".\n\n---\n\n"
            
            context_str += context_block
    
    # Calculate average confidence
    if context_metadata['confidence_scores']:
        context_metadata['average_confidence'] = sum(context_metadata['confidence_scores']) / len(context_metadata['confidence_scores'])
    
    # Print summary
    print(f"\n📊 Context Gathering Summary:")
    print(f"  - Total Dependencies: {context_metadata['total_dependencies']}")
    print(f"  - Documented: {context_metadata['found']['documented']}")
    print(f"  - From Graph: {context_metadata['found']['graph']}")
    print(f"  - Via Search: {context_metadata['found']['search']}")
    print(f"  - External: {context_metadata['found']['external']}")
    print(f"  - Average Confidence: {context_metadata['average_confidence']:.1%}")
    print(f"{'='*60}\n")
    
    return {
        "context_for_llm": context_str,
        "context_metadata": context_metadata
    }


def generate_documentation(state: AgentState) -> dict:
    """
    Invokes the LLM to generate documentation for the current node.
    ENHANCED: Now includes context quality indicators in documentation.
    """
    if state.get("is_finished"): return {}
    print(f"--- Generating Documentation for '{state['current_node_name']}' ---")
    
    node_info = state['current_node_info']
    context_metadata = state.get('context_metadata', {})
    
    # Add quality warning if confidence is low
    quality_note = ""
    if context_metadata.get('average_confidence', 1.0) < 0.7:
        quality_note = "\n> ⚠️ **Note**: Some dependencies could not be fully resolved. Documentation may be incomplete.\n"
    
    llm = AzureChatOpenAI(deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"), temperature=0.2, max_tokens=1024)
    prompt = PromptTemplate.from_template(DOCUMENTATION_PROMPT_TEMPLATE)
    chain = prompt | llm | StrOutputParser()
    
    print("Invoking LLM for documentation...")
    generated_doc = chain.invoke({
        "node_name": state['current_node_name'],
        "node_category": node_info.get('category', 'N/A'),
        "node_fname": node_info.get('fname', 'N/A'),
        "node_line_start": node_info.get('line', [0, 0])[0],
        "node_line_end": node_info.get('line', [0, 0])[1],
        "node_docstring": node_info.get('docstring', 'Not available.'),
        "dependencies_context": state['context_for_llm'],
        "source_code": node_info.get('info', '# Source code not available')
    })
    
    # Prepend quality note if needed
    if quality_note:
        generated_doc = quality_note + generated_doc
    
    documented_nodes = state['documented_nodes']
    documented_nodes[state['current_node_name']] = generated_doc
    
    return {"documented_nodes": documented_nodes}

def generate_conceptual_graph_data(state: AgentState) -> dict:
    """
    Builds the conceptual graph by merging AST metadata with LLM-generated
    semantic metadata for the current node.
    ENHANCED: Now includes confidence scores in relationships.
    """
    if state.get("is_finished"): return {}
    current_node = state['current_node_name']
    print(f"--- Generating Conceptual Graph Data for '{current_node}' ---")

    context_metadata = state.get('context_metadata', {})
    
    llm = AzureChatOpenAI(deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"), temperature=0.0, max_tokens=1024)
    prompt = PromptTemplate.from_template(CONCEPTUAL_GRAPH_PROMPT_TEMPLATE)
    chain = prompt | llm | JsonOutputParser()

    print("Invoking LLM for conceptual analysis...")
    
    final_output_data = state['final_output_data']
    
    try:
        response_data = chain.invoke({
            "node_name": current_node,
            "documentation": state['documented_nodes'][current_node],
            "dependencies_context": state['context_for_llm'],
            "source_code": state['current_node_info'].get('info', '# Source code not available')
        })

        conceptual_graph = state['conceptual_graph']
        
        base_metadata = state['repo_graph'].nodes[current_node]
        semantic_metadata = response_data.get('semantic_metadata', {})
        
        # Add context quality to metadata
        semantic_metadata['context_confidence'] = context_metadata.get('average_confidence', 1.0)
        
        if not conceptual_graph.has_node(current_node):
            conceptual_graph.add_node(current_node, **base_metadata)
        
        nx.set_node_attributes(conceptual_graph, {current_node: semantic_metadata})

        for edge in response_data.get('semantic_edges', []):
            target_node = edge.get('target')
            if target_node and conceptual_graph.has_node(target_node):
                conceptual_graph.add_edge(current_node, target_node, label=edge.get('label', 'RELATED_TO'))

        final_output_data[current_node] = {
            'documentation': state['documented_nodes'][current_node],
            'conceptual_data': response_data,
            'context_metadata': context_metadata
        }
    except Exception as e:
        print(f"Warning: Failed to process conceptual data for node '{current_node}': {e}")
        final_output_data[current_node] = {
            'documentation': state['documented_nodes'][current_node],
            'conceptual_data': {"error": str(e)},
            'context_metadata': context_metadata
        }

    return {
        "conceptual_graph": conceptual_graph,
        "final_output_data": final_output_data
    }

def update_documentation_queue(state: AgentState) -> dict:
    """
    Updates the documentation queue with new nodes that are now ready.
    """
    if state.get("is_finished"): return {}
    current_node = state['current_node_name']
    print(f"--- Updating Queue after processing '{current_node}' ---")

    searcher = RepoSearcher(graph=state['repo_graph'])
    potential_new_nodes = searcher.get_references(current_node)

    nodes_to_document = state['nodes_to_document']
    documented_nodes = state['documented_nodes']
    
    for node in potential_new_nodes:
        if node in documented_nodes or node in nodes_to_document:
            continue 

        dependencies = searcher.get_dependencies(node)
        if all(dep in documented_nodes for dep in dependencies):
            print(f"New node ready for documentation: '{node}'")
            nodes_to_document.append(node)
            
    return {"nodes_to_document": nodes_to_document}

def should_continue(state: AgentState) -> str:
    """
    Determines whether the agent should continue its work.
    """
    if state.get("is_finished"):
        return "end"
        
    num_documented = len(state['documented_nodes'])
    num_total = len(state['nodes_to_process'])
    
    print(f"--- Progress Check: {num_documented} / {num_total} nodes documented. ---")
    
    if num_documented < num_total:
        return "continue"
    else:
        print("\n--- All nodes have been documented. Agent is finished. ---")
        return "end"