#!/usr/bin/env python3
# main_doc_generator.py
#
# Main script for generating comprehensive technical and architectural 
# documentation from markdown files created by the AI Documentation Agent.

import os
import sys
import argparse
import json
from pathlib import Path
from datetime import datetime

# Import our components
from core.doc_processor import DocumentProcessor
from core.chunk_manager import ChunkManager, ChunkState
from core.similarity_calculator import SimilarityCalculator, SimilarityConfig, SimilarityMetric, VectorType
from core.assignment_engine import AssignmentEngine, AssignmentStrategy


def main():
    """Main entry point for documentation generation"""
    parser = argparse.ArgumentParser(
        description="Generate comprehensive documentation from AI-generated markdown files"
    )
    parser.add_argument(
        "output_dir", 
        help="Path to the output directory containing generated graphs and docs"
    )
    parser.add_argument(
        "--config", 
        help="Path to JSON configuration file"
    )
    parser.add_argument(
        "--technical", 
        action="store_true",
        help="Generate technical documentation"
    )
    parser.add_argument(
        "--architectural", 
        action="store_true",
        help="Generate architectural documentation"
    )
    parser.add_argument(
        "--advanced", 
        action="store_true",
        help="Use advanced ML models for similarity (if available)"
    )
    parser.add_argument(
        "--data-dir", 
        default="doc_generator_data",
        help="Directory to store processing data"
    )
    parser.add_argument(
        "--output-file", 
        help="Output file name (default: auto-generated)"
    )
    
    args = parser.parse_args()
    
    # Validate output directory
    output_dir = Path(args.output_dir)
    if not output_dir.exists() or not output_dir.is_dir():
        print(f"Error: Output directory not found: {output_dir}")
        sys.exit(1)
    
    # Load configuration
    config = {
        "chunk_size": 30,
        "similarity_threshold": 0.6,
        "assignment_strategy": "hybrid",
        "data_dir": args.data_dir,
        "include_metadata": True,
        "use_advanced_models": args.advanced
    }
    
    if args.config:
        config_path = Path(args.config)
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_updates = json.load(f)
                    config.update(config_updates)
                print(f"Loaded configuration from {config_path}")
            except Exception as e:
                print(f"Error loading configuration: {e}")
    
    # Initialize document processor
    print(f"Initializing document processor for {output_dir}...")
    processor = DocumentProcessor(
        output_dir=str(output_dir),
        config=config
    )
    
    # Process documentation
    print("Processing documentation...")
    processing_results = processor.process_documentation()
    
    print("\nProcessing Summary:")
    print(f"- Documents processed: {processing_results.get('documents_processed', 0)}")
    print(f"- Chunks created: {processing_results.get('chunks_created', 0)}")
    print(f"- Similarity connections: {processing_results.get('similarity_connections', 0)}")
    
    assignments = processing_results.get('assignments', {})
    if 'by_status' in assignments and 'assigned' in assignments['by_status']:
        print(f"- Assignments created: {assignments['by_status']['assigned']}")
    
    conflicts = processing_results.get('conflicts', {})
    if 'detected' in conflicts:
        print(f"- Conflicts detected and resolved: {conflicts['detected']}")
    
    # Generate documentation
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if args.technical or not args.architectural:
        # Default to technical if nothing specified
        tech_output = args.output_file or f"technical_documentation_{timestamp}.md"
        print(f"\nGenerating technical documentation: {tech_output}")
        processor.generate_technical_documentation(tech_output)
    
    if args.architectural:
        arch_output = args.output_file or f"architectural_documentation_{timestamp}.md"
        if args.technical and arch_output == tech_output:
            # Avoid name collision
            arch_output = f"architectural_documentation_{timestamp}.md"
        
        print(f"\nGenerating architectural documentation: {arch_output}")
        processor.generate_architectural_documentation(arch_output)
    
    print("\nDocumentation generation complete.")
    print(f"Output files are in: {Path(config['data_dir'])}")


if __name__ == "__main__":
    main()