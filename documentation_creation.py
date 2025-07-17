import asyncio
import os
import pickle
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import networkx as nx

from agent.agent_manager import AgentManager
from agent.workflow_engine import WorkflowEngine
from core.doc_processor import DocumentProcessor
from core.graph_loader import GraphLoader
from core.memory_manager import MemoryManager
from core.similarity_calculator import SimilarityCalculator, SimilarityConfig, VectorType
from core.assignment_engine import AssignmentEngine

class DocumentationOrchestrator:
    """Enhanced orchestrator for graph-based multi-agent documentation generation"""
    
    def __init__(self, output_dir: str = "output", config: Dict[str, Any] = None):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.config = config or {
            "max_docs_per_chunk": 10,
            "max_similar_chunks": 3,
            "similarity_threshold": 0.7,
            "compression_level": "balanced",
            "num_content_agents": 3
        }
        
        # Initialize components
        self.agent_manager = AgentManager(str(self.output_dir / "agents"))
        self.workflow_engine = WorkflowEngine(str(self.output_dir / "workflows"))
        self.graph_loader = GraphLoader()
        
        # Register agent types and handlers
        self._register_agent_types()
        self._register_workflow_handlers()
        
        # State tracking
        self.graph = None
        self.compressed_memory = None
        self.document_chunks = {}
        self.generation_results = {}

    def _register_agent_types(self):
        """Register specialized agent types for documentation generation"""
        
        # Memory Agent Factory
        def create_memory_agent(agent_id: str, config: Dict[str, Any]):
            return MemoryAgent(agent_id, config, self.output_dir)
        
        # Similarity Agent Factory  
        def create_similarity_agent(agent_id: str, config: Dict[str, Any]):
            return SimilarityAgent(agent_id, config, self.output_dir)
        
        # Content Agent Factory
        def create_content_agent(agent_id: str, config: Dict[str, Any]):
            return ContentAgent(agent_id, config, self.output_dir)
        
        self.agent_manager.registry.register_agent_type("memory_agent", create_memory_agent)
        self.agent_manager.registry.register_agent_type("similarity_agent", create_similarity_agent)
        self.agent_manager.registry.register_agent_type("content_agent", create_content_agent)

    def _register_workflow_handlers(self):
        """Register workflow node handlers"""
        
        self.workflow_engine.register_node_handler("initialize_system", self._initialize_system_handler)
        self.workflow_engine.register_node_handler("load_graph", self._load_graph_handler)
        self.workflow_engine.register_node_handler("create_memory", self._create_memory_handler)
        self.workflow_engine.register_node_handler("organize_chunks", self._organize_chunks_handler)
        self.workflow_engine.register_node_handler("generate_content", self._generate_content_handler)
        self.workflow_engine.register_node_handler("finalize_output", self._finalize_output_handler)

    async def generate_documentation(self, 
                                   graph_path: str,
                                   document_ids: List[str] = None) -> Dict[str, Any]:
        """Main method to orchestrate documentation generation"""
        
        print("🚀 Starting Multi-Agent Documentation Generation")
        
        # Create and execute workflow
        workflow_id = self._create_documentation_workflow()
        
        initial_data = {
            "graph_path": graph_path,
            "document_ids": document_ids,
            "output_dir": str(self.output_dir),
            "config": self.config
        }
        
        instance_id = self.workflow_engine.create_workflow_instance(workflow_id, initial_data)
        
        try:
            result = await self.workflow_engine.execute_workflow(instance_id)
            print("✅ Documentation generation completed successfully")
            return result
        except Exception as e:
            print(f"❌ Documentation generation failed: {e}")
            raise

    def _create_documentation_workflow(self) -> str:
        """Create comprehensive documentation workflow"""
        workflow_def = {
            "version": "1.0",
            "description": "Graph-based multi-agent documentation generation",
            "nodes": {
                "initialize_system": {
                    "type": "initialize_system",
                    "params": {"setup_components": True}
                },
                "load_graph": {
                    "type": "load_graph", 
                    "params": {"validate": True, "build_indices": True}
                },
                "create_memory": {
                    "type": "create_memory",
                    "params": {
                        "compression_level": self.config["compression_level"],
                        "traverse_full_graph": True
                    }
                },
                "organize_chunks": {
                    "type": "organize_chunks",
                    "params": {
                        "max_docs_per_chunk": self.config["max_docs_per_chunk"],
                        "max_similar_chunks": self.config["max_similar_chunks"],
                        "similarity_threshold": self.config["similarity_threshold"]
                    }
                },
                "generate_content": {
                    "type": "generate_content",
                    "params": {
                        "num_agents": self.config["num_content_agents"],
                        "use_memory": True,
                        "use_graph_context": True
                    }
                },
                "finalize_output": {
                    "type": "finalize_output",
                    "params": {
                        "formats": ["markdown", "html"],
                        "generate_index": True,
                        "create_summary": True
                    }
                }
            },
            "edges": [
                {"source": "initialize_system", "target": "load_graph"},
                {"source": "load_graph", "target": "create_memory"},
                {"source": "create_memory", "target": "organize_chunks"},
                {"source": "organize_chunks", "target": "generate_content"},
                {"source": "generate_content", "target": "finalize_output"}
            ]
        }
        
        workflow_name = "enhanced_documentation_generation"
        self.workflow_engine.register_workflow(workflow_name, workflow_def)
        return workflow_name

    # Workflow Handler Methods
    
    def _initialize_system_handler(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize system components"""
        print("🔧 Initializing system components...")
        
        workflow_data = input_data["workflow_data"]
        self.config.update(workflow_data.get("config", {}))
        
        # Register agent types
        self.agent_manager.register_agent_types()
        
        return {
            "status": "initialized",
            "config": self.config,
            "components_ready": True
        }

    def _load_graph_handler(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Load and validate graph"""
        print("📊 Loading and validating graph...")
        
        workflow_data = input_data["workflow_data"]
        graph_path = workflow_data["graph_path"]
        
        # Load graph
        self.graph = self.graph_loader.load_graph(graph_path, validate=True)
        
        # Get document IDs if not provided
        document_ids = workflow_data.get("document_ids")
        if not document_ids:
            document_ids = list(self.graph.nodes())
        
        print(f"📈 Loaded graph with {len(self.graph.nodes())} nodes and {len(self.graph.edges())} edges")
        print(f"📋 Processing {len(document_ids)} documents")
        
        return {
            "graph_loaded": True,
            "graph_stats": {
                "nodes": len(self.graph.nodes()),
                "edges": len(self.graph.edges())
            },
            "document_ids": document_ids
        }

    def _create_memory_handler(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create compressed memory from graph"""
        print("🧠 Creating compressed memory from graph...")
        
        workflow_data = input_data["workflow_data"]
        node_data = input_data.get("node_result_load_graph", {})
        
        # Create memory agent
        memory_agent_id = self.agent_manager.registry.create_agent(
            "memory_agent",
            f"memory_agent_{os.getpid()}",
            {"graph": self.graph, "compression_level": workflow_data["params"]["compression_level"]}
        )
        
        # Execute memory creation
        memory_agent = self.agent_manager.registry.get_agent(memory_agent_id)
        memory_result = memory_agent.create_compressed_memory(self.graph)
        
        self.compressed_memory = memory_result["compressed_content"]
        
        print(f"💾 Memory created - Compression ratio: {memory_result.get('compression_ratio', 0):.2f}")
        
        return {
            "memory_created": True,
            "memory_stats": {
                "original_size": memory_result.get("original_size", 0),
                "compressed_size": memory_result.get("compressed_size", 0),
                "compression_ratio": memory_result.get("compression_ratio", 0)
            },
            "compressed_memory": self.compressed_memory
        }

    def _organize_chunks_handler(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Organize documents into similarity-based chunks"""
        print("🔗 Organizing documents into similarity-based chunks...")
        
        workflow_data = input_data["workflow_data"]
        memory_data = input_data.get("node_result_create_memory", {})
        graph_data = input_data.get("node_result_load_graph", {})
        
        document_ids = graph_data.get("document_ids", [])
        
        # Create similarity agent
        similarity_agent_id = self.agent_manager.registry.create_agent(
            "similarity_agent",
            f"similarity_agent_{os.getpid()}",
            {
                "graph": self.graph,
                "memory": self.compressed_memory,
                "max_docs_per_chunk": workflow_data["params"]["max_docs_per_chunk"],
                "max_similar_chunks": workflow_data["params"]["max_similar_chunks"],
                "similarity_threshold": workflow_data["params"]["similarity_threshold"]
            }
        )
        
        # Execute chunking
        similarity_agent = self.agent_manager.registry.get_agent(similarity_agent_id)
        chunking_result = similarity_agent.organize_documents(document_ids)
        
        self.document_chunks = chunking_result["chunks"]
        
        print(f"📦 Created {len(self.document_chunks)} chunks")
        for i, chunk in enumerate(self.document_chunks):
            print(f"   Chunk {i+1}: {len(chunk['documents'])} documents")
        
        return {
            "chunks_created": True,
            "chunk_stats": {
                "total_chunks": len(self.document_chunks),
                "documents_per_chunk": [len(chunk["documents"]) for chunk in self.document_chunks]
            },
            "chunks": self.document_chunks
        }

    def _generate_content_handler(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate content using multiple agents"""
        print("✍️ Generating content with multiple agents...")
        
        workflow_data = input_data["workflow_data"]
        chunk_data = input_data.get("node_result_organize_chunks", {})
        
        chunks = chunk_data.get("chunks", [])
        num_agents = workflow_data["params"]["num_agents"]
        
        # Create content agents
        content_agents = []
        for i in range(num_agents):
            agent_id = self.agent_manager.registry.create_agent(
                "content_agent",
                f"content_agent_{i}_{os.getpid()}",
                {
                    "graph": self.graph,
                    "memory": self.compressed_memory,
                    "agent_id": i
                }
            )
            content_agents.append(agent_id)
        
        # Distribute chunks across agents
        generation_results = {}
        
        for i, chunk in enumerate(chunks):
            agent_id = content_agents[i % len(content_agents)]
            agent = self.agent_manager.registry.get_agent(agent_id)
            
            print(f"   🤖 Agent {i % len(content_agents)} processing chunk {i+1}")
            
            result = agent.generate_content(chunk, self.compressed_memory)
            generation_results[f"chunk_{i}"] = result
        
        self.generation_results = generation_results
        
        print(f"📝 Generated content for {len(generation_results)} chunks")
        
        return {
            "content_generated": True,
            "generation_stats": {
                "chunks_processed": len(generation_results),
                "agents_used": len(content_agents)
            },
            "results": generation_results
        }

    def _finalize_output_handler(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Finalize and format output"""
        print("📄 Finalizing output...")
        
        workflow_data = input_data["workflow_data"]
        content_data = input_data.get("node_result_generate_content", {})
        
        results = content_data.get("results", {})
        formats = workflow_data["params"]["formats"]
        
        # Create final documentation
        output_files = {}
        
        for format_type in formats:
            if format_type == "markdown":
                output_files["markdown"] = self._create_markdown_output(results)
            elif format_type == "html":
                output_files["html"] = self._create_html_output(results)
        
        # Generate index if requested
        if workflow_data["params"].get("generate_index", False):
            output_files["index"] = self._create_index_file(results)
        
        # Create summary if requested
        if workflow_data["params"].get("create_summary", False):
            output_files["summary"] = self._create_summary_file(results)
        
        print(f"📁 Created output files: {list(output_files.keys())}")
        
        return {
            "finalization_complete": True,
            "output_files": output_files,
            "total_content_size": sum(len(str(content)) for content in results.values())
        }

    def _create_markdown_output(self, results: Dict[str, Any]) -> str:
        """Create consolidated markdown output"""
        output_path = self.output_dir / "enhanced_documentation.md"
        
        content_parts = [
            "# Enhanced Documentation",
            f"\n*Generated with Multi-Agent System*\n",
            f"**Total Chunks:** {len(results)}",
            f"**Memory Compression:** {getattr(self, 'compressed_memory', 'N/A') is not None}",
            "\n---\n"
        ]
        
        for chunk_id, chunk_result in results.items():
            content_parts.append(f"\n## {chunk_id.replace('_', ' ').title()}\n")
            content_parts.append(chunk_result.get("content", "No content generated"))
            content_parts.append("\n---\n")
        
        final_content = "\n".join(content_parts)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(final_content)
        
        return str(output_path)

    def _create_html_output(self, results: Dict[str, Any]) -> str:
        """Create HTML output with enhanced styling"""
        # Implementation similar to markdown but with HTML formatting
        output_path = self.output_dir / "enhanced_documentation.html"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Enhanced Documentation</title>
            <style>
                body {{ font-family: system-ui; margin: 40px; line-height: 1.6; }}
                .chunk {{ border: 1px solid #ddd; padding: 20px; margin: 20px 0; border-radius: 5px; }}
                .stats {{ background: #f5f5f5; padding: 10px; border-radius: 3px; }}
            </style>
        </head>
        <body>
            <h1>Enhanced Documentation</h1>
            <div class="stats">
                <p><strong>Total Chunks:</strong> {len(results)}</p>
                <p><strong>Generated with:</strong> Multi-Agent System</p>
            </div>
        """
        
        for chunk_id, chunk_result in results.items():
            html_content += f"""
            <div class="chunk">
                <h2>{chunk_id.replace('_', ' ').title()}</h2>
                <div>{chunk_result.get("content", "No content generated")}</div>
            </div>
            """
        
        html_content += "</body></html>"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(output_path)

    def _create_index_file(self, results: Dict[str, Any]) -> str:
        """Create index file listing all generated content"""
        output_path = self.output_dir / "index.md"
        
        index_content = [
            "# Documentation Index\n",
            "## Generated Chunks\n"
        ]
        
        for chunk_id, chunk_result in results.items():
            index_content.append(f"- [{chunk_id.replace('_', ' ').title()}](#chunk-{chunk_id})")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(index_content))
        
        return str(output_path)

    def _create_summary_file(self, results: Dict[str, Any]) -> str:
        """Create summary of generation process"""
        output_path = self.output_dir / "generation_summary.json"
        
        summary = {
            "generation_timestamp": str(datetime.now()),
            "total_chunks": len(results),
            "memory_compression_used": self.compressed_memory is not None,
            "config": self.config,
            "chunks_summary": {
                chunk_id: {
                    "content_length": len(chunk_result.get("content", "")),
                    "generation_time": chunk_result.get("generation_time", "unknown")
                }
                for chunk_id, chunk_result in results.items()
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        
        return str(output_path)


# Agent Classes (simplified implementations)

class MemoryAgent:
    def __init__(self, agent_id: str, config: Dict[str, Any], output_dir: Path):
        self.agent_id = agent_id
        self.config = config
        self.output_dir = output_dir
    
    def create_compressed_memory(self, graph: nx.MultiDiGraph) -> Dict[str, Any]:
        # Implementation for memory compression
        from core.compression_engine import DocumentationCompressor, CompressionLevel
        
        compressor = DocumentationCompressor()
        
        # Extract graph content
        graph_content = self._extract_graph_overview(graph)
        
        # Compress
        result = compressor.compress_documentation(
            graph_content, 
            CompressionLevel.BALANCED,
            "graph_memory"
        )
        
        return {
            "compressed_content": result.compressed_content,
            "original_size": result.original_size,
            "compressed_size": result.compressed_size,
            "compression_ratio": result.compression_ratio
        }
    
    def _extract_graph_overview(self, graph: nx.MultiDiGraph) -> str:
        content_parts = []
        for node in list(graph.nodes())[:100]:  # Limit for memory
            neighbors = list(graph.neighbors(node))
            content_parts.append(f"Node: {node}, Connections: {len(neighbors)}")
        return "\n".join(content_parts)


class SimilarityAgent:
    def __init__(self, agent_id: str, config: Dict[str, Any], output_dir: Path):
        self.agent_id = agent_id
        self.config = config
        self.output_dir = output_dir
    
    def organize_documents(self, document_ids: List[str]) -> Dict[str, Any]:
        # Simplified similarity-based chunking
        chunks = []
        max_docs = self.config.get("max_docs_per_chunk", 10)
        
        # Group documents into chunks of max_docs
        for i in range(0, len(document_ids), max_docs):
            chunk_docs = document_ids[i:i + max_docs]
            chunks.append({
                "documents": chunk_docs,
                "similarity_scores": {doc: 0.8 for doc in chunk_docs}  # Placeholder
            })
        
        return {"chunks": chunks}


class ContentAgent:
    def __init__(self, agent_id: str, config: Dict[str, Any], output_dir: Path):
        self.agent_id = agent_id
        self.config = config
        self.output_dir = output_dir

    def generate_content(self, chunk: Dict[str, Any], memory: str) -> Dict[str, Any]:
        documents = chunk.get("documents", [])
        
        # Load actual documentation from CalculatorCode
        doc_path = Path("output/CalculatorCode/documentation")
        content_parts = []
        
        for doc_id in documents:
            md_file = doc_path / f"{doc_id.replace('.', '-').replace('::', '-')}.md"
            if md_file.exists():
                with open(md_file, 'r', encoding='utf-8') as f:
                    content_parts.append(f.read())
            else:
                content_parts.append(f"## {doc_id}\nNo documentation found.")
        
        final_content = "\n\n---\n\n".join(content_parts)
        
        # Save to output
        output_file = self.output_dir / f"chunk_{self.agent_id}.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(final_content)
        
        return {"content": final_content, "file": str(output_file)}

# Main execution functions

async def main():
    """Enhanced main function with better configuration and error handling"""
    
    # Configuration
    config = {
        "max_docs_per_chunk": 10,
        "max_similar_chunks": 3, 
        "similarity_threshold": 0.7,
        "compression_level": "balanced",
        "num_content_agents": 3
    }
    
    # Initialize orchestrator
    orchestrator = DocumentationOrchestrator(
        output_dir="output/enhanced_documentation",
        config=config
    )
    
    try:
        # Generate documentation
        result = await orchestrator.generate_documentation(
            graph_path="output/CalculatorCode/conceptual_graph.pkl",  # Adjust path as needed
            document_ids=None  # Will use all nodes from graph
        )
        
        print("\n🎉 Documentation Generation Complete!")
        print(f"📊 Results: {result}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error during documentation generation: {e}")
        raise

    import threading
    for thread in threading.enumerate():
        if thread != threading.current_thread():
            thread.daemon = True


def run_documentation_generation():
    """Simplified synchronous wrapper"""
    return asyncio.run(main())


# Entry point
if __name__ == "__main__":
    result = run_documentation_generation()
    print(f"\n✅ Final Result: {result}")