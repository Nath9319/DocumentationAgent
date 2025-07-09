# File: main_doc_analyzer.py
#
# Main entry point for Documentation Graph Analysis
# Works with generated documentation graphs from the output folder

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import argparse

# Import the new components we created
from core.graph_loader import GraphLoader
from core.graph_searcher import RepoSearcher
from core.graph_index_builder import GraphIndexBuilder

class DocumentationGraphAnalyzer:
    """
    Main analyzer for working with generated documentation graphs.
    Loads and analyzes documentation graphs created by the AI Documentation Agent.
    """
    
    def __init__(self, output_dir: str):
        """
        Initialize the analyzer with an output directory.
        
        Args:
            output_dir (str): Path to the output directory containing generated graphs
        """
        self.output_dir = Path(output_dir)
        self.loader = GraphLoader()
        self.documentation_graph = None
        self.conceptual_graph = None
        self.searcher = None
        self.index_builder = None
        self.metadata = None
        
        self._validate_output_directory()
        self._load_graphs()
        self._load_metadata()
        
    def _validate_output_directory(self):
        """Validate that the output directory contains required files."""
        if not self.output_dir.exists():
            raise FileNotFoundError(f"Output directory not found: {self.output_dir}")
        
        required_files = [
            "documentation_graph.pkl",
            "conceptual_graph.pkl", 
            "documentation_and_graph_data.json"
        ]
        
        missing_files = []
        for file in required_files:
            if not (self.output_dir / file).exists():
                missing_files.append(file)
        
        if missing_files:
            raise FileNotFoundError(
                f"Missing required files in {self.output_dir}: {missing_files}"
            )
        
        print(f"✓ Output directory validated: {self.output_dir}")
    
    def _load_graphs(self):
        """Load documentation and conceptual graphs."""
        print("Loading documentation and conceptual graphs...")
        
        # Load documentation graph (contains documentation text instead of code)
        doc_graph_path = self.output_dir / "documentation_graph.pkl"
        self.documentation_graph = self.loader.load_graph(str(doc_graph_path), validate=True)
        print(f"✓ Documentation graph loaded: {len(self.documentation_graph.nodes())} nodes, {len(self.documentation_graph.edges())} edges")
        
        # Load conceptual graph (contains semantic relationships)
        conceptual_graph_path = self.output_dir / "conceptual_graph.pkl"
        self.conceptual_graph = self.loader.load_graph(str(conceptual_graph_path), validate=True)
        print(f"✓ Conceptual graph loaded: {len(self.conceptual_graph.nodes())} nodes, {len(self.conceptual_graph.edges())} edges")
        
        # Initialize searcher with documentation graph as primary
        self.searcher = RepoSearcher(self.documentation_graph)
        
        # Build indices for fast queries
        print("Building search indices...")
        self.index_builder = GraphIndexBuilder(self.documentation_graph)
        print("✓ Search indices built")
    
    def _load_metadata(self):
        """Load generation metadata and documentation data."""
        # Load main documentation data
        doc_data_path = self.output_dir / "documentation_and_graph_data.json"
        with open(doc_data_path, 'r', encoding='utf-8') as f:
            self.metadata = json.load(f)
        
        # Load generation metadata if available
        gen_metadata_path = self.output_dir / "generation_metadata.json"
        if gen_metadata_path.exists():
            with open(gen_metadata_path, 'r', encoding='utf-8') as f:
                generation_info = json.load(f)
                self.metadata['generation_info'] = generation_info
        
        print(f"✓ Metadata loaded for {len(self.metadata)} documented nodes")
    
    def analyze_documentation_quality(self) -> Dict[str, Any]:
        """
        Analyze the quality of generated documentation.
        
        Returns:
            Dict[str, Any]: Quality analysis report
        """
        print("\n" + "="*60)
        print("DOCUMENTATION QUALITY ANALYSIS")
        print("="*60)
        
        quality_report = {
            'overall_stats': {},
            'confidence_analysis': {},
            'coverage_analysis': {},
            'content_analysis': {}
        }
        
        # Overall statistics
        total_nodes = len(self.documentation_graph.nodes())
        documented_nodes = len(self.metadata)
        
        quality_report['overall_stats'] = {
            'total_nodes_in_graph': total_nodes,
            'documented_nodes': documented_nodes,
            'documentation_coverage': documented_nodes / total_nodes if total_nodes > 0 else 0
        }
        
        # Confidence analysis
        confidence_scores = []
        high_confidence = medium_confidence = low_confidence = 0
        
        for node_name, data in self.metadata.items():
            if isinstance(data, dict) and 'context_metadata' in data:
                context_meta = data['context_metadata']
                confidence = context_meta.get('average_confidence', 1.0)
                confidence_scores.append(confidence)
                
                if confidence >= 0.9:
                    high_confidence += 1
                elif confidence >= 0.7:
                    medium_confidence += 1
                else:
                    low_confidence += 1
        
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        
        quality_report['confidence_analysis'] = {
            'average_confidence': avg_confidence,
            'high_confidence_nodes': high_confidence,
            'medium_confidence_nodes': medium_confidence,
            'low_confidence_nodes': low_confidence,
            'confidence_distribution': {
                'high (90%+)': high_confidence,
                'medium (70-90%)': medium_confidence,
                'low (<70%)': low_confidence
            }
        }
        
        # Coverage analysis by node type
        coverage_by_type = {}
        for node, attrs in self.documentation_graph.nodes(data=True):
            node_type = attrs.get('original_category', 'unknown')
            if node_type not in coverage_by_type:
                coverage_by_type[node_type] = {'total': 0, 'documented': 0}
            
            coverage_by_type[node_type]['total'] += 1
            if node in self.metadata:
                coverage_by_type[node_type]['documented'] += 1
        
        # Calculate coverage percentages
        for node_type, stats in coverage_by_type.items():
            stats['coverage_percent'] = (stats['documented'] / stats['total'] * 100) if stats['total'] > 0 else 0
        
        quality_report['coverage_analysis'] = coverage_by_type
        
        # Content analysis
        doc_lengths = []
        empty_docs = 0
        
        for node_name, data in self.metadata.items():
            if isinstance(data, dict) and 'documentation' in data:
                doc_text = data['documentation']
                if doc_text:
                    doc_lengths.append(len(doc_text))
                else:
                    empty_docs += 1
        
        quality_report['content_analysis'] = {
            'average_doc_length': sum(doc_lengths) / len(doc_lengths) if doc_lengths else 0,
            'min_doc_length': min(doc_lengths) if doc_lengths else 0,
            'max_doc_length': max(doc_lengths) if doc_lengths else 0,
            'empty_documentation': empty_docs,
            'total_analyzed': len(doc_lengths) + empty_docs
        }
        
        self._print_quality_report(quality_report)
        return quality_report
    
    def _print_quality_report(self, report: Dict[str, Any]):
        """Print formatted quality report."""
        print(f"📊 Overall Coverage: {report['overall_stats']['documentation_coverage']:.1%}")
        print(f"📈 Average Confidence: {report['confidence_analysis']['average_confidence']:.1%}")
        print(f"📝 Average Doc Length: {report['content_analysis']['average_doc_length']:.0f} characters")
        
        print(f"\n🎯 Confidence Distribution:")
        for level, count in report['confidence_analysis']['confidence_distribution'].items():
            print(f"   {level}: {count} nodes")
        
        print(f"\n📂 Coverage by Node Type:")
        for node_type, stats in report['coverage_analysis'].items():
            print(f"   {node_type}: {stats['coverage_percent']:.1f}% ({stats['documented']}/{stats['total']})")
    
    def search_documentation(self, query: str, search_type: str = 'all') -> List[Dict[str, Any]]:
        """
        Search through documentation content.
        
        Args:
            query (str): Search query
            search_type (str): Type of search ('name', 'content', 'all')
            
        Returns:
            List[Dict[str, Any]]: Search results
        """
        results = []
        query_lower = query.lower()
        
        for node_name, data in self.metadata.items():
            match_score = 0
            match_reasons = []
            
            # Search in node name
            if search_type in ['name', 'all'] and query_lower in node_name.lower():
                match_score += 10
                match_reasons.append('name_match')
            
            # Search in documentation content
            if search_type in ['content', 'all'] and isinstance(data, dict):
                doc_text = data.get('documentation', '').lower()
                if query_lower in doc_text:
                    match_score += 5
                    match_reasons.append('content_match')
                
                # Search in conceptual data
                conceptual_data = data.get('conceptual_data', {})
                if isinstance(conceptual_data, dict):
                    semantic_meta = conceptual_data.get('semantic_metadata', {})
                    if query_lower in str(semantic_meta).lower():
                        match_score += 3
                        match_reasons.append('semantic_match')
            
            if match_score > 0:
                results.append({
                    'node_name': node_name,
                    'match_score': match_score,
                    'match_reasons': match_reasons,
                    'documentation': data.get('documentation', '') if isinstance(data, dict) else str(data),
                    'node_attrs': self.documentation_graph.nodes.get(node_name, {})
                })
        
        # Sort by match score
        results.sort(key=lambda x: x['match_score'], reverse=True)
        return results
    
    def analyze_node_relationships(self, node_name: str) -> Dict[str, Any]:
        """
        Analyze relationships for a specific node.
        
        Args:
            node_name (str): Name of the node to analyze
            
        Returns:
            Dict[str, Any]: Relationship analysis
        """
        if node_name not in self.documentation_graph:
            return {'error': f"Node '{node_name}' not found in documentation graph"}
        
        analysis = {
            'node_info': {},
            'documentation_relationships': {},
            'conceptual_relationships': {},
            'connection_strength': {}
        }
        
        # Basic node info
        analysis['node_info'] = {
            'name': node_name,
            'attributes': dict(self.documentation_graph.nodes[node_name]),
            'metadata': self.metadata.get(node_name, {})
        }
        
        # Documentation graph relationships
        dependencies = self.searcher.get_dependencies(node_name)
        references = self.searcher.get_references(node_name)
        
        analysis['documentation_relationships'] = {
            'dependencies': dependencies,
            'references': references,
            'dependency_count': len(dependencies),
            'reference_count': len(references)
        }
        
        # Conceptual graph relationships (if node exists there)
        if self.conceptual_graph and self.conceptual_graph.has_node(node_name):
            conceptual_deps = list(self.conceptual_graph.successors(node_name))
            conceptual_refs = list(self.conceptual_graph.predecessors(node_name))
            
            analysis['conceptual_relationships'] = {
                'semantic_dependencies': conceptual_deps,
                'semantic_references': conceptual_refs,
                'semantic_dependency_count': len(conceptual_deps),
                'semantic_reference_count': len(conceptual_refs)
            }
        
        # Connection strength analysis
        connection_strengths = {}
        for target in dependencies[:5]:  # Analyze top 5 dependencies
            strength = self.searcher.calculate_connection_strength(node_name, target)
            connection_strengths[target] = strength
        
        analysis['connection_strength'] = connection_strengths
        
        return analysis
    
    def generate_documentation_report(self, output_file: str = None):
        """
        Generate a comprehensive documentation analysis report.
        
        Args:
            output_file (str): Optional output file path
        """
        print("\n" + "="*60)
        print("GENERATING COMPREHENSIVE DOCUMENTATION REPORT")
        print("="*60)
        
        report = {
            'analysis_metadata': {
                'output_directory': str(self.output_dir),
                'analysis_timestamp': self._get_timestamp()
            },
            'quality_analysis': self.analyze_documentation_quality(),
            'graph_statistics': {
                'documentation_graph': self.searcher.get_enhanced_graph_statistics(),
                'conceptual_graph': self._get_conceptual_graph_stats()
            },
            'top_connected_nodes': self._get_top_connected_nodes(),
            'coverage_gaps': self._identify_coverage_gaps()
        }
        
        if output_file:
            output_path = self.output_dir / output_file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, default=str)
            print(f"✓ Comprehensive report saved to: {output_path}")
        
        return report
    
    def _get_conceptual_graph_stats(self) -> Dict[str, Any]:
        """Get statistics for conceptual graph."""
        if not self.conceptual_graph:
            return {}
        
        conceptual_searcher = RepoSearcher(self.conceptual_graph)
        return conceptual_searcher.get_enhanced_graph_statistics()
    
    def _get_top_connected_nodes(self, top_n: int = 10) -> List[Dict[str, Any]]:
        """Get most connected nodes with their documentation quality."""
        top_nodes = self.searcher.get_most_connected_nodes(top_n)
        
        enriched_nodes = []
        for node_name, degree in top_nodes:
            node_data = {
                'name': node_name,
                'degree': degree,
                'has_documentation': node_name in self.metadata
            }
            
            if node_name in self.metadata:
                metadata = self.metadata[node_name]
                if isinstance(metadata, dict) and 'context_metadata' in metadata:
                    node_data['confidence'] = metadata['context_metadata'].get('average_confidence', 0)
            
            enriched_nodes.append(node_data)
        
        return enriched_nodes
    
    def _identify_coverage_gaps(self) -> List[Dict[str, Any]]:
        """Identify nodes that are highly connected but poorly documented."""
        gaps = []
        
        for node in self.documentation_graph.nodes():
            degree = self.documentation_graph.degree(node)
            
            # Focus on nodes with high connectivity
            if degree >= 3:
                has_doc = node in self.metadata
                confidence = 0
                
                if has_doc and isinstance(self.metadata[node], dict):
                    context_meta = self.metadata[node].get('context_metadata', {})
                    confidence = context_meta.get('average_confidence', 0)
                
                # Identify gaps: high connectivity but no docs or low confidence
                if not has_doc or confidence < 0.7:
                    gaps.append({
                        'node_name': node,
                        'degree': degree,
                        'has_documentation': has_doc,
                        'confidence': confidence,
                        'gap_severity': 'high' if degree >= 5 else 'medium'
                    })
        
        # Sort by degree (most connected first)
        gaps.sort(key=lambda x: x['degree'], reverse=True)
        return gaps[:20]  # Return top 20 gaps
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()

def main():
    """Main entry point for documentation graph analysis."""
    parser = argparse.ArgumentParser(description='Analyze generated documentation graphs')
    parser.add_argument('output_dir', help='Path to output directory containing generated graphs')
    parser.add_argument('--search', help='Search query for documentation')
    parser.add_argument('--analyze-node', help='Analyze relationships for a specific node')
    parser.add_argument('--quality-report', action='store_true', help='Generate quality analysis report')
    parser.add_argument('--full-report', help='Generate comprehensive report (specify output filename)')
    
    args = parser.parse_args()
    
    try:
        # Initialize analyzer
        print("Initializing Documentation Graph Analyzer...")
        analyzer = DocumentationGraphAnalyzer(args.output_dir)
        
        # Execute requested operations
        if args.search:
            print(f"\n🔍 Searching for: '{args.search}'")
            results = analyzer.search_documentation(args.search)
            
            print(f"Found {len(results)} results:")
            for i, result in enumerate(results[:10], 1):  # Show top 10
                print(f"\n{i}. {result['node_name']} (score: {result['match_score']})")
                print(f"   Match reasons: {', '.join(result['match_reasons'])}")
                print(f"   Preview: {result['documentation'][:200]}...")
        
        elif args.analyze_node:
            print(f"\n🔍 Analyzing node: '{args.analyze_node}'")
            analysis = analyzer.analyze_node_relationships(args.analyze_node)
            
            if 'error' in analysis:
                print(f"Error: {analysis['error']}")
            else:
                print(f"Node: {analysis['node_info']['name']}")
                print(f"Dependencies: {analysis['documentation_relationships']['dependency_count']}")
                print(f"References: {analysis['documentation_relationships']['reference_count']}")
                
                if analysis['connection_strength']:
                    print("\nTop Connection Strengths:")
                    for target, strength in analysis['connection_strength'].items():
                        print(f"  → {target}: {strength['overall']:.2f}")
        
        elif args.quality_report:
            analyzer.analyze_documentation_quality()
        
        elif args.full_report:
            analyzer.generate_documentation_report(args.full_report)
        
        else:
            # Default: show overview
            print("\n📋 Documentation Graph Overview:")
            quality = analyzer.analyze_documentation_quality()
            
            print(f"\n💡 To explore further:")
            print(f"   --search 'query'           Search documentation")
            print(f"   --analyze-node 'NodeName'  Analyze specific node")
            print(f"   --quality-report           Detailed quality analysis")
            print(f"   --full-report report.json  Comprehensive report")
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()