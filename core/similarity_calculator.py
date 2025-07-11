import numpy as np
from typing import List, Dict, Any, Tuple, Optional, Union, Set
from dataclasses import dataclass
import json
import sqlite3
from pathlib import Path
import re
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans, AgglomerativeClustering
import hashlib
import os
from enum import Enum

# Import error-safe way (works if module is available or not)
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False


class SimilarityMetric(Enum):
    """Supported similarity metrics"""
    COSINE = "cosine"
    JACCARD = "jaccard"
    SEMANTIC = "semantic"
    HYBRID = "hybrid"
    CUSTOM = "custom"


class VectorType(Enum):
    """Types of vectorization for documents"""
    TFIDF = "tfidf"
    WORD2VEC = "word2vec"
    SENTENCE_BERT = "sentence_bert"
    SPACY = "spacy"
    ENSEMBLE = "ensemble"


@dataclass
class SimilarityConfig:
    """Configuration for similarity calculation"""
    metrics: List[SimilarityMetric]
    vector_type: VectorType
    weights: Dict[SimilarityMetric, float] = None
    min_similarity: float = 0.3
    include_metadata: bool = True
    model_name: str = "all-MiniLM-L6-v2"  # Default model for SentenceBERT
    cache_vectors: bool = True
    n_clusters: int = 4  # Default number of clusters


class SimilarityCalculator:
    """
    Multi-dimensional similarity scoring system for documents and chunks 
    using various metrics and ML models.
    """
    
    def __init__(self, storage_path: str = "similarity_data", config: SimilarityConfig = None):
        """
        Initialize the similarity calculator.
        
        Args:
            storage_path: Directory to store similarity data and vectors
            config: Similarity configuration
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        
        # Set default config if none provided
        if config is None:
            self.config = SimilarityConfig(
                metrics=[SimilarityMetric.COSINE, SimilarityMetric.JACCARD],
                vector_type=VectorType.TFIDF,
                weights={
                    SimilarityMetric.COSINE: 0.7,
                    SimilarityMetric.JACCARD: 0.3
                }
            )
        else:
            self.config = config
            # Fill in default weights if not provided
            if self.config.weights is None:
                self.config.weights = {m: 1.0/len(self.config.metrics) for m in self.config.metrics}
        
        # Initialize vector stores and caches
        self.db_path = self.storage_path / "similarity.db"
        self._init_database()
        
        # Initialize vectorizers based on configuration
        self._init_vectorizers()
        
        # Document content cache (doc_id -> content)
        self.doc_cache = {}
        
        # Vector cache (doc_id -> vector)
        self.vector_cache = {}
        
        # Similarity matrix cache
        self.similarity_cache = {}
    
    def _init_database(self):
        """Initialize SQLite database with similarity tables"""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS document_vectors (
                    document_id TEXT PRIMARY KEY,
                    vector_type TEXT NOT NULL,
                    vector_data BLOB NOT NULL,
                    hash TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                
                CREATE TABLE IF NOT EXISTS similarity_scores (
                    source_id TEXT,
                    target_id TEXT,
                    metric TEXT NOT NULL,
                    score REAL NOT NULL,
                    PRIMARY KEY (source_id, target_id, metric)
                );
                
                CREATE TABLE IF NOT EXISTS similarity_clusters (
                    cluster_id TEXT PRIMARY KEY,
                    algorithm TEXT NOT NULL,
                    parameters TEXT NOT NULL,
                    document_ids TEXT NOT NULL,  -- JSON array
                    centroid_vector BLOB,
                    created_at TEXT NOT NULL
                );
                
                CREATE INDEX IF NOT EXISTS idx_sim_source ON similarity_scores(source_id);
                CREATE INDEX IF NOT EXISTS idx_sim_target ON similarity_scores(target_id);
                CREATE INDEX IF NOT EXISTS idx_vector_type ON document_vectors(vector_type);
            """)
    
    def _init_vectorizers(self):
        """Initialize vectorizers based on configuration"""
        self.vectorizers = {}
        
        # TF-IDF Vectorizer (always available)
        self.vectorizers[VectorType.TFIDF] = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
        # Load other vectorizers based on availability and configuration
        if self.config.vector_type == VectorType.SENTENCE_BERT and SENTENCE_TRANSFORMERS_AVAILABLE:
            self.vectorizers[VectorType.SENTENCE_BERT] = SentenceTransformer(self.config.model_name)
        
        if self.config.vector_type == VectorType.SPACY and SPACY_AVAILABLE:
            import spacy
            try:
                self.vectorizers[VectorType.SPACY] = spacy.load("en_core_web_md")
            except:
                # Fallback to smaller model
                try:
                    self.vectorizers[VectorType.SPACY] = spacy.load("en_core_web_sm")
                except:
                    print("Warning: Spacy models not available. Run: python -m spacy download en_core_web_md")
    
    def calculate_similarity(self, doc1: Union[str, Dict], doc2: Union[str, Dict], 
                           metric: SimilarityMetric = None) -> float:
        """
        Calculate similarity between two documents.
        
        Args:
            doc1: First document (ID, text, or dict with 'content' field)
            doc2: Second document (ID, text, or dict with 'content' field)
            metric: Specific metric to use (defaults to config)
            
        Returns:
            Similarity score between 0 and 1
        """
        # If documents are provided as IDs, look them up
        if isinstance(doc1, str) and not doc1.startswith("{") and len(doc1) < 100:
            doc1 = self._get_document_content(doc1)
        
        if isinstance(doc2, str) and not doc2.startswith("{") and len(doc2) < 100:
            doc2 = self._get_document_content(doc2)
        
        # Extract text content
        text1 = self._extract_text(doc1)
        text2 = self._extract_text(doc2)
        
        if not text1 or not text2:
            return 0.0
        
        # If metric specified, use that; otherwise use all configured metrics
        if metric:
            return self._calculate_single_metric(text1, text2, metric)
        else:
            # Calculate weighted average of all metrics
            scores = {}
            for m in self.config.metrics:
                scores[m] = self._calculate_single_metric(text1, text2, m)
            
            # Weighted average
            total_weight = sum(self.config.weights.values())
            weighted_score = sum(scores[m] * self.config.weights[m] 
                                for m in scores) / total_weight
            
            return weighted_score
    
    def _calculate_single_metric(self, text1: str, text2: str, 
                                metric: SimilarityMetric) -> float:
        """Calculate similarity using a specific metric"""
        if metric == SimilarityMetric.COSINE:
            return self._cosine_similarity(text1, text2)
        elif metric == SimilarityMetric.JACCARD:
            return self._jaccard_similarity(text1, text2)
        elif metric == SimilarityMetric.SEMANTIC:
            return self._semantic_similarity(text1, text2)
        elif metric == SimilarityMetric.HYBRID:
            cosine = self._cosine_similarity(text1, text2)
            semantic = self._semantic_similarity(text1, text2)
            return 0.4 * cosine + 0.6 * semantic
        else:
            # Default to cosine
            return self._cosine_similarity(text1, text2)
    
    def _cosine_similarity(self, text1: str, text2: str) -> float:
        """Calculate cosine similarity between texts using TF-IDF"""
        vectorizer = self.vectorizers.get(VectorType.TFIDF)
        if not vectorizer:
            return 0.0
        
        try:
            # Handle first-time vectorization
            if not hasattr(vectorizer, 'vocabulary_'):
                vectorizer.fit([text1, text2])
            
            vec1 = vectorizer.transform([text1])
            vec2 = vectorizer.transform([text2])
            
            return cosine_similarity(vec1, vec2)[0][0]
        except Exception as e:
            print(f"Error calculating cosine similarity: {e}")
            return 0.0
    
    def _jaccard_similarity(self, text1: str, text2: str) -> float:
        """Calculate Jaccard similarity between texts (token overlap)"""
        # Simple tokenization and cleaning
        def tokenize(text):
            tokens = re.findall(r'\b\w+\b', text.lower())
            return set(tokens)
        
        set1 = tokenize(text1)
        set2 = tokenize(text2)
        
        if not set1 or not set2:
            return 0.0
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0.0
    
    def _semantic_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity using embeddings"""
        if self.config.vector_type == VectorType.SENTENCE_BERT and VectorType.SENTENCE_BERT in self.vectorizers:
            model = self.vectorizers[VectorType.SENTENCE_BERT]
            
            # Create sentence embeddings
            try:
                embedding1 = model.encode([text1])[0]
                embedding2 = model.encode([text2])[0]
                
                # Cosine similarity between embeddings
                similarity = np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))
                return float(similarity)
            except Exception as e:
                print(f"Error calculating semantic similarity: {e}")
                return 0.0
        elif self.config.vector_type == VectorType.SPACY and VectorType.SPACY in self.vectorizers:
            nlp = self.vectorizers[VectorType.SPACY]
            
            try:
                # Process texts with spaCy
                doc1 = nlp(text1)
                doc2 = nlp(text2)
                
                # Use spaCy's similarity method
                return doc1.similarity(doc2)
            except Exception as e:
                print(f"Error calculating spaCy similarity: {e}")
                return 0.0
        else:
            # Fallback to cosine similarity if semantic models unavailable
            return self._cosine_similarity(text1, text2)
    
    def build_similarity_matrix(self, document_ids: List[str], 
                              metric: SimilarityMetric = None,
                              threshold: float = None) -> Dict[Tuple[str, str], float]:
        """
        Build a similarity matrix for multiple documents.
        
        Args:
            document_ids: List of document IDs
            metric: Similarity metric to use
            threshold: Minimum similarity to include
            
        Returns:
            Dictionary of (doc1, doc2) -> similarity score
        """
        if not document_ids:
            return {}
        
        # Set default threshold
        if threshold is None:
            threshold = self.config.min_similarity
        
        # Check cache first
        cache_key = f"{'-'.join(sorted(document_ids))}-{metric.value if metric else 'default'}"
        if cache_key in self.similarity_cache:
            return self.similarity_cache[cache_key]
        
        # Calculate all pairwise similarities
        matrix = {}
        n = len(document_ids)
        
        # Get all document contents first
        documents = {}
        for doc_id in document_ids:
            documents[doc_id] = self._get_document_content(doc_id)
        
        # For large sets, use vectorization for efficiency
        if n > 10 and not metric or metric in [SimilarityMetric.COSINE, SimilarityMetric.SEMANTIC]:
            # Build document vectors
            doc_vectors = self._build_document_vectors(documents)
            
            # Calculate similarity matrix
            for i in range(n):
                for j in range(i+1, n):
                    doc1_id = document_ids[i]
                    doc2_id = document_ids[j]
                    
                    if doc1_id == doc2_id:
                        continue
                    
                    # Calculate vector similarity
                    sim_score = self._vector_similarity(
                        doc_vectors.get(doc1_id),
                        doc_vectors.get(doc2_id)
                    )
                    
                    if sim_score >= threshold:
                        matrix[(doc1_id, doc2_id)] = sim_score
                        matrix[(doc2_id, doc1_id)] = sim_score
        else:
            # Pairwise comparison for smaller sets or specific metrics
            for i in range(n):
                for j in range(i+1, n):
                    doc1_id = document_ids[i]
                    doc2_id = document_ids[j]
                    
                    if doc1_id == doc2_id:
                        continue
                    
                    doc1 = documents.get(doc1_id)
                    doc2 = documents.get(doc2_id)
                    
                    if not doc1 or not doc2:
                        continue
                    
                    sim_score = self.calculate_similarity(doc1, doc2, metric)
                    
                    if sim_score >= threshold:
                        matrix[(doc1_id, doc2_id)] = sim_score
                        matrix[(doc2_id, doc1_id)] = sim_score
        
        # Cache the result
        self.similarity_cache[cache_key] = matrix
        
        return matrix
    
    def _build_document_vectors(self, documents: Dict[str, Any]) -> Dict[str, np.ndarray]:
        """Build vectors for a set of documents"""
        vectors = {}
        
        # Collect document texts
        texts = []
        doc_ids = []
        
        for doc_id, doc in documents.items():
            text = self._extract_text(doc)
            if text:
                texts.append(text)
                doc_ids.append(doc_id)
        
        if not texts:
            return {}
        
        if self.config.vector_type == VectorType.TFIDF:
            # TF-IDF vectorization
            vectorizer = self.vectorizers[VectorType.TFIDF]
            
            try:
                # Fit and transform
                matrix = vectorizer.fit_transform(texts)
                
                # Store vectors by document ID
                for i, doc_id in enumerate(doc_ids):
                    vectors[doc_id] = matrix[i]
            except Exception as e:
                print(f"Error building TF-IDF vectors: {e}")
        
        elif self.config.vector_type == VectorType.SENTENCE_BERT and VectorType.SENTENCE_BERT in self.vectorizers:
            # Sentence BERT embeddings
            model = self.vectorizers[VectorType.SENTENCE_BERT]
            
            try:
                # Generate embeddings
                embeddings = model.encode(texts)
                
                # Store embeddings by document ID
                for i, doc_id in enumerate(doc_ids):
                    vectors[doc_id] = embeddings[i]
            except Exception as e:
                print(f"Error building SBERT vectors: {e}")
        
        elif self.config.vector_type == VectorType.SPACY and VectorType.SPACY in self.vectorizers:
            # SpaCy vectors
            nlp = self.vectorizers[VectorType.SPACY]
            
            try:
                for i, doc_id in enumerate(doc_ids):
                    doc = nlp(texts[i])
                    vectors[doc_id] = doc.vector
            except Exception as e:
                print(f"Error building SpaCy vectors: {e}")
        
        # Cache vectors if configured
        if self.config.cache_vectors:
            self._cache_document_vectors(vectors)
        
        return vectors
    
    def _vector_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate similarity between two vectors"""
        if vec1 is None or vec2 is None:
            return 0.0
        
        try:
            # Handle scipy sparse matrices
            if hasattr(vec1, 'toarray'):
                vec1 = vec1.toarray().flatten()
            
            if hasattr(vec2, 'toarray'):
                vec2 = vec2.toarray().flatten()
            
            # Convert to numpy arrays if needed
            vec1 = np.array(vec1).flatten()
            vec2 = np.array(vec2).flatten()
            
            # Cosine similarity
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return float(np.dot(vec1, vec2) / (norm1 * norm2))
        except Exception as e:
            print(f"Error calculating vector similarity: {e}")
            return 0.0
    
    def _cache_document_vectors(self, vectors: Dict[str, np.ndarray]):
        """Cache document vectors in database"""
        from datetime import datetime
        import pickle
        
        with sqlite3.connect(self.db_path) as conn:
            now = datetime.now().isoformat()
            
            for doc_id, vector in vectors.items():
                # Serialize vector data
                vector_data = pickle.dumps(vector)
                
                # Calculate hash for change detection
                vector_hash = hashlib.md5(vector_data).hexdigest()
                
                # Check if vector exists and has changed
                existing = conn.execute("""
                    SELECT hash FROM document_vectors
                    WHERE document_id = ? AND vector_type = ?
                """, (doc_id, self.config.vector_type.value)).fetchone()
                
                if existing and existing[0] == vector_hash:
                    continue  # No change
                
                # Upsert vector data
                conn.execute("""
                    INSERT OR REPLACE INTO document_vectors
                    (document_id, vector_type, vector_data, hash, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    doc_id,
                    self.config.vector_type.value,
                    vector_data,
                    vector_hash,
                    now
                ))
    
    def _get_document_content(self, doc_id: str) -> Dict:
        """Get document content by ID"""
        # Check cache first
        if doc_id in self.doc_cache:
            return self.doc_cache[doc_id]
        
        # This would normally fetch from a document store
        # For this example, we'll just return a placeholder
        # In a real implementation, this would load from MemoryStore or another storage
        
        # Example placeholder
        document = {
            "id": doc_id,
            "content": f"Example content for document {doc_id}",
            "metadata": {"title": f"Document {doc_id}"}
        }
        
        # Cache for future use
        self.doc_cache[doc_id] = document
        
        return document
    
    def _extract_text(self, document: Union[str, Dict]) -> str:
        """Extract text content from document"""
        if isinstance(document, str):
            # Check if it's a JSON string
            if document.startswith('{') and document.endswith('}'):
                try:
                    doc_dict = json.loads(document)
                    return self._extract_text(doc_dict)
                except:
                    # Treat as plain text
                    return document
            else:
                # Plain text
                return document
        elif isinstance(document, dict):
            # Extract from document dictionary
            content = document.get('content', '')
            
            # If no content but there's text
            if not content and 'text' in document:
                content = document['text']
            
            # Optionally include metadata
            if self.config.include_metadata:
                metadata = document.get('metadata', {})
                title = metadata.get('title', '')
                
                if title:
                    content = f"{title}. {content}"
            
            return content
        else:
            return ""
    
    def cluster_documents(self, document_ids: List[str], 
                         num_clusters: int = None,
                         algorithm: str = 'kmeans') -> List[List[str]]:
        """
        Cluster documents based on similarity.
        
        Args:
            document_ids: List of document IDs to cluster
            num_clusters: Number of clusters (default from config)
            algorithm: Clustering algorithm ('kmeans' or 'hierarchical')
            
        Returns:
            List of document clusters, where each cluster is a list of doc IDs
        """
        if not document_ids:
            return []
        
        if num_clusters is None:
            num_clusters = self.config.n_clusters
        
        # Ensure we don't create more clusters than documents
        num_clusters = min(num_clusters, len(document_ids))
        
        # Get document vectors
        documents = {doc_id: self._get_document_content(doc_id) for doc_id in document_ids}
        vectors_dict = self._build_document_vectors(documents)
        
        # Extract vectors in a consistent order
        ordered_vectors = []
        ordered_ids = []
        
        for doc_id in document_ids:
            if doc_id in vectors_dict:
                vec = vectors_dict[doc_id]
                
                # Handle sparse vectors
                if hasattr(vec, 'toarray'):
                    vec = vec.toarray().flatten()
                
                ordered_vectors.append(vec)
                ordered_ids.append(doc_id)
        
        if not ordered_vectors:
            return []
        
        # Convert to numpy array
        X = np.array(ordered_vectors)
        
        # Perform clustering
        labels = None
        
        try:
            if algorithm == 'kmeans':
                # K-means clustering
                kmeans = KMeans(n_clusters=num_clusters, random_state=42)
                labels = kmeans.fit_predict(X)
            elif algorithm == 'hierarchical':
                # Hierarchical clustering
                clustering = AgglomerativeClustering(n_clusters=num_clusters)
                labels = clustering.fit_predict(X)
            else:
                # Default to K-means
                kmeans = KMeans(n_clusters=num_clusters, random_state=42)
                labels = kmeans.fit_predict(X)
        except Exception as e:
            print(f"Error during clustering: {e}")
            return [[doc_id] for doc_id in ordered_ids]  # Each doc in its own cluster
        
        # Group documents by cluster label
        clusters = [[] for _ in range(num_clusters)]
        
        for i, label in enumerate(labels):
            clusters[label].append(ordered_ids[i])
        
        # Filter out empty clusters
        clusters = [c for c in clusters if c]
        
        # Store clustering results
        self._store_clustering_results(clusters, algorithm)
        
        return clusters
    
    def _store_clustering_results(self, clusters: List[List[str]], algorithm: str):
        """Store clustering results in database"""
        from datetime import datetime
        import pickle
        
        with sqlite3.connect(self.db_path) as conn:
            now = datetime.now().isoformat()
            
            # Generate a unique ID for this clustering
            cluster_hash = hashlib.md5(f"{algorithm}-{now}-{str(clusters)}".encode()).hexdigest()
            
            # Store each cluster
            for i, cluster in enumerate(clusters):
                cluster_id = f"{cluster_hash}-{i}"
                
                conn.execute("""
                    INSERT INTO similarity_clusters
                    (cluster_id, algorithm, parameters, document_ids, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    cluster_id,
                    algorithm,
                    json.dumps({"n_clusters": len(clusters)}),
                    json.dumps(cluster),
                    now
                ))
    
    def find_similar_documents(self, query_doc: Union[str, Dict], 
                             candidate_ids: List[str] = None,
                             top_n: int = 5,
                             threshold: float = None) -> List[Tuple[str, float]]:
        """
        Find the most similar documents to a query document.
        
        Args:
            query_doc: Query document (ID, text, or dict with 'content')
            candidate_ids: List of candidate document IDs (optional)
            top_n: Number of results to return
            threshold: Minimum similarity threshold
            
        Returns:
            List of (doc_id, similarity_score) tuples
        """
        if threshold is None:
            threshold = self.config.min_similarity
        
        # Extract query text
        query_text = self._extract_text(query_doc)
        if not query_text:
            return []
        
        # If no candidates provided, this is a stub where we would search all documents
        if not candidate_ids:
            return []
        
        # Calculate similarity for each candidate
        similarities = []
        
        for doc_id in candidate_ids:
            doc = self._get_document_content(doc_id)
            score = self.calculate_similarity(query_text, doc)
            
            if score >= threshold:
                similarities.append((doc_id, score))
        
        # Sort by similarity score (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Return top N results
        return similarities[:top_n]
    
    def update_similarity_cache(self, document_ids: List[str]) -> None:
        """
        Update similarity cache for specified documents.
        
        Args:
            document_ids: List of document IDs to update
        """
        # Clear existing cache entries for these documents
        keys_to_remove = []
        for key in self.similarity_cache:
            doc_ids = key.split('-')[:-1]  # Remove metric suffix
            if any(doc_id in doc_ids for doc_id in document_ids):
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            self.similarity_cache.pop(key, None)
        
        # Clear document cache
        for doc_id in document_ids:
            self.doc_cache.pop(doc_id, None)
            self.vector_cache.pop(doc_id, None)
    
    def get_similarity_stats(self) -> Dict[str, Any]:
        """
        Get statistics about similarity calculations.
        
        Returns:
            Dictionary with statistics
        """
        with sqlite3.connect(self.db_path) as conn:
            # Vector counts
            vector_counts = conn.execute("""
                SELECT vector_type, COUNT(*) FROM document_vectors
                GROUP BY vector_type
            """).fetchall()
            
            vector_stats = {vt: count for vt, count in vector_counts}
            
            # Similarity score distribution
            score_stats = conn.execute("""
                SELECT 
                    COUNT(*) as total,
                    AVG(score) as avg_score,
                    MIN(score) as min_score,
                    MAX(score) as max_score
                FROM similarity_scores
            """).fetchone()
            
            # Clustering stats
            cluster_stats = conn.execute("""
                SELECT 
                    COUNT(DISTINCT cluster_id) as total_clusters,
                    COUNT(*) as total_assignments,
                    AVG(json_array_length(document_ids)) as avg_cluster_size
                FROM similarity_clusters
            """).fetchone()
            
            return {
                "vectors": {
                    "total": sum(vector_stats.values()),
                    "by_type": vector_stats
                },
                "similarity_scores": {
                    "total": score_stats[0],
                    "avg_score": score_stats[1],
                    "min_score": score_stats[2],
                    "max_score": score_stats[3]
                },
                "clusters": {
                    "total": cluster_stats[0],
                    "total_assignments": cluster_stats[1],
                    "avg_cluster_size": cluster_stats[2]
                },
                "cache": {
                    "similarity_cache_size": len(self.similarity_cache),
                    "document_cache_size": len(self.doc_cache),
                    "vector_cache_size": len(self.vector_cache)
                }
            }