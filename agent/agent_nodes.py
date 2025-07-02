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
        """
        Builds multiple indices to enable efficient searching of nodes in the graph by name, file, or method.

        This method creates three indices:
        - name_index: Maps lowercase node names to their actual names for case-insensitive lookup.
        - file_index: Maps file paths to lists of node names defined in each file.
        - method_index: Maps method names to lists of their fully qualified names (e.g., ClassName.method).

        For each node in the graph:
            - Adds an entry to name_index using the lowercase node name.
            - Adds the node to file_index under its file path, if available.
            - If the node name contains a dot ('.'), treats it as a method and adds it to method_index under the method name.

        This indexing supports fast lookups for search, navigation, and analysis tasks.

        Example:
            self._build_search_indices()
            node = self.name_index.get('myfunction')
            nodes_in_file = self.file_index.get('utils.py')
            qualified_methods = self.method_index.get('run')

        Returns:
            None
        """
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
        Searches for a dependency node in the graph using multiple strategies and returns a list of potential matches with confidence scores.

        The search is performed in the following order:
        1. Exact match: Checks if the dependency name exactly matches a node in the graph.
        2. Case-insensitive match: Looks for a node name that matches the dependency name, ignoring case.
        3. Fuzzy match: Uses SequenceMatcher to find nodes with high similarity to the dependency name.
        4. Method name search: Finds nodes that match the dependency as a method name (for unqualified method calls).
        5. Import alias resolution: Recognizes common import aliases (e.g., 'np' for 'numpy') and maps them to their actual package names.

        For each matching strategy, a dictionary is added to the results list containing:
            - 'node': The matched node name or None for external dependencies.
            - 'confidence': A float score indicating the confidence of the match.
            - 'strategy': The name of the matching strategy used.
            - 'data': Additional data about the node or dependency.

        The results are sorted by confidence in descending order, and the top 5 matches are returned.

        Args:
            dep_name (str): The name of the dependency to search for.

        Returns:
            List[Dict[str, Any]]: A list of up to 5 dictionaries, each describing a potential match with confidence and metadata.
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
    Selects the next node to document from the queue or remaining nodes.

    This function manages the process of determining which code node should be documented next.
    It first checks the primary queue (`nodes_to_document`). If the queue is empty, it looks for
    any remaining undocumented nodes in the repository graph and selects one to break cycles or
    start a new component. The function prints informative messages about its decision process.

    Steps:
    1. Prints a header indicating the selection process has started.
    2. Retrieves the current queue of nodes to document from the agent state.
    3. If the queue is empty:
        a. Prints a message and computes the set of remaining undocumented nodes.
        b. If there are no remaining nodes, prints a message and returns a flag indicating completion.
        c. Otherwise, selects the first remaining node to continue processing and prints its name.
    4. If the queue is not empty, pops the next node from the queue.
    5. Retrieves information about the selected node from the repository graph.
    6. Prints the selected node and its category.
    7. Returns a dictionary containing the selected node's name, its info, and the updated queue.

    Args:
        state (AgentState): The current agent state, including queues and the repository graph.

    Returns:
        dict: A dictionary with keys:
            - "current_node_name": The name of the node selected for documentation.
            - "current_node_info": Metadata about the selected node.
            - "nodes_to_document": The updated queue of nodes to document.
            - If finished, returnscts the next node to document from the queue.
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
    Gathers and compiles context for documenting the current code node, including advanced dependency analysis and confidence scoring.

    Steps:
    1. Checks if the documentation process is finished; if so, returns an empty dictionary.
    2. Retrieves the current node's name, info, the repository graph, and already documented nodes from the state.
    3. Initializes an EnhancedDependencySearcher for advanced dependency lookups.
    4. Uses an LLM (or a regex fallback) to analyze the current node's code and identify dependencies.
        - If the LLM fails, falls back to regex-based extraction.
        - Filters out common Python keywords from dependencies.
    5. For each dependency:
        - If already documented, adds its content to the context.
        - If present in the repo graph, adds its node data to the context.
        - Otherwise, marks it for enhanced search.
    6. For dependencies not found, uses EnhancedDependencySearcher to find the best match and adds the result to the context, including confidence and strategy.
    7. Compiles a context string for the LLM, including docstrings, code, or external library notes for each dependency.
    8. Calculates and records confidence scores and metadata about the context gathering process.
    9. Prints a summary of the context gathering results, including counts and average confidence.
    10. Returns a dictionary containing:
        - "context_for_llm": The compiled context string for use in documentation generation.
        - "context_metadata": Metadata including dependency counts, sources, and confidence scores.

    Args:
        state (AgentState): The current agent state, including the node to document, the repo graph, and documented nodes.

    Returns:
        dict: {
            "context_for_llm": str,  # Markdown-formatted context for the LLM
            "context_metadata": dict # Metadata about dependencies and confidence
        }
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
        'each_dependencies': dependencies,
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
    ### Dependency Adding
    dependencies = context_metadata.get('each_dependencies', [])
    if not dependencies and 'context_for_llm' in state:
        # Optionally, extract dependency names from the context string if not present in metadata
        # (You may want to explicitly pass the dependency list in gather_documentation_context)
        dependencies = []  # fallback: leave empty or parse from context string if needed

    dependencies_section = ""
    if dependencies:
        dependencies_section = "\n**Dependencies:**\n" + "\n".join(f"- `{dep}`" for dep in dependencies) + "\n"
        
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
        generated_doc = quality_note + dependencies_section + generated_doc
    
    documented_nodes = state['documented_nodes']
    documented_nodes[state['current_node_name']] = generated_doc
    
    return {"documented_nodes": documented_nodes}

def generate_conceptual_graph_data(state: AgentState) -> dict:
    """
    Builds and updates the conceptual graph for the current code node by merging AST metadata with LLM-generated semantic metadata.

    Steps:
    1. Checks if the documentation process is finished; if so, returns an empty dictionary.
    2. Retrieves the current node's name and prints a header for conceptual graph generation.
    3. Gets context metadata from the state for use in confidence scoring.
    4. Initializes an AzureChatOpenAI LLM and prepares a prompt for conceptual graph analysis.
    5. Invokes the LLM to generate semantic metadata and conceptual relationships for the current node.
    6. Retrieves the conceptual graph and base metadata for the current node from the repository graph.
    7. Merges LLM-generated semantic metadata with AST metadata, including context confidence.
    8. Adds the current node to the conceptual graph if not already present.
    9. Sets node attributes in the conceptual graph with the merged metadata.
    10. Iterates over semantic edges returned by the LLM:
        - For each edge, adds an edge to the conceptual graph if the target node exists, using the provided label.
    11. Updates the final output data for the current node with documentation, conceptual data, and context metadata.
    12. Handles exceptions by logging a warning and storing error information in the output data.
    13. Returns the updated conceptual graph and final output data.

    Args:
        state (AgentState): The current agent state, including node information, context, and output data.

    Returns:
        dict: {
            "conceptual_graph": The updated conceptual graph (networkx graph object),
            "final_output_data": The updated output data dictionary for allNCED: Now includes confidence scores in relationships.
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