import os
import networkx as nx
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Set, Tuple
from datetime import datetime
import hashlib
import re
from tqdm import tqdm
import re
# Import our components
from core.chunk_manager import ChunkManager, ChunkState
from core.similarity_calculator import SimilarityCalculator, SimilarityConfig, SimilarityMetric, VectorType
from core.assignment_engine import AssignmentEngine, AssignmentStrategy
from core.memory_manager import MemoryManager
from core.compression_engine import CompressionLevel


class DocumentProcessor:
    """
    Main processor that orchestrates the documentation processing pipeline.
    Integrates ChunkManager, SimilarityCalculator, and AssignmentEngine.
    """
    
    def __init__(self, output_dir: str = None, config: Dict = None):
        """
        Initialize the document processor.
        
        Args:
            output_dir: Path to the output directory containing graphs and docs
            config: Configuration dictionary
        """
        self.config = config or {
            "chunk_size": 30,  # Default max docs per chunk
            "similarity_threshold": 0.6,
            "assignment_strategy": "hybrid",
            "data_dir": "processor_data",
            "include_metadata": True,
            "use_advanced_models": False  # Set to True to use SentenceBERT if available
        }
        
        # Set data directory
        self.data_dir = Path(self.config["data_dir"])
        self.data_dir.mkdir(exist_ok=True)
        
        # Set output directory
        self.output_dir = Path(output_dir) if output_dir else None
        
        # Initialize components
        self._init_components()
        
        # Document cache (id -> content)
        self.doc_cache = {}
        
        # Graph data from output
        self.conceptual_graph = None
        self.documentation_graph = None
        self.documentation_data = None
        self.memory_manager = MemoryManager(str(self.data_dir / "memory"))
        self.graph_memory = None
        self.similarity_threshold = 0.7
        self.max_docs_per_chunk = 10
        self.max_similar_chunks = 3
        
        # Load data if output_dir is provided
        if self.output_dir:
            self._load_output_data()
    
    def _init_components(self):
        """Initialize the processing components"""
        # Initialize ChunkManager
        self.chunk_manager = ChunkManager(
            storage_path=str(self.data_dir / "chunks")
        )
        
        # Initialize SimilarityCalculator with appropriate config
        sim_config = SimilarityConfig(
            metrics=[SimilarityMetric.COSINE, SimilarityMetric.JACCARD],
            vector_type=VectorType.SENTENCE_BERT if self.config["use_advanced_models"] else VectorType.TFIDF,
            min_similarity=self.config["similarity_threshold"],
            include_metadata=self.config["include_metadata"]
        )
        
        self.similarity_calculator = SimilarityCalculator(
            storage_path=str(self.data_dir / "similarity"),
            config=sim_config
        )
        
        # Initialize AssignmentEngine
        self.assignment_engine = AssignmentEngine(
            storage_path=str(self.data_dir / "assignments"),
            chunk_manager=self.chunk_manager,
            similarity_calculator=self.similarity_calculator
        )
        
        # Update engine config
        self.assignment_engine.config.update({
            "default_strategy": AssignmentStrategy(self.config["assignment_strategy"]),
            "similarity_threshold": self.config["similarity_threshold"],
            "max_chunk_assignments": self.config["chunk_size"]
        })
    def _to_anchor(text: str) -> str:
        """Convert text to a valid anchor ID"""
        return re.sub(r'[^a-zA-Z0-9_-]', '-', text.lower())
    
    def create_graph_memory(self) -> Dict[str, Any]:
        """Create compressed memory from entire graph traversal"""
        if not self.documentation_graph:
            return {"error": "No documentation graph available"}
        
        # Traverse entire graph to understand structure
        graph_content = self._extract_full_graph_content()
        
        # Compress into memory using aggressive compression
        memory_result = self.memory_manager.compressor.compress_documentation(
            graph_content, CompressionLevel.BALANCED, "graph_overview"
        )
        
        # Store compressed memory
        self.graph_memory = memory_result.compressed_content
        
        return {
            "original_size": memory_result.original_size,
            "compressed_size": memory_result.compressed_size,
            "compression_ratio": memory_result.compression_ratio
        }

    def _extract_full_graph_content(self) -> str:
        """Extract content from entire graph for memory creation"""
        content_parts = []
        
        # Get all nodes and their relationships
        for node in self.documentation_graph.nodes():
            if node in self.documentation_data:
                doc_content = self.documentation_data[node].get('documentation', '')
                connections = list(self.documentation_graph.neighbors(node))
                
                summary = f"Node: {node}\nConnections: {connections}\nContent: {doc_content[:200]}..."
                content_parts.append(summary)
        
        return "\n\n".join(content_parts)

    def _load_output_data(self):
        """Load data from output directory"""
        if not self.output_dir or not self.output_dir.exists():
            print(f"Output directory not found: {self.output_dir}")
            return
        
        # Load conceptual graph
        conceptual_graph_path = self.output_dir / "conceptual_graph.pkl"
        if conceptual_graph_path.exists():
            try:
                import pickle
                with open(conceptual_graph_path, 'rb') as f:
                    self.conceptual_graph = pickle.load(f)
                print(f"Loaded conceptual graph: {len(self.conceptual_graph.nodes())} nodes")
            except Exception as e:
                print(f"Error loading conceptual graph: {e}")
        
        # Load documentation graph
        doc_graph_path = self.output_dir / "documentation_graph.pkl"
        if doc_graph_path.exists():
            try:
                import pickle
                with open(doc_graph_path, 'rb') as f:
                    self.documentation_graph = pickle.load(f)
                print(f"Loaded documentation graph: {len(self.documentation_graph.nodes())} nodes")
            except Exception as e:
                print(f"Error loading documentation graph: {e}")
        
        # Load documentation data
        doc_data_path = self.output_dir / "documentation_and_graph_data.json"
        if doc_data_path.exists():
            try:
                with open(doc_data_path, 'r', encoding='utf-8') as f:
                    self.documentation_data = json.load(f)
                print(f"Loaded documentation data: {len(self.documentation_data)} entries")
            except Exception as e:
                print(f"Error loading documentation data: {e}")
        
        # Load markdown documents
        self.markdown_docs = {}
        markdown_dir = self.output_dir / "documentation"
        if markdown_dir.exists():
            md_files = list(markdown_dir.glob("*.md"))
            print(f"Found {len(md_files)} markdown files")
            
            for md_path in md_files:
                try:
                    with open(md_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Extract node name from filename or content
                    node_name = self._extract_node_name(md_path, content)
                    if node_name:
                        self.markdown_docs[node_name] = {
                            "path": str(md_path),
                            "content": content
                        }
                except Exception as e:
                    print(f"Error loading markdown file {md_path}: {e}")
    
    def _extract_node_name(self, file_path: Path, content: str) -> Optional[str]:
        """Extract node name from markdown file"""
        # Try to extract from content first (better)
        name_match = re.search(r'^# Documentation for `([^`]+)`', content)
        if name_match:
            return name_match.group(1)
        
        # Fall back to filename
        filename = file_path.stem
        # Convert to something that might be a node name
        possible_name = filename.replace('-', '.').replace('_', '.')
        
        # Check if this name exists in our graphs
        if self.documentation_graph and possible_name in self.documentation_graph:
            return possible_name
        
        if self.conceptual_graph and possible_name in self.conceptual_graph:
            return possible_name
        
        # Last resort: just return the filename
        return filename
    
    def process_documentation(self) -> Dict[str, Any]:
        """
        Process all documentation and create chunks.
        
        Returns:
            Processing statistics and results
        """
        if not self.markdown_docs:
            print("No markdown documents found. Call _load_output_data() first.")
            return {"error": "No markdown documents found"}
        
        print(f"Processing {len(self.markdown_docs)} markdown documents...")
        
        # 1. Prepare document metadata
        documents = []
        
        for node_name, doc_info in self.markdown_docs.items():
            # Create document ID
            doc_id = hashlib.md5(node_name.encode()).hexdigest()[:16]
            
            # Extract metadata
            metadata = self._extract_metadata(node_name, doc_info["content"])
            
            documents.append({
                "id": doc_id,
                "node_name": node_name,
                "content": doc_info["content"],
                "metadata": metadata
            })
        
        # 2. Calculate similarity between documents
        print("Calculating document similarities...")
        doc_ids = [doc["id"] for doc in documents]
        
        # Cache document content for similarity calculator
        for doc in documents:
            self.similarity_calculator.doc_cache[doc["id"]] = {
                "id": doc["id"],
                "content": doc["content"],
                "metadata": doc["metadata"]
            }
        
        # Build similarity matrix
        similarity_matrix = self.similarity_calculator.build_similarity_matrix(doc_ids)
        print(f"Generated similarity matrix with {len(similarity_matrix)} connections")
        
        # 3. Cluster documents into initial groups
        print("Clustering documents...")
        optimal_clusters = min(max(len(documents) // self.config["chunk_size"], 1), 10)
        clusters = self.similarity_calculator.cluster_documents(
            doc_ids, 
            num_clusters=optimal_clusters
        )
        
        print(f"Created {len(clusters)} document clusters")
        
        # 4. Create chunks for each cluster
        print("Creating document chunks...")
        chunks = []
        
        for i, cluster in enumerate(clusters):
            # Create chunk
            chunk_id = self.chunk_manager.create_chunk(
                initial_docs=[],  # Start empty
                capacity=self.config["chunk_size"],
                tags=["auto_generated", f"cluster_{i}"]
            )
            
            chunks.append(chunk_id)
        
        # 5. Assign documents to chunks
        print("Assigning documents to chunks...")
        assignments = self.assignment_engine.bulk_assign_documents(
            doc_ids,
            strategy=AssignmentStrategy(self.config["assignment_strategy"]),
            metadata={"source": "initial_processing"}
        )
        
        # 6. Optimize assignments if needed
        print("Optimizing document assignments...")
        optimization_results = self.assignment_engine.optimize_assignments(
            target_chunks=chunks,
            strategy=AssignmentStrategy.HYBRID
        )
        
        # 7. Detect and resolve conflicts
        print("Checking for assignment conflicts...")
        conflicts = self.assignment_engine.detect_conflicts()
        
        if conflicts:
            print(f"Resolving {len(conflicts)} assignment conflicts...")
            resolution_results = self.assignment_engine.resolve_conflicts(conflicts)
        else:
            resolution_results = {"message": "No conflicts to resolve"}
        
        # 8. Build documentation content for each chunk
        print("Building documentation content for each chunk...")
        chunk_contents = self._build_chunk_documentation(chunks, documents)
        
        # Return results
        return {
            "documents_processed": len(documents),
            "chunks_created": len(chunks),
            "similarity_connections": len(similarity_matrix),
            "assignments": {
                "total": len(assignments),
                "by_status": self.assignment_engine.get_assignment_stats()["by_status"]
            },
            "optimization": optimization_results,
            "conflicts": {
                "detected": len(conflicts),
                "resolution": resolution_results
            },
            "chunks": chunk_contents
        }
    
    def _extract_metadata(self, node_name: str, content: str) -> Dict[str, Any]:
        """Extract metadata from node and content"""
        metadata = {
            "node_name": node_name,
            "tags": [],
            "type": "unknown",
            "category": "unknown",
            "confidence": 1.0
        }
        
        # Try to extract from documentation data
        if self.documentation_data and node_name in self.documentation_data:
            node_data = self.documentation_data[node_name]
            
            # Extract conceptual data
            if "conceptual_data" in node_data and isinstance(node_data["conceptual_data"], dict):
                conceptual = node_data["conceptual_data"]
                
                if "semantic_metadata" in conceptual:
                    semantic = conceptual["semantic_metadata"]
                    
                    if "type" in semantic:
                        metadata["type"] = semantic["type"]
                    
                    if "label" in semantic:
                        metadata["tags"].append(semantic["label"])
            
            # Extract context metadata
            if "context_metadata" in node_data and isinstance(node_data["context_metadata"], dict):
                context = node_data["context_metadata"]
                
                if "average_confidence" in context:
                    metadata["confidence"] = context["average_confidence"]
        
        # Try to extract from documentation graph
        if self.documentation_graph and node_name in self.documentation_graph:
            node_attrs = self.documentation_graph.nodes[node_name]
            
            if "category" in node_attrs:
                metadata["category"] = node_attrs["category"]
            
            if "original_category" in node_attrs:
                metadata["tags"].append(node_attrs["original_category"])
            
            if "fname" in node_attrs:
                metadata["file"] = node_attrs["fname"]
        
        # Extract from content
        # Extract quality notice
        quality_match = re.search(r'Quality Notice.*?(\d+%)', content, re.IGNORECASE)
        if quality_match:
            try:
                confidence_str = quality_match.group(1).replace('%', '')
                metadata["confidence"] = float(confidence_str) / 100.0
            except:
                pass
        
        # Remove duplicates from tags
        metadata["tags"] = list(set(metadata["tags"]))
        
        return metadata

    def _get_component_summary(self, component: str) -> str:
        """Get concise summary of component"""
        if component in self.documentation_data:
            conceptual = self.documentation_data[component].get('conceptual_data', {})
            semantic = conceptual.get('semantic_metadata', {})
            return semantic.get('summary', f"Component: {component}")
        return f"Component: {component}"

    def _save_documentation(self, content: str, filename: str):
        """Save documentation to CreatedFile directory"""
        output_dir = "CreatedFile"
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Documentation saved to {output_path}")

    def _build_chunk_documentation(self, chunk_ids: List[str], documents: List[Dict]) -> Dict[str, Any]:
        """
        Build documentation content for each chunk.
        """
        results = {}
        
        # Build lookup for documents
        doc_lookup = {doc["id"]: doc for doc in documents}
        
        for chunk_id in chunk_ids:
            chunk = self.chunk_manager.get_chunk(chunk_id)
            if not chunk:
                continue
            
            # Get assignments for this chunk
            assignments = self.assignment_engine.get_chunk_assignments(chunk_id)
            
            # Debug print to see what's happening
            print(f"Chunk {chunk_id}: {len(assignments)} assignments")
            
            # If no assignments, check if chunk has documents directly
            if not assignments and chunk.document_ids:
                # Fallback: use documents directly from chunk
                chunk_docs = []
                for doc_id in chunk.document_ids:
                    if doc_id in doc_lookup:
                        chunk_docs.append(doc_lookup[doc_id])
            else:
                # Collect documents from assignments
                chunk_docs = []
                for assignment in assignments:
                    doc_id = assignment.document_id
                    if doc_id in doc_lookup:
                        chunk_docs.append(doc_lookup[doc_id])
            
            # Generate content even if no docs (with empty message)
            content = self._generate_chunk_content(chunk, chunk_docs)
            
            results[chunk_id] = {
                "document_count": len(chunk_docs),
                "state": chunk.state.value,
                "content": content
            }
        
        return results

    def _generate_chunk_content(self, chunk, documents: List[Dict]) -> str:
        """Generate content for a chunk"""
        if not documents:
            return "No documents in this chunk."
        
        # Sort documents by type and name
        documents.sort(key=lambda d: (d["metadata"].get("type", ""), d["node_name"]))
        
        # Generate table of contents
        toc = ["# Documentation Chunk\n\n## Table of Contents\n"]
        
        for i, doc in enumerate(documents, 1):
            node_name = doc["node_name"]
            node_type = doc["metadata"].get("type", "Unknown")
            toc.append(f"{i}. [{node_name}](#{_to_anchor(node_name)}) - {node_type}")
        
        toc.append("\n---\n")
        
        # Generate content sections
        sections = []
        
        for doc in documents:
            node_name = doc["node_name"]
            content = doc["content"]
            
            # Add anchor and divider
            sections.append(f"<a id='{_to_anchor(node_name)}'></a>\n\n{content}\n\n---\n")
        
        # Generate metadata section
        metadata = ["\n## Chunk Metadata\n"]
        metadata.append(f"- **Chunk ID**: {chunk.chunk_id}")
        metadata.append(f"- **Documents**: {len(documents)}/{chunk.capacity}")
        metadata.append(f"- **State**: {chunk.state.value}")
        metadata.append(f"- **Created**: {chunk.created_at}")
        
        if chunk.tags:
            metadata.append(f"- **Tags**: {', '.join(chunk.tags)}")
        
        # Combine all sections
        return "\n".join(toc + sections + metadata)
    
    def generate_technical_documentation(self, output_file: str = None) -> str:
        """
        Generate comprehensive technical documentation from chunks.
        
        Args:
            output_file: Optional file to write documentation to
            
        Returns:
            Generated documentation content
        """
        # Get all active chunks
        active_chunks = self.chunk_manager.find_chunks_by_state(ChunkState.ACTIVE)
        
        if not active_chunks:
            return "No active documentation chunks found."
        
        # Get chunk contents
        chunk_contents = {}
        
        for chunk_id in active_chunks:
            content = self.chunk_manager.get_chunk_content(chunk_id)
            if content:
                chunk_contents[chunk_id] = content
        
        # Build documentation
        doc_parts = [
            "# Technical Documentation\n\n",
            f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n\n",
            "## Overview\n\n"
        ]
        
        # Get overview from conceptual graph
        if self.conceptual_graph:
            # Find most central nodes
            try:
                centrality = nx.betweenness_centrality(self.conceptual_graph)
                top_nodes = sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:5]
                
                doc_parts.append("This documentation covers the following key components:\n\n")
                
                for node, _ in top_nodes:
                    if node in self.documentation_data:
                        node_data = self.documentation_data[node]
                        if "conceptual_data" in node_data and "semantic_metadata" in node_data["conceptual_data"]:
                            semantic = node_data["conceptual_data"]["semantic_metadata"]
                            if "summary" in semantic:
                                doc_parts.append(f"- **{node}**: {semantic['summary']}\n")
                            else:
                                doc_parts.append(f"- **{node}**\n")
                        else:
                            doc_parts.append(f"- **{node}**\n")
            except:
                # Fall back to simple overview
                doc_parts.append(f"This documentation covers {len(self.documentation_data)} components.\n\n")
        
        # Add table of contents
        doc_parts.append("\n## Table of Contents\n\n")
        
        # Group chunks by similarity group or tags
        chunk_groups = {}
        
        for chunk_id, content in chunk_contents.items():
            chunk = self.chunk_manager.get_chunk(chunk_id)
            
            if not chunk:
                continue
                
            group_key = chunk.similarity_group or "default"
            
            if group_key not in chunk_groups:
                chunk_groups[group_key] = []
            
            chunk_groups[group_key].append((chunk_id, chunk))
        
        # Generate TOC entries
        for i, (group_key, chunks) in enumerate(chunk_groups.items(), 1):
            doc_parts.append(f"{i}. [{group_key.replace('_', ' ').title()}](#{_to_anchor(group_key)})\n")
            
            for j, (chunk_id, chunk) in enumerate(chunks, 1):
                doc_parts.append(f"   {i}.{j}. [Chunk {j}](#{_to_anchor(chunk_id)})\n")
        
        # Add content for each group
        for group_key, chunks in chunk_groups.items():
            doc_parts.append(f"\n<a id='{_to_anchor(group_key)}'></a>\n")
            doc_parts.append(f"## {group_key.replace('_', ' ').title()}\n\n")
            
            for j, (chunk_id, chunk) in enumerate(chunks, 1):
                doc_parts.append(f"<a id='{_to_anchor(chunk_id)}'></a>\n")
                doc_parts.append(f"### Chunk {j}\n\n")
                
                # Add chunk content
                if chunk_id in chunk_contents:
                    content = chunk_contents[chunk_id]
                    
                    if isinstance(content, dict) and "documents" in content:
                        # Format document list
                        doc_parts.append("This chunk contains the following documents:\n\n")
                        
                        for doc in content["documents"]:
                            doc_title = doc.get("title", doc.get("id", "Untitled"))
                            doc_parts.append(f"- **{doc_title}**\n")
                        
                        doc_parts.append("\n")
                    else:
                        # Raw content
                        doc_parts.append(str(content))
                
                doc_parts.append("\n---\n\n")
        
        # Build final documentation
        documentation = "".join(doc_parts)
        
        # Write to file if requested
        if output_file:
            output_path = self.data_dir / output_file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(documentation)
            print(f"Documentation written to {output_path}")
        
        return documentation
    def _analyze_architectural_layers(self) -> Dict[str, List[str]]:
        """Analyze components by architectural layer"""
        layers = {"presentation": [], "business": [], "data": [], "utility": [], "infrastructure": []}
        
        for node in self.conceptual_graph.nodes():
            if node in self.documentation_data:
                node_data = self.documentation_data[node].get('conceptual_data', {})
                semantic = node_data.get('semantic_metadata', {})
                layer = semantic.get('layer', 'utility')
                layers.get(layer, layers['utility']).append(node)
        
        return {k: v for k, v in layers.items() if v}  # Remove empty layers
def generate_architectural_documentation(self, output_file: str = None) -> str:
    """Generate comprehensive architectural documentation"""
    if not self.conceptual_graph:
        return "No conceptual graph loaded."
    
    # Analyze architectural layers and patterns
    layers = self._analyze_architectural_layers()
    patterns = self._identify_design_patterns()
    components = self._categorize_components()
    
    doc_parts = [
        "# System Architecture Documentation\n\n",
        f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n\n",
        
        "## Executive Summary\n",
        f"This system consists of {len(self.conceptual_graph.nodes())} components organized across ",
        f"{len(layers)} architectural layers with {len(self.conceptual_graph.edges())} documented relationships.\n\n",
        
        "## Architectural Overview\n\n",
        "### System Layers\n"
    ]
    
    # Document each layer
    for layer_name, layer_components in layers.items():
        doc_parts.append(f"#### {layer_name.title()} Layer\n")
        doc_parts.append(f"**Components**: {len(layer_components)}\n")
        doc_parts.append(f"**Responsibility**: {self._get_layer_responsibility(layer_name)}\n\n")
        
        for component in layer_components[:5]:  # Top 5 components
            if component in self.documentation_data:
                doc_parts.append(f"- **{component}**: {self._get_component_summary(component)}\n")
        doc_parts.append("\n")
    
    # Add component details by category
    doc_parts.append("## Component Catalog\n\n")
    for category, comps in components.items():
        doc_parts.append(f"### {category} Components\n\n")
        for comp in comps:
            summary = self._get_component_summary(comp)
            dependencies = list(self.conceptual_graph.successors(comp))[:3]
            doc_parts.append(f"#### {comp}\n")
            doc_parts.append(f"{summary}\n\n")
            if dependencies:
                doc_parts.append(f"**Key Dependencies**: {', '.join(dependencies)}\n\n")
    
    # Save and return
    documentation = "".join(doc_parts)
    if output_file:
        self._save_documentation(documentation, output_file)
    return documentation

# Helper function to convert text to a valid anchor
def _to_anchor(text: str) -> str:
    """Convert text to a valid anchor ID"""
    return re.sub(r'[^a-zA-Z0-9_-]', '-', text.lower())