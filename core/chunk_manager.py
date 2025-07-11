import os
import json
import hashlib
from enum import Enum
from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass
import sqlite3
from pathlib import Path


class ChunkState(Enum):
    """State machine for chunk lifecycle"""
    CREATED = "created"       # Initial state
    ACTIVE = "active"         # In active use
    FULL = "full"             # At capacity
    STALE = "stale"           # Needs update
    SPLITTING = "splitting"   # Being split
    MERGING = "merging"       # Being merged
    ARCHIVED = "archived"     # Not active but preserved
    DELETED = "deleted"       # Marked for deletion


@dataclass
class ChunkMetadata:
    """Metadata for a documentation chunk"""
    chunk_id: str
    state: ChunkState
    capacity: int
    current_size: int
    version: int
    parent_chunks: List[str]
    child_chunks: List[str]
    document_ids: List[str]
    created_at: str
    updated_at: str
    similarity_group: Optional[str] = None
    tags: List[str] = None


class ChunkManager:
    """
    Advanced chunk lifecycle management system handling creation, updates, 
    splits, and merges while maintaining consistency.
    """
    
    def __init__(self, storage_path: str = "doc_chunks"):
        """
        Initialize the chunk manager with a storage location.
        
        Args:
            storage_path: Directory to store chunk data
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        
        # Database for chunk metadata
        self.db_path = self.storage_path / "chunks.db"
        self._init_database()
        
        # Content directory
        self.chunks_dir = self.storage_path / "content"
        self.chunks_dir.mkdir(exist_ok=True)
        
        # Configuration
        self.config = {
            "default_capacity": 50,         # Default max docs per chunk
            "split_threshold": 0.9,         # Split when 90% full
            "merge_threshold": 0.3,         # Merge when below 30% capacity
            "similarity_threshold": 0.7,    # Min similarity for related chunks
            "gc_retention_days": 30         # Days to keep deleted chunks
        }
    
    def _init_database(self):
        """Initialize SQLite database with chunk tables"""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS chunks (
                    chunk_id TEXT PRIMARY KEY,
                    state TEXT NOT NULL,
                    capacity INTEGER NOT NULL,
                    current_size INTEGER NOT NULL,
                    version INTEGER NOT NULL,
                    parent_chunks TEXT,  -- JSON array
                    child_chunks TEXT,   -- JSON array
                    document_ids TEXT,   -- JSON array
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    similarity_group TEXT,
                    tags TEXT            -- JSON array
                );
                
                CREATE TABLE IF NOT EXISTS chunk_relationships (
                    source_chunk_id TEXT,
                    target_chunk_id TEXT,
                    relationship_type TEXT,
                    weight REAL,
                    metadata TEXT,       -- JSON object
                    PRIMARY KEY (source_chunk_id, target_chunk_id, relationship_type),
                    FOREIGN KEY (source_chunk_id) REFERENCES chunks (chunk_id),
                    FOREIGN KEY (target_chunk_id) REFERENCES chunks (chunk_id)
                );
                
                CREATE TABLE IF NOT EXISTS chunk_versions (
                    chunk_id TEXT,
                    version INTEGER,
                    content_hash TEXT,
                    state TEXT,
                    timestamp TEXT,
                    change_reason TEXT,
                    PRIMARY KEY (chunk_id, version),
                    FOREIGN KEY (chunk_id) REFERENCES chunks (chunk_id)
                );
                
                CREATE TABLE IF NOT EXISTS document_chunk_assignments (
                    document_id TEXT,
                    chunk_id TEXT,
                    assignment_score REAL,
                    assigned_at TEXT,
                    PRIMARY KEY (document_id, chunk_id),
                    FOREIGN KEY (chunk_id) REFERENCES chunks (chunk_id)
                );
                
                CREATE INDEX IF NOT EXISTS idx_chunks_state ON chunks(state);
                CREATE INDEX IF NOT EXISTS idx_chunks_similarity ON chunks(similarity_group);
                CREATE INDEX IF NOT EXISTS idx_document_assignments ON document_chunk_assignments(document_id);
            """)
    
    def create_chunk(self, 
                     initial_docs: List[str] = None, 
                     capacity: int = None, 
                     tags: List[str] = None, 
                     similarity_group: str = None) -> str:
        """
        Create a new chunk with specified initial documents.
        
        Args:
            initial_docs: List of document IDs to include
            capacity: Maximum number of documents (defaults to config)
            tags: Categorical tags for the chunk
            similarity_group: Group identifier for related chunks
            
        Returns:
            chunk_id: ID of the newly created chunk
        """
        from datetime import datetime
        
        # Generate a unique chunk ID
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_suffix = hashlib.md5(os.urandom(8)).hexdigest()[:8]
        chunk_id = f"chunk_{timestamp}_{random_suffix}"
        
        # Set defaults
        if capacity is None:
            capacity = self.config["default_capacity"]
        
        if initial_docs is None:
            initial_docs = []
            
        if tags is None:
            tags = []
        
        # Create chunk metadata
        now = datetime.now().isoformat()
        chunk_metadata = ChunkMetadata(
            chunk_id=chunk_id,
            state=ChunkState.CREATED,
            capacity=capacity,
            current_size=len(initial_docs),
            version=1,
            parent_chunks=[],
            child_chunks=[],
            document_ids=initial_docs,
            created_at=now,
            updated_at=now,
            similarity_group=similarity_group,
            tags=tags
        )
        
        # Store in database
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO chunks 
                (chunk_id, state, capacity, current_size, version, parent_chunks, 
                 child_chunks, document_ids, created_at, updated_at, similarity_group, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                chunk_id,
                chunk_metadata.state.value,
                chunk_metadata.capacity,
                chunk_metadata.current_size,
                chunk_metadata.version,
                json.dumps(chunk_metadata.parent_chunks),
                json.dumps(chunk_metadata.child_chunks),
                json.dumps(chunk_metadata.document_ids),
                chunk_metadata.created_at,
                chunk_metadata.updated_at,
                chunk_metadata.similarity_group,
                json.dumps(chunk_metadata.tags)
            ))
            
            # Create initial version record
            conn.execute("""
                INSERT INTO chunk_versions
                (chunk_id, version, content_hash, state, timestamp, change_reason)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                chunk_id, 
                1, 
                "", 
                ChunkState.CREATED.value,
                now,
                "Initial creation"
            ))
            
            # Create document assignments
            for doc_id in initial_docs:
                conn.execute("""
                    INSERT INTO document_chunk_assignments
                    (document_id, chunk_id, assignment_score, assigned_at)
                    VALUES (?, ?, ?, ?)
                """, (
                    doc_id,
                    chunk_id,
                    1.0,  # Default score
                    now
                ))
        
        # Activate the chunk if it has initial documents
        if initial_docs:
            self.update_chunk_state(chunk_id, ChunkState.ACTIVE)
        
        return chunk_id
    
    def get_chunk(self, chunk_id: str) -> Optional[ChunkMetadata]:
        """
        Retrieve chunk metadata by ID.
        
        Args:
            chunk_id: ID of the chunk to retrieve
            
        Returns:
            ChunkMetadata object or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("""
                SELECT * FROM chunks WHERE chunk_id = ?
            """, (chunk_id,)).fetchone()
            
            if not row:
                return None
            
            return ChunkMetadata(
                chunk_id=row['chunk_id'],
                state=ChunkState(row['state']),
                capacity=row['capacity'],
                current_size=row['current_size'],
                version=row['version'],
                parent_chunks=json.loads(row['parent_chunks']),
                child_chunks=json.loads(row['child_chunks']),
                document_ids=json.loads(row['document_ids']),
                created_at=row['created_at'],
                updated_at=row['updated_at'],
                similarity_group=row['similarity_group'],
                tags=json.loads(row['tags'])
            )
    
    def update_chunk_state(self, chunk_id: str, new_state: ChunkState, reason: str = None) -> bool:
        """
        Update the state of a chunk in the state machine.
        
        Args:
            chunk_id: ID of the chunk
            new_state: New state to transition to
            reason: Explanation for state change
            
        Returns:
            Success flag
        """
        from datetime import datetime
        
        chunk = self.get_chunk(chunk_id)
        if not chunk:
            return False
        
        # Validate state transition
        valid_transitions = {
            ChunkState.CREATED: [ChunkState.ACTIVE, ChunkState.DELETED],
            ChunkState.ACTIVE: [ChunkState.FULL, ChunkState.STALE, ChunkState.ARCHIVED],
            ChunkState.FULL: [ChunkState.SPLITTING, ChunkState.STALE, ChunkState.ACTIVE],
            ChunkState.STALE: [ChunkState.ACTIVE, ChunkState.ARCHIVED],
            ChunkState.SPLITTING: [ChunkState.ACTIVE, ChunkState.ARCHIVED],
            ChunkState.MERGING: [ChunkState.ACTIVE, ChunkState.ARCHIVED],
            ChunkState.ARCHIVED: [ChunkState.ACTIVE, ChunkState.DELETED],
            ChunkState.DELETED: []
        }
        
        if new_state not in valid_transitions[chunk.state]:
            raise ValueError(f"Invalid state transition: {chunk.state.value} -> {new_state.value}")
        
        now = datetime.now().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            # Update chunk state
            conn.execute("""
                UPDATE chunks 
                SET state = ?, updated_at = ?, version = version + 1
                WHERE chunk_id = ?
            """, (new_state.value, now, chunk_id))
            
            # Create version record
            conn.execute("""
                INSERT INTO chunk_versions
                (chunk_id, version, content_hash, state, timestamp, change_reason)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                chunk_id, 
                chunk.version + 1, 
                "", 
                new_state.value,
                now,
                reason or f"State change to {new_state.value}"
            ))
        
        return True
    
    def add_document_to_chunk(self, chunk_id: str, document_id: str, 
                              assignment_score: float = 1.0) -> bool:
        """
        Add a document to a chunk.
        
        Args:
            chunk_id: Target chunk
            document_id: Document to add
            assignment_score: Relevance score
            
        Returns:
            Success flag
        """
        from datetime import datetime
        
        chunk = self.get_chunk(chunk_id)
        if not chunk or chunk.state not in [ChunkState.CREATED, ChunkState.ACTIVE]:
            return False
        
        # Check capacity
        if chunk.current_size >= chunk.capacity:
            self.update_chunk_state(chunk_id, ChunkState.FULL, 
                                   "Capacity reached during document addition")
            return False
        
        # Check if document already in chunk
        if document_id in chunk.document_ids:
            return True  # Already added
        
        now = datetime.now().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            # Add document to chunk
            updated_docs = chunk.document_ids + [document_id]
            conn.execute("""
                UPDATE chunks 
                SET document_ids = ?, current_size = ?, updated_at = ?, version = version + 1
                WHERE chunk_id = ?
            """, (
                json.dumps(updated_docs),
                chunk.current_size + 1,
                now,
                chunk_id
            ))
            
            # Create assignment record
            conn.execute("""
                INSERT INTO document_chunk_assignments
                (document_id, chunk_id, assignment_score, assigned_at)
                VALUES (?, ?, ?, ?)
            """, (
                document_id,
                chunk_id,
                assignment_score,
                now
            ))
            
            # Create version record
            conn.execute("""
                INSERT INTO chunk_versions
                (chunk_id, version, content_hash, state, timestamp, change_reason)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                chunk_id, 
                chunk.version + 1, 
                "", 
                chunk.state.value,
                now,
                f"Added document {document_id}"
            ))
            
            # Check if we've hit the split threshold
            if (chunk.current_size + 1) >= chunk.capacity * self.config["split_threshold"]:
                conn.execute("""
                    UPDATE chunks SET state = ? WHERE chunk_id = ?
                """, (ChunkState.FULL.value, chunk_id))
        
        return True
    
    def remove_document_from_chunk(self, chunk_id: str, document_id: str) -> bool:
        """
        Remove a document from a chunk.
        
        Args:
            chunk_id: Source chunk
            document_id: Document to remove
            
        Returns:
            Success flag
        """
        from datetime import datetime
        
        chunk = self.get_chunk(chunk_id)
        if not chunk or chunk.state not in [ChunkState.ACTIVE, ChunkState.FULL, ChunkState.STALE]:
            return False
        
        # Check if document is in chunk
        if document_id not in chunk.document_ids:
            return False
        
        now = datetime.now().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            # Remove document from chunk
            updated_docs = [d for d in chunk.document_ids if d != document_id]
            conn.execute("""
                UPDATE chunks 
                SET document_ids = ?, current_size = ?, updated_at = ?, version = version + 1
                WHERE chunk_id = ?
            """, (
                json.dumps(updated_docs),
                chunk.current_size - 1,
                now,
                chunk_id
            ))
            
            # Remove assignment record
            conn.execute("""
                DELETE FROM document_chunk_assignments
                WHERE document_id = ? AND chunk_id = ?
            """, (document_id, chunk_id))
            
            # Create version record
            conn.execute("""
                INSERT INTO chunk_versions
                (chunk_id, version, content_hash, state, timestamp, change_reason)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                chunk_id, 
                chunk.version + 1, 
                "", 
                chunk.state.value,
                now,
                f"Removed document {document_id}"
            ))
            
            # Check if we've hit the merge threshold
            if (chunk.current_size - 1) <= chunk.capacity * self.config["merge_threshold"]:
                if chunk.state == ChunkState.FULL:
                    # If we were full, we're now active again
                    conn.execute("""
                        UPDATE chunks SET state = ? WHERE chunk_id = ?
                    """, (ChunkState.ACTIVE.value, chunk_id))
        
        return True
    
    def split_chunk(self, chunk_id: str, similarity_calculator=None) -> List[str]:
        """
        Split a chunk into multiple chunks based on similarity.
        
        Args:
            chunk_id: Chunk to split
            similarity_calculator: Optional similarity calculator instance
            
        Returns:
            List of new chunk IDs
        """
        chunk = self.get_chunk(chunk_id)
        if not chunk or chunk.state != ChunkState.FULL:
            return []
        
        # Mark as splitting
        self.update_chunk_state(chunk_id, ChunkState.SPLITTING, "Starting split operation")
        
        # Determine how to split (default: split in half)
        new_capacity = chunk.capacity // 2
        if new_capacity < 5:  # Minimum chunk size
            new_capacity = 5
        
        # Create two new chunks
        new_chunk_ids = []
        
        if similarity_calculator and len(chunk.document_ids) > 2:
            # Use similarity-based clustering if available
            try:
                # Assuming similarity_calculator.cluster_documents returns groups
                document_groups = similarity_calculator.cluster_documents(
                    chunk.document_ids, 
                    num_clusters=2
                )
                
                for i, doc_group in enumerate(document_groups):
                    new_id = self.create_chunk(
                        initial_docs=doc_group,
                        capacity=new_capacity,
                        tags=chunk.tags,
                        similarity_group=chunk.similarity_group
                    )
                    new_chunk_ids.append(new_id)
                    
            except Exception as e:
                # Fallback to simple split
                print(f"Error during similarity-based split: {e}")
                mid = len(chunk.document_ids) // 2
                new_chunk_ids.append(self.create_chunk(
                    initial_docs=chunk.document_ids[:mid],
                    capacity=new_capacity,
                    tags=chunk.tags,
                    similarity_group=chunk.similarity_group
                ))
                new_chunk_ids.append(self.create_chunk(
                    initial_docs=chunk.document_ids[mid:],
                    capacity=new_capacity,
                    tags=chunk.tags,
                    similarity_group=chunk.similarity_group
                ))
        else:
            # Simple split in half
            mid = len(chunk.document_ids) // 2
            new_chunk_ids.append(self.create_chunk(
                initial_docs=chunk.document_ids[:mid],
                capacity=new_capacity,
                tags=chunk.tags,
                similarity_group=chunk.similarity_group
            ))
            new_chunk_ids.append(self.create_chunk(
                initial_docs=chunk.document_ids[mid:],
                capacity=new_capacity,
                tags=chunk.tags,
                similarity_group=chunk.similarity_group
            ))
        
        # Update parent-child relationships
        with sqlite3.connect(self.db_path) as conn:
            for new_chunk_id in new_chunk_ids:
                # Add original as parent to new chunk
                new_chunk = self.get_chunk(new_chunk_id)
                conn.execute("""
                    UPDATE chunks 
                    SET parent_chunks = ?
                    WHERE chunk_id = ?
                """, (
                    json.dumps([chunk_id] + new_chunk.parent_chunks),
                    new_chunk_id
                ))
            
            # Add new chunks as children to original
            conn.execute("""
                UPDATE chunks 
                SET child_chunks = ?, state = ?
                WHERE chunk_id = ?
            """, (
                json.dumps(new_chunk_ids + chunk.child_chunks),
                ChunkState.ARCHIVED.value,
                chunk_id
            ))
        
        return new_chunk_ids
    
    def merge_chunks(self, chunk_ids: List[str]) -> Optional[str]:
        """
        Merge multiple chunks into a single new chunk.
        
        Args:
            chunk_ids: List of chunks to merge
            
        Returns:
            New chunk ID or None if failed
        """
        if len(chunk_ids) < 2:
            return None
        
        # Get all chunks
        chunks = [self.get_chunk(cid) for cid in chunk_ids]
        if any(c is None for c in chunks):
            return None
        
        # Mark chunks as merging
        for chunk in chunks:
            self.update_chunk_state(chunk.chunk_id, ChunkState.MERGING, "Starting merge operation")
        
        # Collect all documents and calculate new capacity
        all_docs = []
        for chunk in chunks:
            all_docs.extend(chunk.document_ids)
        
        # Remove duplicates while preserving order
        unique_docs = []
        seen = set()
        for doc in all_docs:
            if doc not in seen:
                seen.add(doc)
                unique_docs.append(doc)
        
        # Calculate new capacity - sum of original capacities
        new_capacity = sum(c.capacity for c in chunks)
        
        # Get common tags and similarity group
        common_tags = set(chunks[0].tags)
        for chunk in chunks[1:]:
            common_tags &= set(chunk.tags)
        
        similarity_groups = [c.similarity_group for c in chunks if c.similarity_group]
        similarity_group = similarity_groups[0] if similarity_groups else None
        
        # Create new merged chunk
        new_chunk_id = self.create_chunk(
            initial_docs=unique_docs,
            capacity=new_capacity,
            tags=list(common_tags),
            similarity_group=similarity_group
        )
        
        # Update parent-child relationships
        with sqlite3.connect(self.db_path) as conn:
            # Set all original parents as parents of new chunk
            all_parents = []
            for chunk in chunks:
                all_parents.extend(chunk.parent_chunks)
            all_parents = list(set(all_parents))  # Remove duplicates
            
            new_chunk = self.get_chunk(new_chunk_id)
            conn.execute("""
                UPDATE chunks 
                SET parent_chunks = ?
                WHERE chunk_id = ?
            """, (
                json.dumps(all_parents),
                new_chunk_id
            ))
            
            # Set all original chunks as parents of new chunk
            conn.execute("""
                UPDATE chunks 
                SET parent_chunks = ?
                WHERE chunk_id = ?
            """, (
                json.dumps(chunk_ids),
                new_chunk_id
            ))
            
            # Set new chunk as child of all original chunks
            for chunk_id in chunk_ids:
                chunk = self.get_chunk(chunk_id)
                conn.execute("""
                    UPDATE chunks 
                    SET child_chunks = ?, state = ?
                    WHERE chunk_id = ?
                """, (
                    json.dumps([new_chunk_id] + chunk.child_chunks),
                    ChunkState.ARCHIVED.value,
                    chunk_id
                ))
        
        return new_chunk_id
    
    def get_chunk_versions(self, chunk_id: str) -> List[Dict]:
        """
        Get version history for a chunk.
        
        Args:
            chunk_id: Target chunk
            
        Returns:
            List of version records
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("""
                SELECT * FROM chunk_versions
                WHERE chunk_id = ?
                ORDER BY version DESC
            """, (chunk_id,)).fetchall()
            
            return [dict(row) for row in rows]
    
    def find_chunks_by_state(self, state: ChunkState) -> List[str]:
        """
        Find all chunks in a particular state.
        
        Args:
            state: Target state
            
        Returns:
            List of chunk IDs
        """
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute("""
                SELECT chunk_id FROM chunks
                WHERE state = ?
            """, (state.value,)).fetchall()
            
            return [row[0] for row in rows]
    
    def run_garbage_collection(self) -> int:
        """
        Permanently remove chunks marked for deletion.
        
        Returns:
            Number of chunks removed
        """
        from datetime import datetime, timedelta
        
        # Find deleted chunks older than retention period
        retention_days = self.config["gc_retention_days"]
        cutoff_date = (datetime.now() - timedelta(days=retention_days)).isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            # Find chunks to delete
            rows = conn.execute("""
                SELECT chunk_id FROM chunks
                WHERE state = ? AND updated_at < ?
            """, (ChunkState.DELETED.value, cutoff_date)).fetchall()
            
            chunk_ids = [row[0] for row in rows]
            
            # Delete from all tables
            for chunk_id in chunk_ids:
                conn.execute("DELETE FROM chunk_versions WHERE chunk_id = ?", (chunk_id,))
                conn.execute("DELETE FROM chunk_relationships WHERE source_chunk_id = ? OR target_chunk_id = ?", 
                             (chunk_id, chunk_id))
                conn.execute("DELETE FROM document_chunk_assignments WHERE chunk_id = ?", (chunk_id,))
                conn.execute("DELETE FROM chunks WHERE chunk_id = ?", (chunk_id,))
                
                # Delete content file if exists
                chunk_path = self._get_chunk_path(chunk_id)
                if chunk_path.exists():
                    chunk_path.unlink()
        
        return len(chunk_ids)
    
    def get_chunk_content(self, chunk_id: str) -> Optional[Dict]:
        """
        Get the aggregated content of a chunk.
        
        Args:
            chunk_id: Target chunk
            
        Returns:
            Dictionary with chunk content and metadata
        """
        chunk = self.get_chunk(chunk_id)
        if not chunk:
            return None
        
        # Check if cached content exists
        content_path = self._get_chunk_path(chunk_id)
        if content_path.exists():
            try:
                with open(content_path, 'r', encoding='utf-8') as f:
                    content = json.load(f)
                    return content
            except Exception:
                pass  # Fall through to regeneration
        
        # Need to regenerate content
        return self._regenerate_chunk_content(chunk)
    
    def _get_chunk_path(self, chunk_id: str) -> Path:
        """Get path for chunk content file"""
        return self.chunks_dir / f"{chunk_id}.json"
    
    def _regenerate_chunk_content(self, chunk: ChunkMetadata) -> Dict:
        """
        Regenerate chunk content from individual documents.
        
        Args:
            chunk: Chunk metadata
            
        Returns:
            Dictionary with chunk content
        """
        # This would normally load documents from a document store
        # For now, create a skeleton structure
        document_contents = []
        for doc_id in chunk.document_ids:
            # Placeholder - would fetch actual document content
            document_contents.append({
                "id": doc_id,
                "title": f"Document {doc_id}",
                "content": "Document content would be loaded here"
            })
        
        content = {
            "chunk_id": chunk.chunk_id,
            "metadata": {
                "state": chunk.state.value,
                "version": chunk.version,
                "document_count": chunk.current_size,
                "capacity": chunk.capacity,
                "tags": chunk.tags,
                "similarity_group": chunk.similarity_group
            },
            "documents": document_contents,
            "generated_at": datetime.now().isoformat()
        }
        
        # Save to file
        content_path = self._get_chunk_path(chunk.chunk_id)
        with open(content_path, 'w', encoding='utf-8') as f:
            json.dump(content, f, indent=2)
        
        return content
    
    def find_chunks_containing_document(self, document_id: str) -> List[str]:
        """
        Find all chunks containing a specific document.
        
        Args:
            document_id: Target document
            
        Returns:
            List of chunk IDs
        """
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute("""
                SELECT chunk_id FROM document_chunk_assignments
                WHERE document_id = ?
            """, (document_id,)).fetchall()
            
            return [row[0] for row in rows]
    
    def get_chunk_stats(self) -> Dict[str, Any]:
        """
        Get overall statistics about chunks.
        
        Returns:
            Dictionary with statistics
        """
        with sqlite3.connect(self.db_path) as conn:
            # Total counts
            total = conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
            
            # By state
            state_counts = {}
            rows = conn.execute("""
                SELECT state, COUNT(*) FROM chunks
                GROUP BY state
            """).fetchall()
            for row in rows:
                state_counts[row[0]] = row[1]
            
            # Capacity metrics
            capacity_metrics = conn.execute("""
                SELECT 
                    AVG(current_size) as avg_size,
                    MAX(current_size) as max_size,
                    AVG(current_size * 1.0 / capacity) as avg_fill_ratio,
                    SUM(current_size) as total_documents
                FROM chunks
                WHERE state != ?
            """, (ChunkState.DELETED.value,)).fetchone()
            
            return {
                "total_chunks": total,
                "by_state": state_counts,
                "avg_size": capacity_metrics[0],
                "max_size": capacity_metrics[1],
                "avg_fill_ratio": capacity_metrics[2],
                "total_documents": capacity_metrics[3]
            }