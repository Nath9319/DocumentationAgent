import sqlite3
import json
import gzip
import os
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pathlib import Path
import hashlib

class MemoryStore:
    """Persistent storage for compressed knowledge"""
    
    def __init__(self, storage_path: str = "memory_store"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        
        # Initialize database
        self.db_path = self.storage_path / "memory.db"
        self._init_database()
        
        # Content-addressable storage directory
        self.content_dir = self.storage_path / "content"
        self.content_dir.mkdir(exist_ok=True)
    
    def _init_database(self):
        """Initialize SQLite database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content_hash TEXT UNIQUE NOT NULL,
                    title TEXT,
                    doc_type TEXT,
                    compression_level TEXT,
                    original_size INTEGER,
                    compressed_size INTEGER,
                    quality_score REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT
                );
                
                CREATE TABLE IF NOT EXISTS entities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    document_id INTEGER,
                    entity_name TEXT,
                    entity_type TEXT,
                    confidence REAL,
                    FOREIGN KEY (document_id) REFERENCES documents (id)
                );
                
                CREATE TABLE IF NOT EXISTS versions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    document_id INTEGER,
                    version_number INTEGER,
                    content_hash TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (document_id) REFERENCES documents (id)
                );
                
                CREATE INDEX IF NOT EXISTS idx_content_hash ON documents(content_hash);
                CREATE INDEX IF NOT EXISTS idx_entity_name ON entities(entity_name);
                CREATE INDEX IF NOT EXISTS idx_doc_type ON documents(doc_type);
            """)
    
    def store_compressed_document(self, compressed_result: 'CompressionResult', 
                                title: str, doc_type: str, entities: List[Dict] = None) -> str:
        """Store compressed document with metadata"""
        content = compressed_result.compressed_content
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        
        # Store content in content-addressable storage
        self._store_content(content_hash, content)
        
        # Store metadata in database
        with sqlite3.connect(self.db_path) as conn:
            # Check if document already exists
            existing = conn.execute(
                "SELECT id FROM documents WHERE content_hash = ?", 
                (content_hash,)
            ).fetchone()
            
            if existing:
                return content_hash  # Already stored
            
            # Insert new document
            cursor = conn.execute("""
                INSERT INTO documents 
                (content_hash, title, doc_type, compression_level, original_size, 
                 compressed_size, quality_score, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                content_hash, title, doc_type, compressed_result.method,
                compressed_result.original_size, compressed_result.compressed_size,
                compressed_result.quality_score, json.dumps(compressed_result.metadata)
            ))
            
            doc_id = cursor.lastrowid
            
            # Store entities
            if entities:
                for entity in entities:
                    conn.execute("""
                        INSERT INTO entities (document_id, entity_name, entity_type, confidence)
                        VALUES (?, ?, ?, ?)
                    """, (doc_id, entity['name'], entity['type'], entity.get('confidence', 1.0)))
            
            # Create initial version
            conn.execute("""
                INSERT INTO versions (document_id, version_number, content_hash)
                VALUES (?, 1, ?)
            """, (doc_id, content_hash))
        
        return content_hash
    
    def retrieve_document(self, content_hash: str) -> Optional[Dict[str, Any]]:
        """Retrieve document by content hash"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            doc_row = conn.execute("""
                SELECT * FROM documents WHERE content_hash = ?
            """, (content_hash,)).fetchone()
            
            if not doc_row:
                return None
            
            # Get content
            content = self._retrieve_content(content_hash)
            if not content:
                return None
            
            # Get entities
            entities = conn.execute("""
                SELECT entity_name, entity_type, confidence 
                FROM entities WHERE document_id = ?
            """, (doc_row['id'],)).fetchall()
            
            return {
                'content': content,
                'metadata': {
                    'title': doc_row['title'],
                    'doc_type': doc_row['doc_type'],
                    'compression_level': doc_row['compression_level'],
                    'original_size': doc_row['original_size'],
                    'compressed_size': doc_row['compressed_size'],
                    'quality_score': doc_row['quality_score'],
                    'created_at': doc_row['created_at'],
                    'metadata': json.loads(doc_row['metadata']) if doc_row['metadata'] else {}
                },
                'entities': [dict(e) for e in entities]
            }
    
    def _store_content(self, content_hash: str, content: str):
        """Store content in content-addressable storage"""
        # Use first 2 chars for directory structure
        subdir = self.content_dir / content_hash[:2]
        subdir.mkdir(exist_ok=True)
        
        # Compress and store
        file_path = subdir / f"{content_hash[2:]}.gz"
        with gzip.open(file_path, 'wt', encoding='utf-8') as f:
            f.write(content)
    
    def _retrieve_content(self, content_hash: str) -> Optional[str]:
        """Retrieve content from storage"""
        subdir = self.content_dir / content_hash[:2]
        file_path = subdir / f"{content_hash[2:]}.gz"
        
        if not file_path.exists():
            return None
        
        try:
            with gzip.open(file_path, 'rt', encoding='utf-8') as f:
                return f.read()
        except Exception:
            return None
    
    def search_documents(self, query: str, doc_type: str = None, limit: int = 10) -> List[Dict]:
        """Basic search functionality"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # Build query
            sql = "SELECT * FROM documents WHERE title LIKE ?"
            params = [f"%{query}%"]
            
            if doc_type:
                sql += " AND doc_type = ?"
                params.append(doc_type)
            
            sql += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)
            
            results = conn.execute(sql, params).fetchall()
            return [dict(row) for row in results]