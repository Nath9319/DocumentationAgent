from typing import List, Dict, Any
from pathlib import Path
import json
import pickle

class DocumentAnalyzer:
    """Main document analysis orchestrator"""
    
    def __init__(self):
        self.parser = DocumentParserManager()
        self.extractor = EntityExtractor()
        self.preprocessor = DocumentPreprocessor()
    
    def analyze_documentation_folder(self, folder_path: str) -> Dict[str, Any]:
        """Analyze all documentation files in a folder"""
        results = {
            'documents': {},
            'entities': {},
            'statistics': {}
        }
        
        folder = Path(folder_path)
        doc_files = list(folder.glob('**/*.md')) + list(folder.glob('**/*.json'))
        
        for file_path in doc_files:
            doc = self.parser.parse_document(str(file_path))
            if doc:
                # Preprocess
                doc = self.preprocessor.preprocess(doc)
                
                # Extract entities
                entities = self.extractor.extract_entities(doc)
                doc.entities = [e.__dict__ for e in entities]
                
                results['documents'][str(file_path)] = {
                    'metadata': doc.metadata,
                    'sections': [s.__dict__ for s in doc.sections],
                    'entities': doc.entities,
                    'fingerprint': doc.fingerprint
                }
        
        # Generate statistics
        results['statistics'] = self._generate_statistics(results['documents'])
        
        return results
    
    def analyze_existing_output(self, output_dir: str) -> Dict[str, Any]:
        """Analyze existing output from main.py execution"""
        output_path = Path(output_dir)
        
        # Load existing data
        conceptual_graph = None
        doc_data = None
        
        if (output_path / "conceptual_graph.pkl").exists():
            with open(output_path / "conceptual_graph.pkl", 'rb') as f:
                conceptual_graph = pickle.load(f)
        
        if (output_path / "documentation_and_graph_data.json").exists():
            with open(output_path / "documentation_and_graph_data.json", 'r') as f:
                doc_data = json.load(f)
        
        # Analyze markdown files in documentation folder
        doc_folder = output_path / "documentation"
        analysis_results = self.analyze_documentation_folder(str(doc_folder))
        
        # Integrate with existing data
        return {
            'parsed_documents': analysis_results,
            'conceptual_graph_nodes': len(conceptual_graph.nodes()) if conceptual_graph else 0,
            'original_doc_data': len(doc_data) if doc_data else 0,
            'cross_reference_data': self._cross_reference_entities(analysis_results, doc_data)
        }
    
    def _cross_reference_entities(self, analysis_results: Dict, doc_data: Dict) -> Dict:
        """Cross-reference extracted entities with original documentation"""
        if not doc_data:
            return {}
        
        entity_map = {}
        for doc_path, doc_info in analysis_results['documents'].items():
            for entity in doc_info['entities']:
                entity_name = entity['name']
                if entity_name in doc_data:
                    entity_map[entity_name] = {
                        'found_in_markdown': doc_path,
                        'original_documentation': bool(doc_data[entity_name]),
                        'extraction_confidence': entity['confidence']
                    }
        
        return entity_map
    
    def _generate_statistics(self, documents: Dict) -> Dict[str, Any]:
        """Generate analysis statistics"""
        total_docs = len(documents)
        total_entities = sum(len(doc['entities']) for doc in documents.values())
        total_sections = sum(len(doc['sections']) for doc in documents.values())
        
        entity_types = {}
        for doc in documents.values():
            for entity in doc['entities']:
                entity_type = entity['type']
                entity_types[entity_type] = entity_types.get(entity_type, 0) + 1
        
        return {
            'total_documents': total_docs,
            'total_entities': total_entities,
            'total_sections': total_sections,
            'entity_distribution': entity_types
        }
