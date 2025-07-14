# File: core/graph_loader.py

import os
import pickle
import json
import networkx as nx
from typing import Optional, Dict, Any, List
from pathlib import Path
import magic  # For content-based format detection
from jsonschema import validate, ValidationError
import networkx as nx

class GraphLoader:
    """
    Enhanced graph loader with NetworkX validation and multiple format support.
    """
    
    def __init__(self):
        self.supported_formats = ['.pkl', '.json', '.gml', '.graphml', '.edgelist', '.adjlist']
        # Define schema for validation
        self.node_schema = {
            "type": "object",
            "required": ["category"],
            "properties": {
                "category": {"type": "string"},
                "fname": {"type": "string"},
                "line": {"type": "array", "items": {"type": "integer"}},
                "info": {"type": "string"},
                "docstring": {"type": "string"}
            }
        }
        
        self.edge_schema = {
            "type": "object",
            "properties": {
                "label": {"type": "string"},
                "weight": {"type": "number"}
            }
        }

    def load_graph(self, file_path: str, validate: bool = True) -> Optional[nx.MultiDiGraph]:
        """
        Load a NetworkX graph from various formats with validation.
        
        Args:
            file_path (str): Path to the graph file
            validate (bool): Whether to validate the graph structure
            
        Returns:
            nx.MultiDiGraph: Loaded and validated graph
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Graph file not found: {file_path}")
        
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext == '.pkl':
            graph = self._load_pickle(file_path)
        elif file_ext == '.json':
            graph = self._load_json(file_path)
        elif file_ext == '.gml':
            graph = nx.read_gml(file_path)
        elif file_ext == '.graphml':
            graph = nx.read_graphml(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")
        
        if validate:
            self.validate_graph(graph)
            
        return graph
    
    def _load_pickle(self, file_path: str) -> nx.MultiDiGraph:
        """Load graph from pickle file."""
        with open(file_path, 'rb') as f:
            graph = pickle.load(f)
        return graph
    
    def _load_json(self, file_path: str) -> nx.MultiDiGraph:
        """Load graph from JSON format."""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        graph = nx.MultiDiGraph()
        
        # Add nodes
        for node_data in data.get('nodes', []):
            node_id = node_data.pop('id')
            graph.add_node(node_id, **node_data)
        
        # Add edges
        for edge_data in data.get('edges', []):
            source = edge_data.pop('source')
            target = edge_data.pop('target')
            graph.add_edge(source, target, **edge_data)
        
        return graph
    
    def validate_graph(self, graph: nx.MultiDiGraph) -> Dict[str, Any]:
        """
        Validate NetworkX graph structure and return validation report.
        
        Args:
            graph (nx.MultiDiGraph): Graph to validate
            
        Returns:
            Dict[str, Any]: Validation report
        """
        validation_report = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'statistics': {}
        }
        
        # Basic structure validation
        if not isinstance(graph, (nx.DiGraph, nx.MultiDiGraph)):
            validation_report['errors'].append("Graph must be a NetworkX DiGraph or MultiDiGraph")
            validation_report['is_valid'] = False
        
        # Check for empty graph
        if len(graph.nodes()) == 0:
            validation_report['warnings'].append("Graph has no nodes")
        
        # Check for isolated nodes
        isolated_nodes = list(nx.isolates(graph))
        if isolated_nodes:
            validation_report['warnings'].append(f"Found {len(isolated_nodes)} isolated nodes")
        
        # Validate node attributes
        required_node_attrs = ['category', 'fname', 'line']
        for node, attrs in graph.nodes(data=True):
            missing_attrs = [attr for attr in required_node_attrs if attr not in attrs]
            if missing_attrs:
                validation_report['warnings'].append(
                    f"Node '{node}' missing attributes: {missing_attrs}"
                )
        
        # Check for self-loops
        self_loops = list(nx.selfloop_edges(graph))
        if self_loops:
            validation_report['warnings'].append(f"Found {len(self_loops)} self-loops")
        
        # Generate statistics
        validation_report['statistics'] = {
            'total_nodes': len(graph.nodes()),
            'total_edges': len(graph.edges()),
            'isolated_nodes': len(isolated_nodes),
            'self_loops': len(self_loops),
            'is_connected': nx.is_weakly_connected(graph),
            'number_of_components': nx.number_weakly_connected_components(graph)
        }
        
        return validation_report
    
    def save_graph(self, graph: nx.MultiDiGraph, file_path: str, format: str = 'pickle'):
        """
        Save graph in specified format.
        
        Args:
            graph (nx.MultiDiGraph): Graph to save
            file_path (str): Output file path
            format (str): Output format ('pickle', 'json', 'gml', 'graphml')
        """
        if format == 'pickle':
            with open(file_path, 'wb') as f:
                pickle.dump(graph, f)
        elif format == 'json':
            self._save_json(graph, file_path)
        elif format == 'gml':
            nx.write_gml(graph, file_path)
        elif format == 'graphml':
            nx.write_graphml(graph, file_path)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _save_json(self, graph: nx.MultiDiGraph, file_path: str):
        """Save graph to JSON format."""
        data = {
            'nodes': [{'id': node, **attrs} for node, attrs in graph.nodes(data=True)],
            'edges': [{'source': u, 'target': v, **attrs} for u, v, attrs in graph.edges(data=True)]
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)

    def detect_format(self, file_path: str) -> str:
        """
        Detect graph format based on both file extension and content analysis.
        
        Args:
            file_path (str): Path to the graph file
            
        Returns:
            str: Detected format
        """
        file_ext = Path(file_path).suffix.lower()
        
        # First try extension-based detection
        if file_ext in ['.pkl', '.pickle']:
            return 'pickle'
        elif file_ext == '.json':
            return 'json'
        elif file_ext == '.gml':
            return 'gml'
        elif file_ext == '.graphml':
            return 'graphml'
        
        # Content-based detection for ambiguous cases
        try:
            with open(file_path, 'rb') as f:
                header = f.read(1024)
            
            # Check for pickle magic bytes
            if header.startswith(b'\x80\x03') or header.startswith(b'\x80\x04'):
                return 'pickle'
            
            # Check for JSON
            header_str = header.decode('utf-8', errors='ignore')
            if header_str.strip().startswith('{') or header_str.strip().startswith('['):
                return 'json'
            
            # Check for XML-based formats
            if '<?xml' in header_str or '<graphml' in header_str:
                return 'graphml'
            
            if 'graph [' in header_str:
                return 'gml'
                
        except Exception:
            pass
        
        raise ValueError(f"Cannot detect format for file: {file_path}")
    
    def validate_schema(self, graph: nx.MultiDiGraph) -> Dict[str, Any]:
        """
        Validate node and edge attributes against predefined schemas.
        
        Args:
            graph (nx.MultiDiGraph): Graph to validate
            
        Returns:
            Dict[str, Any]: Validation report with schema compliance
        """
        validation_report = {
            'schema_valid': True,
            'node_validation_errors': [],
            'edge_validation_errors': [],
            'schema_warnings': []
        }
        
        # Validate node attributes
        for node, attrs in graph.nodes(data=True):
            try:
                validate(instance=attrs, schema=self.node_schema)
            except ValidationError as e:
                validation_report['node_validation_errors'].append({
                    'node': node,
                    'error': str(e.message),
                    'path': list(e.path)
                })
                validation_report['schema_valid'] = False
        
        # Validate edge attributes
        for u, v, attrs in graph.edges(data=True):
            try:
                validate(instance=attrs, schema=self.edge_schema)
            except ValidationError as e:
                validation_report['edge_validation_errors'].append({
                    'edge': f"{u} -> {v}",
                    'error': str(e.message),
                    'path': list(e.path)
                })
                validation_report['schema_valid'] = False
        
        return validation_report
    
    def convert_graph_representation(self, graph: nx.MultiDiGraph, target_type: str) -> nx.Graph:
        """
        Convert between different graph representations.
        
        Args:
            graph (nx.MultiDiGraph): Source graph
            target_type (str): Target type ('directed', 'undirected', 'simple')
            
        Returns:
            nx.Graph: Converted graph
        """
        if target_type == 'undirected':
            return graph.to_undirected()
        elif target_type == 'simple':
            # Convert MultiDiGraph to simple DiGraph
            simple_graph = nx.DiGraph()
            for node, attrs in graph.nodes(data=True):
                simple_graph.add_node(node, **attrs)
            
            # Merge parallel edges
            for u, v, attrs in graph.edges(data=True):
                if simple_graph.has_edge(u, v):
                    # Merge edge attributes
                    existing_attrs = simple_graph[u][v]
                    weight = existing_attrs.get('weight', 1) + attrs.get('weight', 1)
                    simple_graph[u][v]['weight'] = weight
                else:
                    simple_graph.add_edge(u, v, **attrs)
            
            return simple_graph
        elif target_type == 'directed':
            return graph  # Already directed
        else:
            raise ValueError(f"Unsupported target type: {target_type}")