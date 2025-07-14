# core/doc_generator_integration.py

from typing import Dict, Any, List, Optional
import networkx as nx
from pathlib import Path

from core.content_generator import ContentGenerator
from core.chunk_updater import ChunkUpdater
from core.output_formatter import OutputFormatter
from core.doc_processor import DocumentProcessor

class DocumentationGeneratorSystem:
    """Integrates content generation, chunk updates, and output formatting"""
    
    def __init__(self, 
                 output_dir: str,
                 doc_processor: Optional[DocumentProcessor] = None,
                 config: Dict[str, Any] = None):
        """
        Initialize the documentation generator system
        
        Args:
            output_dir: Path to output directory with graphs and docs
            doc_processor: Existing DocumentProcessor instance or None
            config: Configuration dictionary
        """
        self.output_dir = Path(output_dir)
        
        # Initialize or use provided doc processor
        if doc_processor:
            self.doc_processor = doc_processor
        else:
            self.doc_processor = DocumentProcessor(output_dir=str(self.output_dir), config=config)
        
        # Initialize components
        self.content_generator = ContentGenerator(
            llm_config=config.get('llm_config') if config else None
        )
        
        self.chunk_updater = ChunkUpdater(
            chunk_manager=self.doc_processor.chunk_manager
        )
        
        self.output_formatter = OutputFormatter(
            documentation_graph=self.doc_processor.documentation_graph,
            output_dir=str(self.output_dir / "formatted_docs")
        )
    
    def process_and_format(self, 
                          output_formats: List[str] = ["markdown", "html"],
                          generate_index: bool = True) -> Dict[str, Any]:
        """
        Process documentation and generate formatted outputs
        
        Args:
            output_formats: List of output formats to generate
            generate_index: Whether to generate index pages
            
        Returns:
            Dictionary with results and output paths
        """
        # Process documentation (reusing existing code)
        processing_results = self.doc_processor.process_documentation()
        
        # Generate output documents
        output_paths = {}
        documents = []
        
        # Extract chunks for formatting
        chunks = processing_results.get('chunks', {})
        for chunk_id, chunk_data in chunks.items():
            # Convert chunk to document format for formatter
            document = {
                "title": f"Documentation Chunk {chunk_id}",
                "sections": []
            }
            
            # Extract content from chunk
            content = chunk_data.get('content', '')
            
            # Parse content into sections (simplified)
            section = {
                "title": "Content",
                "content": content
            }
            document["sections"].append(section)
            documents.append(document)
        
        # Format in each requested format
        for output_format in output_formats:
            paths = self.output_formatter.format_multiple_documents(
                documents,
                output_format=output_format
            )
            output_paths[output_format] = paths
            
            # Generate index if requested
            if generate_index:
                index_path = self.output_formatter.generate_index(
                    documents,
                    output_format=output_format
                )
                output_paths[f"{output_format}_index"] = index_path
        
        return {
            "processing_results": processing_results,
            "output_paths": output_paths,
            "document_count": len(documents)
        }
    
    def update_chunk(self, 
                    chunk_id: str, 
                    updated_content: str) -> Dict[str, Any]:
        """
        Update a documentation chunk and regenerate outputs
        
        Args:
            chunk_id: ID of the chunk to update
            updated_content: New content for the chunk
            
        Returns:
            Update results
        """
        # Update the chunk
        update_result = self.chunk_updater.update_chunk(chunk_id, updated_content)
        
        if update_result.get('success', False):
            # Regenerate formatted outputs for this chunk
            chunk_data = self.doc_processor.chunk_manager.get_chunk(chunk_id)
            
            if chunk_data:
                document = {
                    "title": f"Documentation Chunk {chunk_id}",
                    "sections": [
                        {
                            "title": "Content",
                            "content": updated_content
                        }
                    ]
                }
                
                # Regenerate in both formats
                output_paths = {}
                for output_format in ["markdown", "html"]:
                    path = self.output_formatter.format_document(
                        document,
                        output_format=output_format,
                        filename=f"chunk_{chunk_id}.{output_format}"
                    )
                    output_paths[output_format] = path
                
                update_result["output_paths"] = output_paths
        
        return update_result
    
    def generate_custom_content(self, 
                              template_id: str,
                              variables: Dict[str, Any],
                              output_format: str = "markdown") -> Dict[str, Any]:
        """
        Generate custom content using templates
        
        Args:
            template_id: Template identifier
            variables: Template variables
            output_format: Output format
            
        Returns:
            Generation results
        """
        # Generate content
        generation_result = self.content_generator.generate_content(
            template_id=template_id,
            variables=variables
        )
        
        if generation_result.get('success', False):
            # Format the generated content
            content = generation_result['content']
            
            # Convert to document format
            document = {
                "title": variables.get('title', 'Generated Content'),
                "sections": [
                    {
                        "title": "Content",
                        "content": content
                    }
                ]
            }
            
            # Format the document
            output_path = self.output_formatter.format_document(
                document,
                output_format=output_format
            )
            
            generation_result["output_path"] = output_path
        
        return generation_result