
import sqlite3
from typing import Dict, Any, List, Optional
from .compression_engine import DocumentationCompressor, CompressionLevel
from .memory_store import MemoryStore
from .memory_search import MemorySearchEngine

class MemoryManager:
    """Unified interface for memory system"""
    
    def __init__(self, storage_path: str = "memory_store"):
        self.compressor = DocumentationCompressor()
        self.store = MemoryStore(storage_path)
        self.search_engine = MemorySearchEngine(self.store)
    
    def process_documentation_folder(self, analysis_results: Dict[str, Any], 
                                   compression_level: CompressionLevel = CompressionLevel.BALANCED):
        """Process analyzed documentation and store compressed versions"""
        processed_count = 0
        
        for doc_path, doc_info in analysis_results['documents'].items():
            content = self._reconstruct_content(doc_info['sections'])
            
            if content.strip():
                compression_result = self.compressor.compress_documentation(
                    content, compression_level, doc_info['metadata'].get('format', 'markdown')
                )
                
                content_hash = self.store.store_compressed_document(
                    compression_result,
                    title=doc_info['metadata'].get('title', 'Untitled'),
                    doc_type=doc_info['metadata'].get('format', 'markdown'),
                    entities=doc_info.get('entities', [])
                )
                
                processed_count += 1
        
        self.search_engine._build_search_index()
        
        return {
            'processed_documents': processed_count,
            'storage_stats': self.get_system_stats()
        }
    
    def _reconstruct_content(self, sections: List[Dict]) -> str:
        return '\n\n'.join(section['content'] for section in sections if section['content'])
    
    def search_memory(self, query: str, search_type: str = "hybrid", limit: int = 10) -> List[Dict]:
        return self.search_engine.search(query, search_type, limit)
    
    def get_system_stats(self) -> Dict[str, Any]:
        search_stats = self.search_engine.get_search_analytics()
        
        with sqlite3.connect(self.store.db_path) as conn:
            compression_stats = conn.execute("""
                SELECT compression_level, COUNT(*) as count,
                       AVG(original_size) as avg_original,
                       AVG(compressed_size) as avg_compressed,
                       AVG(quality_score) as avg_quality
                FROM documents GROUP BY compression_level
            """).fetchall()
        
        return {
            'search_analytics': search_stats,
            'compression_statistics': [
                {
                    'level': row[0], 'document_count': row[1],
                    'avg_original_size': row[2], 'avg_compressed_size': row[3],
                    'avg_compression_ratio': row[3] / row[2] if row[2] > 0 else 0,
                    'avg_quality_score': row[4]
                }
                for row in compression_stats
            ]
        }