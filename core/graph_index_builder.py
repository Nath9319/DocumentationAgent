# File: core/graph_index_builder.py

import networkx as nx
from typing import Dict, List, Set, Tuple, Optional, Any
from collections import defaultdict
import json
import pickle
from scipy.spatial import KDTree
import heapq
from collections import deque


class GraphIndexBuilder:
    """
    Builds efficient indices for graph operations including node lookup,
    edge weight indexing, and connection path caching.
    """
    
    def __init__(self, graph: nx.MultiDiGraph):
        self.graph = graph
        self.node_indices = {}
        self.edge_indices = {}
        self.path_cache = {}
        self._build_all_indices()
    
    def _build_all_indices(self):
        """Build all types of indices."""
        self._build_node_lookup_indices()
        self._build_edge_weight_indices()
        self._build_connection_path_cache()
    
    def _build_node_lookup_indices(self):
        """Create efficient node lookup indices."""
        # Category index
        self.node_indices['by_category'] = defaultdict(list)
        
        # File index
        self.node_indices['by_file'] = defaultdict(list)
        
        # Name pattern index (for fuzzy search)
        self.node_indices['by_name_pattern'] = defaultdict(list)
        
        # Line number index
        self.node_indices['by_line_range'] = defaultdict(list)
        
        # Docstring keyword index
        self.node_indices['by_docstring_keywords'] = defaultdict(set)
        
        for node, attrs in self.graph.nodes(data=True):
            # Category indexing
            category = attrs.get('category', 'unknown')
            self.node_indices['by_category'][category].append(node)
            
            # File indexing
            fname = attrs.get('fname', '')
            if fname:
                self.node_indices['by_file'][fname].append(node)
            
            # Name pattern indexing (for fuzzy matching)
            node_lower = node.lower()
            for i in range(len(node_lower)):
                for j in range(i + 2, len(node_lower) + 1):
                    pattern = node_lower[i:j]
                    self.node_indices['by_name_pattern'][pattern].append(node)
            
            # Line range indexing
            line_info = attrs.get('line', [0, 0])
            if isinstance(line_info, (list, tuple)) and len(line_info) >= 2:
                start_line, end_line = line_info[0], line_info[1]
                line_range = f"{fname}:{start_line}-{end_line}"
                self.node_indices['by_line_range'][line_range].append(node)
            
            # Docstring keyword indexing
            docstring = attrs.get('docstring', '')
            if docstring:
                keywords = self._extract_keywords(docstring)
                for keyword in keywords:
                    self.node_indices['by_docstring_keywords'][keyword].add(node)
    
    def _build_edge_weight_indices(self):
        """Implement edge weight indexing for fast relationship queries."""
        # Edge type index
        self.edge_indices['by_type'] = defaultdict(list)
        
        # Weight range index
        self.edge_indices['by_weight_range'] = defaultdict(list)
        
        # Source node index
        self.edge_indices['by_source'] = defaultdict(list)
        
        # Target node index
        self.edge_indices['by_target'] = defaultdict(list)
        
        # Edge weights (calculated or default)
        edge_type_weights = {
            'calls': 1.0,
            'inherits_from': 0.9,
            'contains': 0.8,
            'belongs_to': 0.8,
            'uses': 0.7,
            'references': 0.6,
            'invokes': 0.5,
            'defines': 0.4
        }
        
        for source, target, edge_data in self.graph.edges(data=True):
            edge_type = edge_data.get('label', 'unknown')
            weight = edge_type_weights.get(edge_type, 0.3)
            
            edge_info = {
                'source': source,
                'target': target,
                'type': edge_type,
                'weight': weight,
                'data': edge_data
            }
            
            # Index by type
            self.edge_indices['by_type'][edge_type].append(edge_info)
            
            # Index by weight range
            weight_range = self._get_weight_range(weight)
            self.edge_indices['by_weight_range'][weight_range].append(edge_info)
            
            # Index by source and target
            self.edge_indices['by_source'][source].append(edge_info)
            self.edge_indices['by_target'][target].append(edge_info)
    
    def _build_connection_path_cache(self, max_depth: int = 4):
        """Build connection path cache for frequent path queries."""
        # Cache shortest paths between frequently connected nodes
        high_degree_nodes = [
            node for node, degree in self.graph.degree() 
            if degree >= 3  # Nodes with 3+ connections
        ]
        
        # Limit to top 100 nodes to avoid memory explosion
        high_degree_nodes = high_degree_nodes[:100]
        
        for i, source in enumerate(high_degree_nodes):
            for target in high_degree_nodes[i+1:]:
                try:
                    # Cache both directions
                    if nx.has_path(self.graph, source, target):
                        path = nx.shortest_path(self.graph, source, target)
                        if len(path) <= max_depth:
                            self.path_cache[(source, target)] = {
                                'path': path,
                                'length': len(path) - 1,
                                'exists': True
                            }
                    
                    if nx.has_path(self.graph, target, source):
                        path = nx.shortest_path(self.graph, target, source)
                        if len(path) <= max_depth:
                            self.path_cache[(target, source)] = {
                                'path': path,
                                'length': len(path) - 1,
                                'exists': True
                            }
                            
                except nx.NetworkXNoPath:
                    self.path_cache[(source, target)] = {'exists': False}
                    self.path_cache[(target, source)] = {'exists': False}
    
    def _extract_keywords(self, text: str) -> Set[str]:
        """Extract meaningful keywords from text."""
        # Simple keyword extraction (can be enhanced with NLP)
        words = text.lower().split()
        keywords = set()
        for word in words:
            # Filter out common words and keep meaningful terms
            if len(word) > 3 and word.isalpha():
                keywords.add(word)
        return keywords
    
    def _get_weight_range(self, weight: float) -> str:
        """Categorize weight into ranges."""
        if weight >= 0.8:
            return 'high'
        elif weight >= 0.5:
            return 'medium'
        else:
            return 'low'
    
    # LOOKUP METHODS
    
    def find_nodes_by_category(self, category: str) -> List[str]:
        """Fast lookup of nodes by category."""
        return self.node_indices['by_category'].get(category, [])
    
    def find_nodes_by_file(self, filename: str) -> List[str]:
        """Fast lookup of nodes by filename."""
        return self.node_indices['by_file'].get(filename, [])
    
    def find_nodes_by_pattern(self, pattern: str, max_results: int = 10) -> List[str]:
        """Fast fuzzy search using pattern index."""
        pattern_lower = pattern.lower()
        matches = set()
        
        # Direct pattern matches
        if pattern_lower in self.node_indices['by_name_pattern']:
            matches.update(self.node_indices['by_name_pattern'][pattern_lower][:max_results])
        
        # Substring matches
        for indexed_pattern, nodes in self.node_indices['by_name_pattern'].items():
            if pattern_lower in indexed_pattern:
                matches.update(nodes)
                if len(matches) >= max_results:
                    break
        
        return list(matches)[:max_results]
    
    def find_edges_by_weight_range(self, weight_range: str) -> List[Dict[str, Any]]:
        """Find edges by weight range (high/medium/low)."""
        return self.edge_indices['by_weight_range'].get(weight_range, [])
    
    def find_edges_by_type(self, edge_type: str) -> List[Dict[str, Any]]:
        """Find edges by type."""
        return self.edge_indices['by_type'].get(edge_type, [])
    
    def get_cached_path(self, source: str, target: str) -> Optional[Dict[str, Any]]:
        """Get cached path between nodes."""
        return self.path_cache.get((source, target))
    
    def save_indices(self, filepath: str):
        """Save indices to file for later loading."""
        index_data = {
            'node_indices': dict(self.node_indices),
            'edge_indices': dict(self.edge_indices),
            'path_cache': self.path_cache
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(index_data, f)
    
    def load_indices(self, filepath: str):
        """Load indices from file."""
        with open(filepath, 'rb') as f:
            index_data = pickle.load(f)
        
        self.node_indices = index_data['node_indices']
        self.edge_indices = index_data['edge_indices'] 
        self.path_cache = index_data['path_cache']

    def _build_adjacency_optimizations(self):
        """Create optimized adjacency list structures for fast traversals."""
        # Forward adjacency (successors)
        self.adjacency_indices['forward'] = {}
        # Backward adjacency (predecessors) 
        self.adjacency_indices['backward'] = {}
        # Bidirectional adjacency
        self.adjacency_indices['bidirectional'] = {}
        
        for node in self.graph.nodes():
            # Forward adjacency with edge weights
            successors = []
            for successor in self.graph.successors(node):
                edge_data = self.graph.get_edge_data(node, successor)
                weight = edge_data.get(0, {}).get('weight', 1.0) if edge_data else 1.0
                successors.append((successor, weight))
            self.adjacency_indices['forward'][node] = successors
            
            # Backward adjacency
            predecessors = []
            for predecessor in self.graph.predecessors(node):
                edge_data = self.graph.get_edge_data(predecessor, node)
                weight = edge_data.get(0, {}).get('weight', 1.0) if edge_data else 1.0
                predecessors.append((predecessor, weight))
            self.adjacency_indices['backward'][node] = predecessors
            
            # Bidirectional (all neighbors)
            neighbors = set(self.graph.successors(node)) | set(self.graph.predecessors(node))
            self.adjacency_indices['bidirectional'][node] = list(neighbors)
    
    def build_spatial_indices(self, layout_algorithm: str = 'spring') -> Dict[str, Any]:
        """
        Design spatial indices for layout algorithms and geometric queries.
        
        Args:
            layout_algorithm (str): Layout algorithm to use ('spring', 'circular', 'random')
            
        Returns:
            Dict[str, Any]: Spatial index information
        """
        # Generate layout positions
        if layout_algorithm == 'spring':
            positions = nx.spring_layout(self.graph, k=1, iterations=50)
        elif layout_algorithm == 'circular':
            positions = nx.circular_layout(self.graph)
        elif layout_algorithm == 'random':
            positions = nx.random_layout(self.graph)
        else:
            positions = nx.spring_layout(self.graph)
        
        # Extract coordinates
        nodes = list(positions.keys())
        coordinates = np.array([positions[node] for node in nodes])
        
        # Build KD-tree for spatial queries
        kdtree = KDTree(coordinates)
        
        # Store spatial index
        self.spatial_index = {
            'positions': positions,
            'nodes': nodes,
            'coordinates': coordinates,
            'kdtree': kdtree,
            'layout_algorithm': layout_algorithm
        }
        
        return {
            'num_nodes': len(nodes),
            'layout_algorithm': layout_algorithm,
            'bounding_box': {
                'min_x': np.min(coordinates[:, 0]),
                'max_x': np.max(coordinates[:, 0]),
                'min_y': np.min(coordinates[:, 1]),
                'max_y': np.max(coordinates[:, 1])
            }
        }
    
    def optimize_for_query_patterns(self, query_patterns: List[str]):
        """
        Optimize indices for specific query patterns.
        
        Args:
            query_patterns (List[str]): List of query types to optimize for
        """
        self.query_optimizations = {}
        
        for pattern in query_patterns:
            if pattern == 'shortest_path':
                self._optimize_shortest_path_queries()
            elif pattern == 'neighborhood':
                self._optimize_neighborhood_queries()
            elif pattern == 'centrality':
                self._optimize_centrality_queries()
            elif pattern == 'subgraph':
                self._optimize_subgraph_queries()
    
    def _optimize_shortest_path_queries(self):
        """Pre-compute shortest paths for frequently accessed node pairs."""
        # Identify high-degree nodes as likely query targets
        high_degree_nodes = [
            node for node, degree in self.graph.degree() 
            if degree >= np.percentile([d for n, d in self.graph.degree()], 75)
        ]
        
        # Pre-compute all-pairs shortest paths for high-degree nodes
        self.query_optimizations['shortest_paths'] = {}
        
        for source in high_degree_nodes[:20]:  # Limit to prevent memory explosion
            try:
                paths = nx.single_source_shortest_path(self.graph, source, cutoff=4)
                self.query_optimizations['shortest_paths'][source] = paths
            except:
                continue
    
    def _optimize_neighborhood_queries(self):
        """Pre-compute multi-hop neighborhoods."""
        self.query_optimizations['neighborhoods'] = {}
        
        for node in self.graph.nodes():
            neighborhoods = {}
            
            # 1-hop neighborhood
            neighborhoods[1] = set(self.graph.neighbors(node))
            
            # 2-hop neighborhood
            two_hop = set()
            for neighbor in neighborhoods[1]:
                two_hop.update(self.graph.neighbors(neighbor))
            neighborhoods[2] = two_hop - neighborhoods[1] - {node}
            
            self.query_optimizations['neighborhoods'][node] = neighborhoods
    
    def _optimize_centrality_queries(self):
        """Pre-compute centrality measures."""
        self.query_optimizations['centrality'] = {}
        
        # Degree centrality
        self.query_optimizations['centrality']['degree'] = dict(self.graph.degree())
        
        # Betweenness centrality (sample for large graphs)
        if len(self.graph.nodes()) <= 1000:
            self.query_optimizations['centrality']['betweenness'] = nx.betweenness_centrality(self.graph)
        else:
            # Sample-based approximation for large graphs
            sample_size = min(100, len(self.graph.nodes()) // 10)
            self.query_optimizations['centrality']['betweenness'] = nx.betweenness_centrality(
                self.graph, k=sample_size
            )
    
    def _optimize_subgraph_queries(self):
        """Pre-compute common subgraph patterns."""
        self.query_optimizations['subgraphs'] = {}
        
        # Component-based subgraphs
        if not self.graph.is_directed():
            components = list(nx.connected_components(self.graph))
        else:
            components = list(nx.weakly_connected_components(self.graph))
        
        self.query_optimizations['subgraphs']['components'] = components
        
        # File-based subgraphs (nodes from same file)
        file_subgraphs = {}
        for node, attrs in self.graph.nodes(data=True):
            fname = attrs.get('fname', 'unknown')
            if fname not in file_subgraphs:
                file_subgraphs[fname] = []
            file_subgraphs[fname].append(node)
        
        self.query_optimizations['subgraphs']['by_file'] = file_subgraphs
    
    # OPTIMIZED QUERY METHODS
    
    def fast_shortest_path(self, source: str, target: str) -> Optional[List[str]]:
        """Fast shortest path query using pre-computed paths."""
        # Check cache first
        if hasattr(self, 'query_optimizations') and 'shortest_paths' in self.query_optimizations:
            if source in self.query_optimizations['shortest_paths']:
                paths = self.query_optimizations['shortest_paths'][source]
                if target in paths:
                    return paths[target]
        
        # Fall back to standard computation
        try:
            return nx.shortest_path(self.graph, source, target)
        except nx.NetworkXNoPath:
            return None
    
    def fast_neighborhood(self, node: str, hops: int = 1) -> Set[str]:
        """Fast neighborhood query using pre-computed neighborhoods."""
        if hasattr(self, 'query_optimizations') and 'neighborhoods' in self.query_optimizations:
            if node in self.query_optimizations['neighborhoods']:
                neighborhoods = self.query_optimizations['neighborhoods'][node]
                if hops in neighborhoods:
                    return neighborhoods[hops]
        
        # Fall back to standard computation
        if hops == 1:
            return set(self.graph.neighbors(node))
        else:
            # BFS for multi-hop
            visited = set()
            current_level = {node}
            
            for _ in range(hops):
                next_level = set()
                for n in current_level:
                    next_level.update(self.graph.neighbors(n))
                current_level = next_level - visited
                visited.update(current_level)
            
            return current_level
    
    def spatial_nearest_neighbors(self, node: str, k: int = 5) -> List[str]:
        """Find k nearest neighbors in spatial layout."""
        if not hasattr(self, 'spatial_index'):
            raise ValueError("Spatial index not built. Call build_spatial_indices() first.")
        
        if node not in self.spatial_index['positions']:
            return []
        
        node_pos = self.spatial_index['positions'][node]
        
        # Query KD-tree
        distances, indices = self.spatial_index['kdtree'].query(
            node_pos, k=k+1  # +1 because it includes the query node itself
        )
        
        # Convert indices to node names (excluding the query node itself)
        neighbors = []
        for i, idx in enumerate(indices):
            if i == 0:  # Skip the query node itself
                continue
            neighbors.append(self.spatial_index['nodes'][idx])
        
        return neighbors[:k]        