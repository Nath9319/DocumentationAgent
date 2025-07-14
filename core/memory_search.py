import numpy as np
from typing import List, Dict, Any, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json
import sqlite3
from .memory_store import MemoryStore
class MemorySearchEngine:
    """High-performance search for compressed memory"""
    
    def __init__(self, memory_store: MemoryStore):
        self.memory_store = memory_store
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            max_features=5000,
            ngram_range=(1, 2)
        )
        self.document_vectors = None
        self.document_index = {}
        self._build_search_index()
    
    def _build_search_index(self):
        """Build search index from stored documents"""
        with sqlite3.connect(self.memory_store.db_path) as conn:
            conn.row_factory = sqlite3.Row
            docs = conn.execute("SELECT content_hash, title FROM documents").fetchall()
        
        if not docs:
            return
        
        # Collect document texts
        doc_texts = []
        for doc in docs:
            content = self.memory_store._retrieve_content(doc['content_hash'])
            if content:
                # Combine title and content for better search
                search_text = f"{doc['title']} {content}"
                doc_texts.append(search_text)
                self.document_index[len(doc_texts) - 1] = doc['content_hash']
        
        if doc_texts:
            # Build TF-IDF vectors
            self.document_vectors = self.vectorizer.fit_transform(doc_texts)
    
    def search(self, query: str, search_type: str = "hybrid", limit: int = 10) -> List[Dict[str, Any]]:
        """Main search interface"""
        if search_type == "keyword":
            return self._keyword_search(query, limit)
        elif search_type == "semantic":
            return self._semantic_search(query, limit)
        else:  # hybrid
            return self._hybrid_search(query, limit)
    
    def _keyword_search(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Traditional keyword-based search"""
        results = self.memory_store.search_documents(query, limit=limit)
        
        # Add relevance scores
        for result in results:
            content = self.memory_store._retrieve_content(result['content_hash'])
            if content:
                # Simple relevance scoring
                query_terms = query.lower().split()
                content_lower = content.lower()
                score = sum(1 for term in query_terms if term in content_lower)
                result['relevance_score'] = score / len(query_terms) if query_terms else 0
            else:
                result['relevance_score'] = 0
        
        return sorted(results, key=lambda x: x['relevance_score'], reverse=True)
    
    def _semantic_search(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Vector-based semantic search"""
        if self.document_vectors is None or self.document_vectors.shape[0] == 0:
            return []
        
        # Vectorize query
        query_vector = self.vectorizer.transform([query])
        
        # Calculate similarities
        similarities = cosine_similarity(query_vector, self.document_vectors).flatten()
        
        # Get top results
        top_indices = np.argsort(similarities)[::-1][:limit]
        
        results = []
        for idx in top_indices:
            if similarities[idx] > 0.1:  # Minimum similarity threshold
                content_hash = self.document_index[idx]
                doc = self.memory_store.retrieve_document(content_hash)
                if doc:
                    doc['relevance_score'] = float(similarities[idx])
                    results.append(doc)
        
        return results
    
    def _hybrid_search(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Combined keyword and semantic search"""
        keyword_results = self._keyword_search(query, limit * 2)
        semantic_results = self._semantic_search(query, limit * 2)
        
        # Combine and deduplicate
        combined_results = {}
        
        # Add keyword results with weight
        for result in keyword_results:
            hash_key = result.get('content_hash', '')
            if hash_key:
                combined_results[hash_key] = result
                combined_results[hash_key]['keyword_score'] = result.get('relevance_score', 0)
        
        # Add semantic results with weight
        for result in semantic_results:
            hash_key = result['metadata']['content_hash'] if 'metadata' in result else ''
            if hash_key in combined_results:
                combined_results[hash_key]['semantic_score'] = result.get('relevance_score', 0)
            else:
                combined_results[hash_key] = result
                combined_results[hash_key]['keyword_score'] = 0
                combined_results[hash_key]['semantic_score'] = result.get('relevance_score', 0)
        
        # Calculate combined scores
        for result in combined_results.values():
            keyword_score = result.get('keyword_score', 0)
            semantic_score = result.get('semantic_score', 0)
            result['combined_score'] = 0.4 * keyword_score + 0.6 * semantic_score
        
        # Sort by combined score and return top results
        sorted_results = sorted(
            combined_results.values(), 
            key=lambda x: x.get('combined_score', 0), 
            reverse=True
        )
        
        return sorted_results[:limit]
    
    def suggest_queries(self, partial_query: str) -> List[str]:
        """Query suggestion based on stored entities"""
        with sqlite3.connect(self.memory_store.db_path) as conn:
            suggestions = conn.execute("""
                SELECT DISTINCT entity_name 
                FROM entities 
                WHERE entity_name LIKE ? 
                ORDER BY entity_name 
                LIMIT 5
            """, (f"%{partial_query}%",)).fetchall()
        
        return [s[0] for s in suggestions]
    
    def get_search_analytics(self) -> Dict[str, Any]:
        """Basic search analytics"""
        with sqlite3.connect(self.memory_store.db_path) as conn:
            stats = conn.execute("""
                SELECT 
                    COUNT(*) as total_documents,
                    AVG(compressed_size) as avg_size,
                    AVG(quality_score) as avg_quality,
                    COUNT(DISTINCT doc_type) as doc_types
                FROM documents
            """).fetchone()
        
        return {
            'total_documents': stats[0],
            'average_compressed_size': stats[1],
            'average_quality_score': stats[2],
            'document_types': stats[3],
            'index_size': self.document_vectors.shape if self.document_vectors is not None else (0, 0)
        }
