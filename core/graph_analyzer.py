# ADD TO: core/graph_searcher.py (or create new core/graph_analyzer.py)

import numpy as np
from scipy import sparse
from sklearn.cluster import SpectralClustering
import community  # python-louvain for community detection

class GraphAnalyzer:
    """
    Comprehensive graph analysis engine for structural properties and pattern identification.
    """
    
    def __init__(self, graph: nx.MultiDiGraph):
        self.graph = graph
        self.undirected_graph = graph.to_undirected()
        self._metrics_cache = {}
    
    def calculate_graph_metrics(self) -> Dict[str, float]:
        """
        Calculate comprehensive graph metrics including density, diameter, clustering coefficient.
        
        Returns:
            Dict[str, float]: Dictionary of graph metrics
        """
        if 'basic_metrics' in self._metrics_cache:
            return self._metrics_cache['basic_metrics']
        
        metrics = {}
        
        # Basic metrics
        num_nodes = len(self.graph.nodes())
        num_edges = len(self.graph.edges())
        
        metrics['num_nodes'] = num_nodes
        metrics['num_edges'] = num_edges
        metrics['density'] = nx.density(self.graph)
        
        # Diameter and average path length (on largest connected component)
        if nx.is_connected(self.undirected_graph):
            metrics['diameter'] = nx.diameter(self.undirected_graph)
            metrics['average_path_length'] = nx.average_shortest_path_length(self.undirected_graph)
        else:
            # Use largest connected component
            largest_cc = max(nx.connected_components(self.undirected_graph), key=len)
            subgraph = self.undirected_graph.subgraph(largest_cc)
            metrics['diameter'] = nx.diameter(subgraph)
            metrics['average_path_length'] = nx.average_shortest_path_length(subgraph)
            metrics['largest_component_size'] = len(largest_cc)
            metrics['connectivity_ratio'] = len(largest_cc) / num_nodes
        
        # Clustering coefficient
        metrics['average_clustering'] = nx.average_clustering(self.undirected_graph)
        metrics['transitivity'] = nx.transitivity(self.undirected_graph)
        
        # Degree statistics
        degrees = [d for n, d in self.graph.degree()]
        metrics['average_degree'] = np.mean(degrees)
        metrics['degree_std'] = np.std(degrees)
        metrics['max_degree'] = max(degrees)
        metrics['min_degree'] = min(degrees)
        
        # Assortativity
        try:
            metrics['degree_assortativity'] = nx.degree_assortativity_coefficient(self.graph)
        except:
            metrics['degree_assortativity'] = None
        
        self._metrics_cache['basic_metrics'] = metrics
        return metrics
    
    def identify_important_nodes(self) -> Dict[str, List[str]]:
        """
        Identify important nodes including hubs, bridges, and articulation points.
        
        Returns:
            Dict[str, List[str]]: Dictionary categorizing important nodes
        """
        important_nodes = {
            'hubs': [],
            'bridges': [],
            'articulation_points': [],
            'high_betweenness': [],
            'high_closeness': [],
            'high_eigenvector': []
        }
        
        # Degree-based hubs (top 10% by degree)
        degrees = dict(self.graph.degree())
        degree_threshold = np.percentile(list(degrees.values()), 90)
        important_nodes['hubs'] = [node for node, deg in degrees.items() if deg >= degree_threshold]
        
        # Bridge edges and articulation points
        bridge_edges = list(nx.bridges(self.undirected_graph))
        important_nodes['bridges'] = list(set([node for edge in bridge_edges for node in edge]))
        
        articulation_points = list(nx.articulation_points(self.undirected_graph))
        important_nodes['articulation_points'] = articulation_points
        
        # Centrality-based importance
        # Betweenness centrality
        betweenness = nx.betweenness_centrality(self.graph)
        bet_threshold = np.percentile(list(betweenness.values()), 90)
        important_nodes['high_betweenness'] = [node for node, bet in betweenness.items() if bet >= bet_threshold]
        
        # Closeness centrality (on largest connected component)
        if nx.is_connected(self.undirected_graph):
            closeness = nx.closeness_centrality(self.undirected_graph)
            close_threshold = np.percentile(list(closeness.values()), 90)
            important_nodes['high_closeness'] = [node for node, close in closeness.items() if close >= close_threshold]
        
        # Eigenvector centrality
        try:
            eigenvector = nx.eigenvector_centrality(self.graph, max_iter=1000)
            eig_threshold = np.percentile(list(eigenvector.values()), 90)
            important_nodes['high_eigenvector'] = [node for node, eig in eigenvector.items() if eig >= eig_threshold]
        except:
            important_nodes['high_eigenvector'] = []
        
        return important_nodes
    
    def detect_communities(self, method: str = 'louvain') -> Dict[str, Any]:
        """
        Detect communities and sub-graphs using various algorithms.
        
        Args:
            method (str): Community detection method ('louvain', 'spectral', 'greedy')
            
        Returns:
            Dict[str, Any]: Community detection results
        """
        communities_result = {
            'method': method,
            'communities': [],
            'modularity': 0,
            'num_communities': 0
        }
        
        if method == 'louvain':
            # Convert to simple undirected graph for community detection
            simple_graph = nx.Graph()
            for u, v in self.undirected_graph.edges():
                if simple_graph.has_edge(u, v):
                    simple_graph[u][v]['weight'] += 1
                else:
                    simple_graph.add_edge(u, v, weight=1)
            
            partition = community.best_partition(simple_graph)
            communities_result['modularity'] = community.modularity(partition, simple_graph)
            
            # Group nodes by community
            community_dict = {}
            for node, comm_id in partition.items():
                if comm_id not in community_dict:
                    community_dict[comm_id] = []
                community_dict[comm_id].append(node)
            
            communities_result['communities'] = list(community_dict.values())
            communities_result['num_communities'] = len(community_dict)
        
        elif method == 'spectral':
            # Use spectral clustering
            if len(self.graph.nodes()) > 2:
                adjacency_matrix = nx.adjacency_matrix(self.undirected_graph)
                n_clusters = min(10, len(self.graph.nodes()) // 5)  # Heuristic for number of clusters
                
                clustering = SpectralClustering(n_clusters=n_clusters, affinity='precomputed')
                labels = clustering.fit_predict(adjacency_matrix.toarray())
                
                # Group nodes by cluster
                nodes = list(self.graph.nodes())
                community_dict = {}
                for i, label in enumerate(labels):
                    if label not in community_dict:
                        community_dict[label] = []
                    community_dict[label].append(nodes[i])
                
                communities_result['communities'] = list(community_dict.values())
                communities_result['num_communities'] = len(community_dict)
        
        elif method == 'greedy':
            communities = list(nx.community.greedy_modularity_communities(self.undirected_graph))
            communities_result['communities'] = [list(comm) for comm in communities]
            communities_result['num_communities'] = len(communities)
            communities_result['modularity'] = nx.community.modularity(self.undirected_graph, communities)
        
        return communities_result
    
    def analyze_edge_weight_distribution(self) -> Dict[str, Any]:
        """
        Analyze edge weight distributions and patterns.
        
        Returns:
            Dict[str, Any]: Edge weight analysis
        """
        # Extract edge weights (calculate if not present)
        edge_weights = []
        edge_types = {}
        
        for u, v, attrs in self.graph.edges(data=True):
            weight = attrs.get('weight', 1.0)
            edge_type = attrs.get('label', 'unknown')
            
            edge_weights.append(weight)
            
            if edge_type not in edge_types:
                edge_types[edge_type] = []
            edge_types[edge_type].append(weight)
        
        if not edge_weights:
            return {'error': 'No edges found in graph'}
        
        analysis = {
            'total_edges': len(edge_weights),
            'weight_statistics': {
                'mean': np.mean(edge_weights),
                'std': np.std(edge_weights),
                'min': np.min(edge_weights),
                'max': np.max(edge_weights),
                'median': np.median(edge_weights),
                'percentiles': {
                    '25th': np.percentile(edge_weights, 25),
                    '75th': np.percentile(edge_weights, 75),
                    '90th': np.percentile(edge_weights, 90)
                }
            },
            'edge_type_analysis': {}
        }
        
        # Analyze by edge type
        for edge_type, weights in edge_types.items():
            analysis['edge_type_analysis'][edge_type] = {
                'count': len(weights),
                'mean_weight': np.mean(weights),
                'std_weight': np.std(weights),
                'percentage': len(weights) / len(edge_weights) * 100
            }
        
        return analysis
    
    def generate_graph_health_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive graph health report.
        
        Returns:
            Dict[str, Any]: Health report with recommendations
        """
        health_report = {
            'overall_health': 'good',  # good, fair, poor
            'metrics': self.calculate_graph_metrics(),
            'important_nodes': self.identify_important_nodes(),
            'communities': self.detect_communities(),
            'edge_analysis': self.analyze_edge_weight_distribution(),
            'issues': [],
            'recommendations': []
        }
        
        metrics = health_report['metrics']
        
        # Identify potential issues
        if metrics.get('connectivity_ratio', 1.0) < 0.8:
            health_report['issues'].append('Graph has low connectivity - many isolated components')
            health_report['recommendations'].append('Review isolated nodes and add missing connections')
        
        if metrics.get('density', 0) < 0.01:
            health_report['issues'].append('Graph is very sparse')
            health_report['recommendations'].append('Consider if all important relationships are captured')
        
        if metrics.get('density', 0) > 0.5:
            health_report['issues'].append('Graph is very dense - may indicate over-connection')
            health_report['recommendations'].append('Review if all edges are necessary')
        
        if len(health_report['important_nodes']['articulation_points']) > 0:
            health_report['issues'].append('Graph has critical nodes whose removal would disconnect components')
            health_report['recommendations'].append('Consider redundant paths for critical connections')
        
        # Determine overall health
        issue_count = len(health_report['issues'])
        if issue_count == 0:
            health_report['overall_health'] = 'good'
        elif issue_count <= 2:
            health_report['overall_health'] = 'fair'
        else:
            health_report['overall_health'] = 'poor'
        
        return health_report