# File: core/graph_searcher.py
#
# This class provides a suite of tools for querying and traversing the
# repository graph built by `construct_graph.py`. This version is customized
# with specific methods for finding code dependencies and references, which
# are essential for the documentation agent's logic.

import networkx as nx
from typing import List, Dict, Set, Tuple


class RepoSearcher:
    """A class to perform searches and traversals on a repository code graph."""

    def __init__(self, graph: nx.MultiDiGraph):
        """
        Initializes the RepoSearcher with a NetworkX graph.

        Args:
            graph (nx.MultiDiGraph): The repository code graph.
        """
        self.graph = graph

    def get_dependencies(self, node_name: str) -> List[str]:
        """
        Finds all nodes that the given node directly calls or contains.
        This is useful for understanding what a function/class relies on.

        Args:
            node_name (str): The name of the node to find dependencies for.

        Returns:
            List[str]: A list of node names that are successors of the given node.
        """
        if node_name not in self.graph:
            return []
        # Successors are nodes that the current node has an edge pointing TO.
        return list(self.graph.successors(node_name))

    def get_references(self, node_name: str) -> List[str]:
        """
        Finds all nodes that directly call the given node.
        This is useful for understanding how and where a function/class is used.

        Args:
            node_name (str): The name of the node to find references for.

        Returns:
            List[str]: A list of node names that are predecessors of the given node.
        """
        if node_name not in self.graph:
            return []
        # Predecessors are nodes that have an edge pointing FROM them TO the current node.
        return list(self.graph.predecessors(node_name))

    def get_class_methods(self, class_name: str) -> List[str]:
        """
        Finds all methods that belong to a given class.

        Args:
            class_name (str): The name of the class.

        Returns:
            List[str]: A list of method names that belong to the class.
        """
        if class_name not in self.graph:
            return []
        
        methods = []
        for successor in self.graph.successors(class_name):
            # Check if this edge represents a 'contains' relationship
            edge_data = self.graph.get_edge_data(class_name, successor)
            if any(data.get('label') == 'contains' for data in edge_data.values()):
                methods.append(successor)
        return methods

    def get_method_class(self, method_name: str) -> str:
        """
        Finds the class that contains a given method.

        Args:
            method_name (str): The name of the method (can be full name like 'Class.method').

        Returns:
            str: The class name that contains the method, or empty string if not found.
        """
        if method_name not in self.graph:
            return ""
        
        for predecessor in self.graph.predecessors(method_name):
            # Check if this edge represents a 'belongs_to' relationship
            edge_data = self.graph.get_edge_data(method_name, predecessor)
            if any(data.get('label') == 'belongs_to' for data in edge_data.values()):
                return predecessor
        return ""

    def get_inheritance_chain(self, class_name: str) -> List[str]:
        """
        Finds the inheritance chain for a given class.

        Args:
            class_name (str): The name of the class.

        Returns:
            List[str]: A list of classes in the inheritance chain.
        """
        if class_name not in self.graph:
            return []
        
        inheritance_chain = []
        for successor in self.graph.successors(class_name):
            edge_data = self.graph.get_edge_data(class_name, successor)
            if any(data.get('label') == 'inherits_from' for data in edge_data.values()):
                inheritance_chain.append(successor)
        return inheritance_chain

    def get_function_calls(self, node_name: str) -> List[str]:
        """
        Finds all functions that are called by the given node.

        Args:
            node_name (str): The name of the node (function, method, or class).

        Returns:
            List[str]: A list of function names that are called by the node.
        """
        if node_name not in self.graph:
            return []
        
        calls = []
        for successor in self.graph.successors(node_name):
            edge_data = self.graph.get_edge_data(node_name, successor)
            if any(data.get('label') in ['calls', 'invokes'] for data in edge_data.values()):
                calls.append(successor)
        return calls

    def get_module_definitions(self, file_path: str) -> Dict[str, List[str]]:
        """
        Finds all classes and functions defined in a specific module.

        Args:
            file_path (str): The path of the module file.

        Returns:
            Dict[str, List[str]]: A dictionary with 'classes' and 'functions' keys.
        """
        module_node = f"{file_path}::module_code"
        definitions = {'classes': [], 'functions': []}
        
        if module_node not in self.graph:
            return definitions
        
        for successor in self.graph.successors(module_node):
            edge_data = self.graph.get_edge_data(module_node, successor)
            if any(data.get('label') == 'defines' for data in edge_data.values()):
                node_attrs = self.graph.nodes[successor]
                category = node_attrs.get('category', '')
                if category == 'class':
                    definitions['classes'].append(successor)
                elif category == 'function':
                    definitions['functions'].append(successor)
        
        return definitions

    def get_external_dependencies(self, node_name: str) -> List[str]:
        """
        Finds all external dependencies (functions/classes not defined in the codebase).

        Args:
            node_name (str): The name of the node.

        Returns:
            List[str]: A list of external dependencies.
        """
        if node_name not in self.graph:
            return []
        
        external_deps = []
        for successor in self.graph.successors(node_name):
            node_attrs = self.graph.nodes[successor]
            if node_attrs.get('category') in ['external_function', 'external_class']:
                external_deps.append(successor)
        
        return external_deps

    def get_nodes_by_category(self, category: str) -> List[str]:
        """
        Finds all nodes of a specific category.

        Args:
            category (str): The category to search for (e.g., 'class', 'function', 'module_code').

        Returns:
            List[str]: A list of node names matching the category.
        """
        nodes = []
        for node, attrs in self.graph.nodes(data=True):
            if attrs.get('category') == category:
                nodes.append(node)
        return nodes

    def get_node_info(self, node_name: str) -> Dict:
        """
        Gets detailed information about a specific node.

        Args:
            node_name (str): The name of the node.

        Returns:
            Dict: A dictionary containing node attributes.
        """
        if node_name not in self.graph:
            return {}
        return dict(self.graph.nodes[node_name])

    def dfs_traversal(self, start_node: str, depth_limit: int = 5) -> List[str]:
        """
        Performs a depth-first search (DFS) traversal from a starting node.
        Explores as far as possible along each branch before backtracking.

        Args:
            start_node (str): The node to begin the traversal from.
            depth_limit (int): The maximum depth to explore.

        Returns:
            List[str]: A list of visited nodes in the order they were discovered.
        """
        if start_node not in self.graph:
            return []
            
        visited = []
        stack = [(start_node, 0)]
        while stack:
            node, level = stack.pop()
            if node not in visited:
                visited.append(node)
                if level < depth_limit:
                    # We reverse the neighbors to maintain a more intuitive
                    # left-to-right exploration order from the original source code.
                    neighbors = reversed(list(self.graph.successors(node)))
                    for neighbor in neighbors:
                        if neighbor not in visited:
                            stack.append((neighbor, level + 1))
        return visited

    def bfs_traversal(self, start_node: str, depth_limit: int = 5) -> List[str]:
        """
        Performs a breadth-first search (BFS) traversal from a starting node.
        Explores all neighbors at the present depth prior to moving on to nodes
        at the next depth level.

        Args:
            start_node (str): The node to begin the traversal from.
            depth_limit (int): The maximum depth to explore.

        Returns:
<<<<<<< HEAD
            list[str]: A list of visited nodes in the order they were discovered.
=======
            List[str]: A list of visited nodes in the order they were discovered.
>>>>>>> f6061b0228250a53c82190181e85a5683699240a
        """
        if start_node not in self.graph:
            return []

        visited = []
        queue = [(start_node, 0)]
        
        while queue:
            node, level = queue.pop(0)
            if node not in visited:
                visited.append(node)
                if level < depth_limit:
                    for neighbor in self.graph.successors(node):
                        if neighbor not in visited:
                            queue.append((neighbor, level + 1))
        return visited

    def find_shortest_path(self, source: str, target: str) -> List[str]:
        """
        Finds the shortest path between two nodes in the graph.

        Args:
            source (str): The source node name.
            target (str): The target node name.

        Returns:
            List[str]: A list of nodes representing the shortest path, or empty list if no path exists.
        """
        if source not in self.graph or target not in self.graph:
            return []
        
        try:
            return nx.shortest_path(self.graph, source, target)
        except nx.NetworkXNoPath:
            return []

    def get_connected_components(self) -> List[List[str]]:
        """
        Finds all connected components in the graph.

        Returns:
            List[List[str]]: A list of connected components, where each component is a list of node names.
        """
        # Convert to undirected graph for connected components analysis
        undirected = self.graph.to_undirected()
        return [list(component) for component in nx.connected_components(undirected)]

    def get_graph_statistics(self) -> Dict[str, int]:
        """
        Provides various statistics about the graph structure.

        Returns:
            Dict[str, int]: A dictionary containing graph statistics.
        """
        stats = {
            'total_nodes': len(self.graph.nodes()),
            'total_edges': len(self.graph.edges()),
            'classes': len(self.get_nodes_by_category('class')),
            'functions': len(self.get_nodes_by_category('function')),
            'methods': len(self.get_nodes_by_category('method')),
            'module_code_blocks': len(self.get_nodes_by_category('module_code')),
            'external_functions': len(self.get_nodes_by_category('external_function')),
            'external_classes': len(self.get_nodes_by_category('external_class')),
            'connected_components': len(self.get_connected_components())
        }
        return stats

    def get_edge_types_summary(self) -> Dict[str, int]:
        """
        Provides a summary of different edge types in the graph.

        Returns:
            Dict[str, int]: A dictionary mapping edge labels to their counts.
        """
        edge_types = {}
        for _, _, attrs in self.graph.edges(data=True):
            label = attrs.get('label', 'unknown')
            edge_types[label] = edge_types.get(label, 0) + 1
        return edge_types

    def find_circular_dependencies(self) -> List[List[str]]:
        """
        Finds circular dependencies in the graph.

        Returns:
            List[List[str]]: A list of cycles, where each cycle is a list of node names.
        """
        try:
            cycles = list(nx.simple_cycles(self.graph))
            return cycles
        except:
            return []

    def get_most_connected_nodes(self, top_n: int = 10) -> List[Tuple[str, int]]:
        """
        Finds the most connected nodes in the graph (highest degree).

        Args:
            top_n (int): Number of top nodes to return.

        Returns:
            List[Tuple[str, int]]: A list of tuples (node_name, degree) sorted by degree.
        """
        degrees = [(node, self.graph.degree(node)) for node in self.graph.nodes()]
        return sorted(degrees, key=lambda x: x[1], reverse=True)[:top_n]

    def get_leaf_nodes(self) -> List[str]:
        """
        Finds all leaf nodes (nodes with no outgoing edges).

        Returns:
            List[str]: A list of leaf node names.
        """
        return [node for node in self.graph.nodes() if self.graph.out_degree(node) == 0]

    def get_root_nodes(self) -> List[str]:
        """
        Finds all root nodes (nodes with no incoming edges).

        Returns:
            List[str]: A list of root node names.
        """
        return [node for node in self.graph.nodes() if self.graph.in_degree(node) == 0]

    def search_nodes_by_pattern(self, pattern: str, search_in: str = 'name') -> List[str]:
        """
        Searches for nodes matching a specific pattern.

        Args:
            pattern (str): The pattern to search for (supports partial matching).
            search_in (str): What to search in ('name', 'docstring', 'info', or 'all').

        Returns:
            List[str]: A list of matching node names.
        """
        matching_nodes = []
        pattern_lower = pattern.lower()
        
        for node, attrs in self.graph.nodes(data=True):
            if search_in == 'name' or search_in == 'all':
                if pattern_lower in node.lower():
                    matching_nodes.append(node)
                    continue
            
            if search_in == 'docstring' or search_in == 'all':
                docstring = attrs.get('docstring', '').lower()
                if pattern_lower in docstring:
                    matching_nodes.append(node)
                    continue
            
            if search_in == 'info' or search_in == 'all':
                info = attrs.get('info', '').lower()
                if pattern_lower in info:
                    matching_nodes.append(node)
                    continue
        
        return matching_nodes

    def get_dependency_depth(self, node_name: str, max_depth: int = 10) -> Dict[str, int]:
        """
        Calculates the dependency depth for all reachable nodes from a given node.

        Args:
            node_name (str): The starting node name.
            max_depth (int): Maximum depth to explore.

        Returns:
            Dict[str, int]: A dictionary mapping node names to their depth from the starting node.
        """
        if node_name not in self.graph:
            return {}
        
        depths = {node_name: 0}
        queue = [(node_name, 0)]
        
        while queue:
            current_node, current_depth = queue.pop(0)
            
            if current_depth < max_depth:
                for successor in self.graph.successors(current_node):
                    if successor not in depths:
                        depths[successor] = current_depth + 1
                        queue.append((successor, current_depth + 1))
        
        return depths

    def calculate_connection_strength(self, node1: str, node2: str) -> Dict[str, float]:
        """
        Calculate connection strength between two nodes using multiple metrics.
        
        Args:
            node1 (str): First node
            node2 (str): Second node
            
        Returns:
            Dict[str, float]: Connection strength metrics
        """
        if node1 not in self.graph or node2 not in self.graph:
            return {'direct': 0.0, 'indirect': 0.0, 'semantic': 0.0, 'overall': 0.0}
        
        metrics = {}
        
        # Direct connection strength
        metrics['direct'] = self._calculate_direct_strength(node1, node2)
        
        # Indirect connection strength (shortest path)
        metrics['indirect'] = self._calculate_indirect_strength(node1, node2)
        
        # Semantic similarity
        metrics['semantic'] = self._calculate_semantic_strength(node1, node2)
        
        # Overall weighted score
        metrics['overall'] = (
            0.5 * metrics['direct'] + 
            0.3 * metrics['indirect'] + 
            0.2 * metrics['semantic']
        )
        
        return metrics
    
    def _calculate_direct_strength(self, node1: str, node2: str) -> float:
        """Calculate direct connection strength based on edge types and weights."""
        if not self.graph.has_edge(node1, node2):
            return 0.0
        
        edge_weights = {
            'calls': 1.0,
            'inherits_from': 0.9,
            'contains': 0.8,
            'uses': 0.7,
            'references': 0.6,
            'invokes': 0.5
        }
        
        max_strength = 0.0
        for edge_data in self.graph[node1][node2].values():
            label = edge_data.get('label', 'unknown')
            weight = edge_weights.get(label, 0.3)
            max_strength = max(max_strength, weight)
        
        return max_strength
    
    def _calculate_indirect_strength(self, node1: str, node2: str) -> float:
        """Calculate indirect connection strength based on shortest path."""
        try:
            path_length = nx.shortest_path_length(self.graph, node1, node2)
            if path_length == 1:
                return 1.0
            elif path_length <= 3:
                return 1.0 / path_length
            else:
                return 0.1
        except nx.NetworkXNoPath:
            return 0.0
    
    def _calculate_semantic_strength(self, node1: str, node2: str) -> float:
        """Calculate semantic similarity based on node attributes."""
        node1_attrs = self.graph.nodes[node1]
        node2_attrs = self.graph.nodes[node2]
        
        similarity = 0.0
        
        # Same file bonus
        if node1_attrs.get('fname') == node2_attrs.get('fname'):
            similarity += 0.3
        
        # Same category bonus
        if node1_attrs.get('category') == node2_attrs.get('category'):
            similarity += 0.2
        
        # Docstring similarity (basic keyword matching)
        doc1 = node1_attrs.get('docstring', '').lower()
        doc2 = node2_attrs.get('docstring', '').lower()
        if doc1 and doc2:
            words1 = set(doc1.split())
            words2 = set(doc2.split())
            if words1 and words2:
                jaccard = len(words1 & words2) / len(words1 | words2)
                similarity += 0.5 * jaccard
        
        return min(similarity, 1.0)
    
    def get_node_relationship_matrix(self, nodes: List[str] = None) -> Dict[str, Dict[str, float]]:
        """
        Build comprehensive node relationship matrix with connection strengths.
        
        Args:
            nodes (List[str]): Specific nodes to analyze, or None for all nodes
            
        Returns:
            Dict[str, Dict[str, float]]: Matrix of connection strengths
        """
        if nodes is None:
            nodes = list(self.graph.nodes())
        
        matrix = {}
        for node1 in nodes:
            matrix[node1] = {}
            for node2 in nodes:
                if node1 != node2:
                    strength = self.calculate_connection_strength(node1, node2)
                    matrix[node1][node2] = strength['overall']
                else:
                    matrix[node1][node2] = 1.0
        
        return matrix
    
    def get_enhanced_graph_statistics(self) -> Dict[str, Any]:
        """Enhanced graph statistics with connection analysis."""
        basic_stats = self.get_graph_statistics()
        
        # Add connection strength analysis
        connection_strengths = []
        for node1 in self.graph.nodes():
            for node2 in self.graph.successors(node1):
                strength = self.calculate_connection_strength(node1, node2)
                connection_strengths.append(strength['overall'])
        
        enhanced_stats = {
            **basic_stats,
            'connection_analysis': {
                'avg_connection_strength': sum(connection_strengths) / len(connection_strengths) if connection_strengths else 0,
                'max_connection_strength': max(connection_strengths) if connection_strengths else 0,
                'min_connection_strength': min(connection_strengths) if connection_strengths else 0,
                'total_connections_analyzed': len(connection_strengths)
            }
        }
        
        return enhanced_stats    