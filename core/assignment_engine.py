class AssignmentEngine:
    """
    Intelligent document-to-chunk assignment system with conflict 
    resolution and load balancing.
    """
    
    def __init__(self, 
                 storage_path: str = "assignment_data",
                 chunk_manager: ChunkManager = None,
                 similarity_calculator: SimilarityCalculator = None):
        """
        Initialize the assignment engine.
        
        Args:
            storage_path: Directory to store assignment data
            chunk_manager: ChunkManager instance
            similarity_calculator: SimilarityCalculator instance
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        
        # Database for assignment tracking
        self.db_path = self.storage_path / "assignments.db"
        self._init_database()
        
        # Connect to chunk manager and similarity calculator
        self.chunk_manager = chunk_manager or ChunkManager()
        self.similarity_calculator = similarity_calculator or SimilarityCalculator()
        
        # Configuration
        self.config = {
            "default_strategy": AssignmentStrategy.HYBRID,
            "similarity_threshold": 0.6,
            "max_load_ratio": 0.9,  # Max ratio of chunks to fill
            "conflict_threshold": 0.8,  # Score diff to consider conflict
            "reassignment_cooldown": 3600,  # Seconds before reassignment
            "max_chunk_assignments": 50  # Max assignments per chunk
        }
        
        # Set up logging
        self.logger = logging.getLogger("AssignmentEngine")
        self.logger.setLevel(logging.INFO)
        
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            
            # Also log to file
            file_handler = logging.FileHandler(
                self.storage_path / "assignment_engine.log"
            )
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def _init_database(self):
        """Initialize SQLite database with assignment tables"""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS assignments (
                    document_id TEXT,
                    chunk_id TEXT,
                    status TEXT NOT NULL,
                    score REAL NOT NULL,
                    strategy TEXT NOT NULL,
                    assigned_at TEXT NOT NULL,
                    previous_chunk_id TEXT,
                    conflict_details TEXT,
                    metadata TEXT,
                    PRIMARY KEY (document_id, chunk_id)
                );
                
                CREATE TABLE IF NOT EXISTS assignment_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    document_id TEXT NOT NULL,
                    chunk_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    status TEXT NOT NULL,
                    score REAL,
                    previous_chunk_id TEXT,
                    timestamp TEXT NOT NULL,
                    details TEXT
                );
                
                CREATE TABLE IF NOT EXISTS assignment_conflicts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    document_id TEXT NOT NULL,
                    primary_chunk_id TEXT NOT NULL,
                    secondary_chunk_id TEXT NOT NULL,
                    primary_score REAL NOT NULL,
                    secondary_score REAL NOT NULL,
                    resolution TEXT,
                    resolved_at TEXT,
                    created_at TEXT NOT NULL
                );
                
                CREATE INDEX IF NOT EXISTS idx_assign_doc ON assignments(document_id);
                CREATE INDEX IF NOT EXISTS idx_assign_chunk ON assignments(chunk_id);
                CREATE INDEX IF NOT EXISTS idx_assign_status ON assignments(status);
                CREATE INDEX IF NOT EXISTS idx_history_doc ON assignment_history(document_id);
                CREATE INDEX IF NOT EXISTS idx_conflicts_doc ON assignment_conflicts(document_id);
            """)
    
    def assign_document(self, 
                       document_id: str, 
                       strategy: AssignmentStrategy = None,
                       target_chunk_id: str = None,
                       metadata: Dict = None) -> AssignmentRecord:
        """
        Assign a document to the most appropriate chunk.
        
        Args:
            document_id: Document to assign
            strategy: Assignment strategy to use
            target_chunk_id: Specific chunk to assign to (for manual strategy)
            metadata: Additional metadata for assignment
            
        Returns:
            AssignmentRecord with assignment details
        """
        strategy = strategy or self.config["default_strategy"]
        
        # Check if document is already assigned
        existing = self.get_document_assignment(document_id)
        if existing and existing.status == AssignmentStatus.ASSIGNED:
            self.logger.info(f"Document {document_id} already assigned to {existing.chunk_id}")
            return existing
        
        # Handle manual assignment
        if strategy == AssignmentStrategy.MANUAL and target_chunk_id:
            return self._assign_to_specific_chunk(document_id, target_chunk_id, metadata)
        
        # For other strategies, find the best chunk
        best_chunk_id, score = self._find_best_chunk(document_id, strategy)
        
        if not best_chunk_id:
            # No suitable chunk found, create a new one
            self.logger.info(f"No suitable chunk found for {document_id}, creating new chunk")
            best_chunk_id = self.chunk_manager.create_chunk(
                initial_docs=[],
                tags=metadata.get("tags", []) if metadata else None
            )
            score = 1.0  # Perfect score for a new empty chunk
        
        # Perform the assignment
        result = self._create_assignment(
            document_id=document_id,
            chunk_id=best_chunk_id,
            score=score,
            strategy=strategy,
            metadata=metadata
        )
        
        # Add document to chunk
        self.chunk_manager.add_document_to_chunk(best_chunk_id, document_id, score)
        
        return result
    
    def _assign_to_specific_chunk(self, 
                                document_id: str, 
                                chunk_id: str,
                                metadata: Dict = None) -> AssignmentRecord:
        """Assign document to a specific chunk (manual strategy)"""
        # Check if chunk exists
        chunk = self.chunk_manager.get_chunk(chunk_id)
        if not chunk:
            self.logger.error(f"Cannot assign to non-existent chunk {chunk_id}")
            
            # Create failed assignment record
            return AssignmentRecord(
                document_id=document_id,
                chunk_id=chunk_id,
                status=AssignmentStatus.FAILED,
                score=0.0,
                strategy=AssignmentStrategy.MANUAL,
                assigned_at=datetime.now().isoformat(),
                conflict_details={"error": "Chunk does not exist"}
            )
        
        # Check if chunk is full
        if chunk.current_size >= chunk.capacity:
            self.logger.warning(f"Chunk {chunk_id} is full, cannot assign document {document_id}")
            
            # Create failed assignment record
            return AssignmentRecord(
                document_id=document_id,
                chunk_id=chunk_id,
                status=AssignmentStatus.FAILED,
                score=0.0,
                strategy=AssignmentStrategy.MANUAL,
                assigned_at=datetime.now().isoformat(),
                conflict_details={"error": "Chunk is full"}
            )
        
        # Create assignment
        result = self._create_assignment(
            document_id=document_id,
            chunk_id=chunk_id,
            score=1.0,  # Manual assignment gets perfect score
            strategy=AssignmentStrategy.MANUAL,
            metadata=metadata
        )
        
        # Add document to chunk
        self.chunk_manager.add_document_to_chunk(chunk_id, document_id, 1.0)
        
        return result
    
    def _find_best_chunk(self, 
                       document_id: str, 
                       strategy: AssignmentStrategy) -> Tuple[Optional[str], float]:
        """
        Find the best chunk for a document based on strategy.
        
        Args:
            document_id: Document to assign
            strategy: Assignment strategy
            
        Returns:
            Tuple of (chunk_id, score) or (None, 0.0) if no suitable chunk
        """
        # Get active chunks
        active_chunks = self.chunk_manager.find_chunks_by_state(ChunkState.ACTIVE)
        if not active_chunks:
            return None, 0.0
        
        # Different strategies for finding the best chunk
        if strategy == AssignmentStrategy.SIMILARITY:
            return self._find_by_similarity(document_id, active_chunks)
        elif strategy == AssignmentStrategy.BALANCED:
            return self._find_by_load_balancing(document_id, active_chunks)
        elif strategy == AssignmentStrategy.METADATA:
            return self._find_by_metadata(document_id, active_chunks)
        elif strategy == AssignmentStrategy.HYBRID:
            # Combine similarity and load balancing
            sim_chunk, sim_score = self._find_by_similarity(document_id, active_chunks)
            bal_chunk, bal_score = self._find_by_load_balancing(document_id, active_chunks)
            
            # If similarity is strong enough, prefer it
            if sim_score >= self.config["similarity_threshold"] and sim_chunk:
                return sim_chunk, sim_score
            # Otherwise use load balancing
            elif bal_chunk:
                return bal_chunk, bal_score
            # If neither worked, return the better of the two
            elif sim_score > bal_score:
                return sim_chunk, sim_score
            else:
                return bal_chunk, bal_score
        else:
            # Default to similarity
            return self._find_by_similarity(document_id, active_chunks)
    
    def _find_by_similarity(self, 
                          document_id: str, 
                          chunk_ids: List[str]) -> Tuple[Optional[str], float]:
        """Find best chunk by content similarity"""
        best_chunk_id = None
        best_score = 0.0
        
        # Calculate similarity of document to each chunk
        for chunk_id in chunk_ids:
            # Get documents in chunk
            chunk = self.chunk_manager.get_chunk(chunk_id)
            if not chunk or chunk.current_size >= chunk.capacity:
                continue  # Skip full chunks
            
            # Skip empty chunks (they're handled by load balancing)
            if chunk.current_size == 0:
                continue
                
            # Calculate average similarity to documents in chunk
            sim_scores = []
            for doc_id in chunk.document_ids:
                sim = self.similarity_calculator.calculate_similarity(
                    document_id, doc_id
                )
                sim_scores.append(sim)
            
            # Calculate average similarity
            avg_sim = sum(sim_scores) / len(sim_scores) if sim_scores else 0.0
            
            # Check if this is the best so far
            if avg_sim > best_score:
                best_score = avg_sim
                best_chunk_id = chunk_id
        
        # Only return if similarity is above threshold
        if best_score >= self.config["similarity_threshold"]:
            return best_chunk_id, best_score
        else:
            return None, 0.0
    
    def _find_by_load_balancing(self, 
                              document_id: str, 
                              chunk_ids: List[str]) -> Tuple[Optional[str], float]:
        """Find best chunk by load balancing"""
        candidate_chunks = []
        
        # Calculate load factor for each chunk
        for chunk_id in chunk_ids:
            chunk = self.chunk_manager.get_chunk(chunk_id)
            if not chunk:
                continue
            
            # Skip full chunks
            if chunk.current_size >= chunk.capacity:
                continue
            
            # Calculate load factor (0-1)
            load_factor = chunk.current_size / chunk.capacity
            
            # Calculate available capacity
            available = chunk.capacity - chunk.current_size
            
            # Score is inverse of load factor (prefer emptier chunks)
            score = 1.0 - load_factor
            
            candidate_chunks.append((chunk_id, score, available, load_factor))
        
        if not candidate_chunks:
            return None, 0.0
        
        # Sort by score (highest first)
        candidate_chunks.sort(key=lambda x: x[1], reverse=True)
        
        # Return the best chunk
        best_chunk_id, score, _, _ = candidate_chunks[0]
        return best_chunk_id, score
    
    def _find_by_metadata(self, 
                        document_id: str, 
                        chunk_ids: List[str]) -> Tuple[Optional[str], float]:
        """Find best chunk by metadata matching"""
        # This would look at document metadata and match with chunk metadata
        # For this implementation, we'll just fall back to similarity
        return self._find_by_similarity(document_id, chunk_ids)
    
    def _create_assignment(self, 
                         document_id: str, 
                         chunk_id: str,
                         score: float,
                         strategy: AssignmentStrategy,
                         metadata: Dict = None) -> AssignmentRecord:
        """Create assignment record in database"""
        now = datetime.now().isoformat()
        
        # Check for existing assignments
        existing = self.get_document_assignment(document_id)
        previous_chunk_id = None
        
        if existing:
            previous_chunk_id = existing.chunk_id
            
            # If existing assignment is to same chunk, just update it
            if existing.chunk_id == chunk_id:
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute("""
                        UPDATE assignments
                        SET score = ?, strategy = ?, assigned_at = ?
                        WHERE document_id = ? AND chunk_id = ?
                    """, (
                        score,
                        strategy.value,
                        now,
                        document_id,
                        chunk_id
                    ))
                    
                    # Record in history
                    conn.execute("""
                        INSERT INTO assignment_history
                        (document_id, chunk_id, action, status, score, timestamp, details)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        document_id,
                        chunk_id,
                        "update",
                        AssignmentStatus.ASSIGNED.value,
                        score,
                        now,
                        json.dumps({"strategy": strategy.value})
                    ))
                
                return AssignmentRecord(
                    document_id=document_id,
                    chunk_id=chunk_id,
                    status=AssignmentStatus.ASSIGNED,
                    score=score,
                    strategy=strategy,
                    assigned_at=now,
                    metadata=metadata
                )
            
            # Otherwise, we need to handle reassignment
            self._handle_reassignment(document_id, existing.chunk_id, chunk_id)
        
        # Create new assignment
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO assignments
                (document_id, chunk_id, status, score, strategy, assigned_at, 
                 previous_chunk_id, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                document_id,
                chunk_id,
                AssignmentStatus.ASSIGNED.value,
                score,
                strategy.value,
                now,
                previous_chunk_id,
                json.dumps(metadata) if metadata else None
            ))
            
            # Record in history
            conn.execute("""
                INSERT INTO assignment_history
                (document_id, chunk_id, action, status, score, 
                 previous_chunk_id, timestamp, details)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                document_id,
                chunk_id,
                "assign" if not previous_chunk_id else "reassign",
                AssignmentStatus.ASSIGNED.value,
                score,
                previous_chunk_id,
                now,
                json.dumps({"strategy": strategy.value})
            ))
        
        return AssignmentRecord(
            document_id=document_id,
            chunk_id=chunk_id,
            status=AssignmentStatus.ASSIGNED,
            score=score,
            strategy=strategy,
            assigned_at=now,
            previous_chunk_id=previous_chunk_id,
            metadata=metadata
        )
    
    def _handle_reassignment(self, document_id: str, old_chunk_id: str, new_chunk_id: str):
        """Handle reassignment of document from one chunk to another"""
        # Remove from old chunk
        self.chunk_manager.remove_document_from_chunk(old_chunk_id, document_id)
        
        # Record reassignment
        now = datetime.now().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            # Mark any existing assignments as reassigned
            conn.execute("""
                UPDATE assignments
                SET status = ?, assigned_at = ?
                WHERE document_id = ? AND chunk_id = ?
            """, (
                AssignmentStatus.REASSIGNED.value,
                now,
                document_id,
                old_chunk_id
            ))
            
            # Record in history
            conn.execute("""
                INSERT INTO assignment_history
                (document_id, chunk_id, action, status, timestamp, details)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                document_id,
                old_chunk_id,
                "remove",
                AssignmentStatus.REASSIGNED.value,
                now,
                json.dumps({"new_chunk_id": new_chunk_id})
            ))
    
    def get_document_assignment(self, document_id: str) -> Optional[AssignmentRecord]:
        """Get current assignment for a document"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            row = conn.execute("""
                SELECT * FROM assignments
                WHERE document_id = ? AND status = ?
                ORDER BY assigned_at DESC
                LIMIT 1
            """, (document_id, AssignmentStatus.ASSIGNED.value)).fetchone()
            
            if not row:
                return None
            
            return AssignmentRecord(
                document_id=row['document_id'],
                chunk_id=row['chunk_id'],
                status=AssignmentStatus.ASSIGNED,
                score=row['score'],
                strategy=AssignmentStrategy(row['strategy']),
                assigned_at=row['assigned_at'],
                previous_chunk_id=row['previous_chunk_id'],
                metadata=json.loads(row['metadata']) if row['metadata'] else None
            )
    
    def get_chunk_assignments(self, chunk_id: str) -> List[AssignmentRecord]:
        """Get all assignments for a chunk"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            rows = conn.execute("""
                SELECT * FROM assignments
                WHERE chunk_id = ? AND status = ?
                ORDER BY assigned_at DESC
            """, (chunk_id, AssignmentStatus.ASSIGNED.value)).fetchall()
            
            return [
                AssignmentRecord(
                    document_id=row['document_id'],
                    chunk_id=row['chunk_id'],
                    status=AssignmentStatus.ASSIGNED,
                    score=row['score'],
                    strategy=AssignmentStrategy(row['strategy']),
                    assigned_at=row['assigned_at'],
                    previous_chunk_id=row['previous_chunk_id'],
                    metadata=json.loads(row['metadata']) if row['metadata'] else None
                )
                for row in rows
            ]
    
    def bulk_assign_documents(self, 
                            document_ids: List[str],
                            strategy: AssignmentStrategy = None,
                            metadata: Dict = None) -> Dict[str, AssignmentRecord]:
        """
        Assign multiple documents in a batch.
        
        Args:
            document_ids: List of document IDs to assign
            strategy: Assignment strategy to use
            metadata: Additional metadata for assignments
            
        Returns:
            Dictionary of document_id -> AssignmentRecord
        """
        strategy = strategy or self.config["default_strategy"]
        results = {}
        
        # For similarity-based strategies, need to precompute similarity matrix
        if strategy in [AssignmentStrategy.SIMILARITY, AssignmentStrategy.HYBRID]:
            # Precompute similarity matrix between documents
            self.similarity_calculator.build_similarity_matrix(document_ids)
        
        # First pass: find best chunks for all documents
        assignments = []
        
        for doc_id in document_ids:
            # Handle already assigned documents
            existing = self.get_document_assignment(doc_id)
            if existing and existing.status == AssignmentStatus.ASSIGNED:
                results[doc_id] = existing
                continue
            
            # Find best chunk
            best_chunk_id, score = self._find_best_chunk(doc_id, strategy)
            
            if not best_chunk_id:
                # No suitable chunk found, will create one later
                assignments.append((doc_id, None, 0.0))
            else:
                assignments.append((doc_id, best_chunk_id, score))
        
        # Group by chunks to handle capacity constraints
        chunk_assignments = {}
        
        for doc_id, chunk_id, score in assignments:
            if chunk_id:
                if chunk_id not in chunk_assignments:
                    chunk_assignments[chunk_id] = []
                chunk_assignments[chunk_id].append((doc_id, score))
        
        # Check capacity constraints
        for chunk_id, docs in chunk_assignments.items():
            chunk = self.chunk_manager.get_chunk(chunk_id)
            if not chunk:
                continue
            
            # If too many assignments for chunk capacity, keep only top scoring ones
            available_capacity = chunk.capacity - chunk.current_size
            if len(docs) > available_capacity:
                # Sort by score (highest first) and keep only what fits
                docs.sort(key=lambda x: x[1], reverse=True)
                assigned_docs = docs[:available_capacity]
                rejected_docs = docs[available_capacity:]
                
                # Update assignments for rejected docs
                for doc_id, _ in rejected_docs:
                    # Find position in assignments list
                    for i, (d, c, s) in enumerate(assignments):
                        if d == doc_id and c == chunk_id:
                            # Mark as needing a new chunk
                            assignments[i] = (doc_id, None, 0.0)
                            break
                
                # Update chunk assignments
                chunk_assignments[chunk_id] = assigned_docs
        
        # Second pass: handle documents without chunks
        new_chunks = {}
        
        for i, (doc_id, chunk_id, score) in enumerate(assignments):
            if not chunk_id:
                # No chunk assigned, either create a new one or find an existing new one
                # Group documents to minimize new chunks
                doc_group = None
                
                for group_id, group_docs in new_chunks.items():
                    # Check if group has space
                    if len(group_docs) < self.config["max_chunk_assignments"]:
                        doc_group = group_id
                        break
                
                if not doc_group:
                    # Create a new chunk
                    doc_group = f"new_chunk_{len(new_chunks) + 1}"
                    new_chunks[doc_group] = []
                
                new_chunks[doc_group].append(doc_id)
                assignments[i] = (doc_id, doc_group, 1.0)
        
        # Create actual chunks for new_chunks
        chunk_id_map = {}
        
        for group_id, group_docs in new_chunks.items():
            # Create a new chunk
            actual_chunk_id = self.chunk_manager.create_chunk(
                initial_docs=[],
                tags=metadata.get("tags", []) if metadata else None
            )
            chunk_id_map[group_id] = actual_chunk_id
        
        # Final pass: perform actual assignments
        for doc_id, chunk_id, score in assignments:
            if chunk_id in chunk_id_map:
                # Map virtual chunk ID to actual chunk ID
                chunk_id = chunk_id_map[chunk_id]
            
            # Perform the assignment
            result = self._create_assignment(
                document_id=doc_id,
                chunk_id=chunk_id,
                score=score,
                strategy=strategy,
                metadata=metadata
            )
            
            # Add document to chunk
            self.chunk_manager.add_document_to_chunk(chunk_id, doc_id, score)
            
            # Store result
            results[doc_id] = result
        
        return results
    
    def optimize_assignments(self, 
                           target_chunks: List[str] = None,
                           strategy: AssignmentStrategy = None) -> Dict[str, Any]:
        """
        Optimize document assignments across chunks.
        
        Args:
            target_chunks: Specific chunks to optimize, or None for all
            strategy: Optimization strategy
            
        Returns:
            Statistics about optimizations performed
        """
        strategy = strategy or self.config["default_strategy"]
        
        # If no target chunks specified, use all active chunks
        if not target_chunks:
            target_chunks = self.chunk_manager.find_chunks_by_state(ChunkState.ACTIVE)
        
        if not target_chunks:
            return {"error": "No chunks to optimize"}
        
        # Collect all documents across chunks
        all_documents = set()
        chunk_loads = {}
        
        for chunk_id in target_chunks:
            chunk = self.chunk_manager.get_chunk(chunk_id)
            if not chunk:
                continue
            
            # Add documents to set
            all_documents.update(chunk.document_ids)
            
            # Record load factor
            chunk_loads[chunk_id] = chunk.current_size / chunk.capacity
        
        # Convert to list for consistent ordering
        document_ids = list(all_documents)
        
        # Skip if no documents
        if not document_ids:
            return {"message": "No documents to optimize"}
        
        # Calculate optimal assignments
        if strategy == AssignmentStrategy.BALANCED:
            optimal_assignments = self._optimize_for_balance(document_ids, target_chunks)
        elif strategy == AssignmentStrategy.SIMILARITY:
            optimal_assignments = self._optimize_for_similarity(document_ids, target_chunks)
        else:
            # Default to hybrid approach
            optimal_assignments = self._optimize_hybrid(document_ids, target_chunks)
        
        # Apply changes
        changes = self._apply_optimized_assignments(optimal_assignments)
        
        # Return statistics
        return {
            "optimized_chunks": len(target_chunks),
            "total_documents": len(document_ids),
            "documents_reassigned": changes["reassigned"],
            "conflicts_resolved": changes["conflicts_resolved"],
            "load_balance_before": self._calculate_load_variance(chunk_loads),
            "load_balance_after": self._calculate_load_variance(changes["new_loads"])
        }
    
    def _optimize_for_balance(self, 
                            document_ids: List[str], 
                            chunk_ids: List[str]) -> Dict[str, str]:
        """Optimize assignments for load balancing"""
        # Get chunks and their capacities
        chunks = {}
        for chunk_id in chunk_ids:
            chunk = self.chunk_manager.get_chunk(chunk_id)
            if chunk:
                chunks[chunk_id] = {
                    "capacity": chunk.capacity,
                    "current_size": 0,  # Will be filled in assignment process
                    "documents": []  # Will be filled in assignment process
                }
        
        # Count total capacity
        total_capacity = sum(c["capacity"] for c in chunks.values())
        total_documents = len(document_ids)
        
        if total_capacity < total_documents:
            # Not enough capacity, need to create new chunks
            # But that's out of scope for this optimization
            self.logger.warning(
                f"Not enough capacity ({total_capacity}) for all documents ({total_documents})"
            )
        
        # Simple round-robin assignment for balance
        # Sort chunks by capacity (highest first)
        sorted_chunks = sorted(
            chunks.keys(), 
            key=lambda cid: chunks[cid]["capacity"],
            reverse=True
        )
        
        # Assign documents in round-robin fashion
        assignments = {}
        chunk_index = 0
        
        for doc_id in document_ids:
            # Find next chunk with available capacity
            assigned = False
            for _ in range(len(sorted_chunks)):
                chunk_id = sorted_chunks[chunk_index]
                chunk = chunks[chunk_id]
                
                if chunk["current_size"] < chunk["capacity"]:
                    # Assign to this chunk
                    assignments[doc_id] = chunk_id
                    chunk["current_size"] += 1
                    chunk["documents"].append(doc_id)
                    assigned = True
                    break
                
                # Try next chunk
                chunk_index = (chunk_index + 1) % len(sorted_chunks)
            
            if not assigned:
                # No capacity left, leave assignment as is
                # (This document will be ignored in _apply_optimized_assignments)
                current = self.get_document_assignment(doc_id)
                if current:
                    assignments[doc_id] = current.chunk_id
        
        return assignments
    
    def _optimize_for_similarity(self, 
                               document_ids: List[str], 
                               chunk_ids: List[str]) -> Dict[str, str]:
        """Optimize assignments for content similarity"""
        # Build similarity matrix between all documents
        sim_matrix = self.similarity_calculator.build_similarity_matrix(document_ids)
        
        # Get chunks and their current documents
        chunks = {}
        for chunk_id in chunk_ids:
            chunk = self.chunk_manager.get_chunk(chunk_id)
            if chunk:
                chunks[chunk_id] = {
                    "capacity": chunk.capacity,
                    "documents": list(chunk.document_ids),
                    "centroid": None  # Will calculate below
                }
        
        # Calculate document-to-chunk similarity
        doc_chunk_similarity = {}
        
        for doc_id in document_ids:
            doc_chunk_similarity[doc_id] = {}
            
            for chunk_id, chunk_data in chunks.items():
                # Calculate similarity to documents in this chunk
                similarities = []
                
                for existing_doc in chunk_data["documents"]:
                    if existing_doc == doc_id:
                        continue  # Skip self
                    
                    # Get similarity from matrix
                    sim_key = (doc_id, existing_doc)
                    alt_key = (existing_doc, doc_id)
                    
                    if sim_key in sim_matrix:
                        similarities.append(sim_matrix[sim_key])
                    elif alt_key in sim_matrix:
                        similarities.append(sim_matrix[alt_key])
                
                # Average similarity to chunk
                if similarities:
                    avg_sim = sum(similarities) / len(similarities)
                else:
                    avg_sim = 0.0
                
                doc_chunk_similarity[doc_id][chunk_id] = avg_sim
        
        # Assign each document to most similar chunk
        assignments = {}
        for doc_id in document_ids:
            # Find most similar chunk with capacity
            best_chunk = None
            best_sim = -1.0
            
            for chunk_id, chunk_data in chunks.items():
                # Skip if no capacity
                if len(chunk_data["documents"]) >= chunk_data["capacity"]:
                    continue
                
                sim = doc_chunk_similarity[doc_id].get(chunk_id, 0.0)
                if sim > best_sim:
                    best_sim = sim
                    best_chunk = chunk_id
            
            if best_chunk and best_sim > self.config["similarity_threshold"]:
                # Assign to this chunk
                assignments[doc_id] = best_chunk
                chunks[best_chunk]["documents"].append(doc_id)
            else:
                # No good match, leave as is
                current = self.get_document_assignment(doc_id)
                if current:
                    assignments[doc_id] = current.chunk_id
        
        return assignments
    
    def _optimize_hybrid(self, 
                       document_ids: List[str], 
                       chunk_ids: List[str]) -> Dict[str, str]:
        """Optimize assignments with a hybrid approach"""
        # First optimize for similarity to get a baseline
        sim_assignments = self._optimize_for_similarity(document_ids, chunk_ids)
        
        # Get chunks and their capacities
        chunks = {}
        for chunk_id in chunk_ids:
            chunk = self.chunk_manager.get_chunk(chunk_id)
            if chunk:
                chunks[chunk_id] = {
                    "capacity": chunk.capacity,
                    "current_size": 0,
                    "documents": []
                }
        
        # Calculate projected load based on similarity assignments
        for doc_id, chunk_id in sim_assignments.items():
            if chunk_id in chunks:
                chunks[chunk_id]["current_size"] += 1
                chunks[chunk_id]["documents"].append(doc_id)
        
        # Calculate load variance
        load_factors = [c["current_size"] / c["capacity"] for c in chunks.values()]
        variance = self._calculate_load_variance(
            {cid: c["current_size"] / c["capacity"] for cid, c in chunks.items()}
        )
        
        # If variance is high, adjust assignments to balance load
        if variance > 0.15:  # Threshold for imbalance
            # Identify overloaded and underloaded chunks
            overloaded = [
                cid for cid, c in chunks.items() 
                if c["current_size"] / c["capacity"] > 0.85  # More than 85% full
            ]
            
            underloaded = [
                cid for cid, c in chunks.items()
                if c["current_size"] / c["capacity"] < 0.5  # Less than 50% full
            ]
            
            if overloaded and underloaded:
                # Move some documents from overloaded to underloaded
                for over_chunk in overloaded:
                    # Calculate how many to move
                    chunk = chunks[over_chunk]
                    target_size = int(chunk["capacity"] * 0.7)  # Target 70% load
                    to_move = max(0, chunk["current_size"] - target_size)
                    
                    if to_move == 0:
                        continue
                    
                    # Find documents to move (least similar to chunk)
                    docs_to_move = []
                    docs_in_chunk = [
                        d for d in chunk["documents"] 
                        if sim_assignments.get(d) == over_chunk
                    ]
                    
                    # Build document similarity to chunk
                    doc_sim = {}
                    for doc_id in docs_in_chunk:
                        # Get average similarity to other docs in chunk
                        similarities = []
                        for other_doc in docs_in_chunk:
                            if other_doc == doc_id:
                                continue
                            
                            # Get similarity
                            sim_key = (doc_id, other_doc)
                            alt_key = (other_doc, doc_id)
                            
                            if sim_key in sim_matrix:
                                similarities.append(sim_matrix[sim_key])
                            elif alt_key in sim_matrix:
                                similarities.append(sim_matrix[alt_key])
                        
                        # Average similarity
                        if similarities:
                            doc_sim[doc_id] = sum(similarities) / len(similarities)
                        else:
                            doc_sim[doc_id] = 0.0
                    
                    # Sort by similarity (ascending)
                    sorted_docs = sorted(docs_in_chunk, key=lambda d: doc_sim.get(d, 0.0))
                    
                    # Select docs to move
                    docs_to_move = sorted_docs[:to_move]
                    
                    # Assign to underloaded chunks
                    for doc_id in docs_to_move:
                        # Find best underloaded chunk
                        best_under = None
                        best_sim = -1.0
                        
                        for under_chunk in underloaded:
                            # Skip if full
                            if chunks[under_chunk]["current_size"] >= chunks[under_chunk]["capacity"]:
                                continue
                            
                            # Calculate similarity to this chunk
                            u_chunk = chunks[under_chunk]
                            similarities = []
                            
                            for other_doc in u_chunk["documents"]:
                                # Get similarity
                                sim_key = (doc_id, other_doc)
                                alt_key = (other_doc, doc_id)
                                
                                if sim_key in sim_matrix:
                                    similarities.append(sim_matrix[sim_key])
                                elif alt_key in sim_matrix:
                                    similarities.append(sim_matrix[alt_key])
                            
                            # Average similarity
                            if similarities:
                                sim = sum(similarities) / len(similarities)
                            else:
                                sim = 0.0
                            
                            if sim > best_sim:
                                best_sim = sim
                                best_under = under_chunk
                        
                        if best_under:
                            # Update assignment
                            sim_assignments[doc_id] = best_under
                            
                            # Update chunk tracking
                            chunks[over_chunk]["current_size"] -= 1
                            chunks[over_chunk]["documents"].remove(doc_id)
                            
                            chunks[best_under]["current_size"] += 1
                            chunks[best_under]["documents"].append(doc_id)
        
        return sim_assignments
    
    def _apply_optimized_assignments(self, assignments: Dict[str, str]) -> Dict[str, Any]:
        """
        Apply optimized assignments.
        
        Args:
            assignments: Document ID -> Chunk ID mapping
            
        Returns:
            Statistics about changes made
        """
        # Track changes
        changes = {
            "reassigned": 0,
            "conflicts_resolved": 0,
            "new_loads": {}
        }
        
        # Create batch for each chunk
        chunk_batches = {}
        
        for doc_id, chunk_id in assignments.items():
            if chunk_id not in chunk_batches:
                chunk_batches[chunk_id] = []
            chunk_batches[chunk_id].append(doc_id)
        
        # Process each batch
        for chunk_id, doc_ids in chunk_batches.items():
            # Get chunk info
            chunk = self.chunk_manager.get_chunk(chunk_id)
            if not chunk:
                continue
            
            # Get current assignments
            current_assignments = {}
            for doc_id in doc_ids:
                current = self.get_document_assignment(doc_id)
                if current:
                    current_assignments[doc_id] = current
            
            # Apply changes
            for doc_id in doc_ids:
                current = current_assignments.get(doc_id)
                
                if not current:
                    # New assignment
                    self._create_assignment(
                        document_id=doc_id,
                        chunk_id=chunk_id,
                        score=1.0,  # Default score
                        strategy=AssignmentStrategy.HYBRID,
                        metadata={"source": "optimization"}
                    )
                    
                    # Add to chunk
                    self.chunk_manager.add_document_to_chunk(chunk_id, doc_id, 1.0)
                    
                    changes["reassigned"] += 1
                elif current.chunk_id != chunk_id:
                    # Reassignment
                    previous_chunk_id = current.chunk_id
                    
                    # Remove from old chunk
                    self.chunk_manager.remove_document_from_chunk(previous_chunk_id, doc_id)
                    
                    # Create new assignment
                    self._create_assignment(
                        document_id=doc_id,
                        chunk_id=chunk_id,
                        score=1.0,  # Default score
                        strategy=AssignmentStrategy.HYBRID,
                        metadata={"source": "optimization"}
                    )
                    
                    # Add to new chunk
                    self.chunk_manager.add_document_to_chunk(chunk_id, doc_id, 1.0)
                    
                    changes["reassigned"] += 1
            
            # Update load tracking
            changes["new_loads"][chunk_id] = len(doc_ids) / chunk.capacity
        
        return changes
    
    def _calculate_load_variance(self, loads: Dict[str, float]) -> float:
        """Calculate variance of load factors"""
        if not loads:
            return 0.0
        
        values = list(loads.values())
        mean = sum(values) / len(values)
        
        # Calculate variance
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        
        return variance
    
    def detect_conflicts(self, threshold: float = None) -> List[Dict]:
        """
        Detect assignment conflicts.
        
        Args:
            threshold: Score difference threshold (default from config)
            
        Returns:
            List of conflict details
        """
        if threshold is None:
            threshold = self.config["conflict_threshold"]
        
        # Get all active chunks
        active_chunks = self.chunk_manager.find_chunks_by_state(ChunkState.ACTIVE)
        
        # Get all assigned documents
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("""
                SELECT document_id, chunk_id, score
                FROM assignments
                WHERE status = ?
            """, (AssignmentStatus.ASSIGNED.value,)).fetchall()
            
            assignments = {}
            for row in rows:
                doc_id = row['document_id']
                if doc_id not in assignments:
                    assignments[doc_id] = []
                
                assignments[doc_id].append((row['chunk_id'], row['score']))
        
        # Detect conflicts
        conflicts = []
        
        for doc_id, chunks in assignments.items():
            if len(chunks) > 1:
                # Sort by score (highest first)
                chunks.sort(key=lambda x: x[1], reverse=True)
                
                # Check if top two are close
                if len(chunks) >= 2:
                    chunk1, score1 = chunks[0]
                    chunk2, score2 = chunks[1]
                    
                    diff = score1 - score2
                    if diff < threshold:
                        # Conflict detected
                        conflicts.append({
                            "document_id": doc_id,
                            "primary_chunk": chunk1,
                            "secondary_chunk": chunk2,
                            "primary_score": score1,
                            "secondary_score": score2,
                            "score_difference": diff
                        })
        
        return conflicts
    
    def resolve_conflicts(self, 
                        conflicts: List[Dict] = None, 
                        strategy: AssignmentStrategy = None) -> Dict[str, Any]:
        """
        Resolve assignment conflicts.
        
        Args:
            conflicts: List of conflicts to resolve (or None to auto-detect)
            strategy: Resolution strategy
            
        Returns:
            Statistics about resolved conflicts
        """
        strategy = strategy or self.config["default_strategy"]
        
        # Auto-detect conflicts if not provided
        if conflicts is None:
            conflicts = self.detect_conflicts()
        
        if not conflicts:
            return {"message": "No conflicts to resolve"}
        
        # Track changes
        changes = {
            "resolved": 0,
            "kept_primary": 0,
            "kept_secondary": 0,
            "reassigned": 0
        }
        
        for conflict in conflicts:
            doc_id = conflict["document_id"]
            primary_chunk = conflict["primary_chunk"]
            secondary_chunk = conflict["secondary_chunk"]
            
            # Resolution decision
            resolution = None
            
            if strategy == AssignmentStrategy.SIMILARITY:
                # Keep highest similarity (primary)
                resolution = primary_chunk
                changes["kept_primary"] += 1
            elif strategy == AssignmentStrategy.BALANCED:
                # Choose based on load balancing
                primary_chunk_obj = self.chunk_manager.get_chunk(primary_chunk)
                secondary_chunk_obj = self.chunk_manager.get_chunk(secondary_chunk)
                
                if (primary_chunk_obj and secondary_chunk_obj and
                    primary_chunk_obj.current_size > secondary_chunk_obj.current_size):
                    # Primary is more loaded, choose secondary
                    resolution = secondary_chunk
                    changes["kept_secondary"] += 1
                else:
                    # Default to primary
                    resolution = primary_chunk
                    changes["kept_primary"] += 1
            else:
                # Hybrid: consider both similarity and balance
                primary_score = conflict["primary_score"]
                secondary_score = conflict["secondary_score"]
                
                # If scores are very close, consider load
                if abs(primary_score - secondary_score) < 0.1:
                    # Choose based on load
                    primary_chunk_obj = self.chunk_manager.get_chunk(primary_chunk)
                    secondary_chunk_obj = self.chunk_manager.get_chunk(secondary_chunk)
                    
                    if (primary_chunk_obj and secondary_chunk_obj and
                        primary_chunk_obj.current_size > secondary_chunk_obj.current_size):
                        # Primary is more loaded, choose secondary
                        resolution = secondary_chunk
                        changes["kept_secondary"] += 1
                    else:
                        # Default to primary
                        resolution = primary_chunk
                        changes["kept_primary"] += 1
                else:
                    # Significant difference, choose primary
                    resolution = primary_chunk
                    changes["kept_primary"] += 1
            
            # Apply resolution
            if resolution == primary_chunk:
                # Keep primary, remove secondary
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute("""
                        UPDATE assignments
                        SET status = ?
                        WHERE document_id = ? AND chunk_id = ?
                    """, (
                        AssignmentStatus.CONFLICTED.value,
                        doc_id,
                        secondary_chunk
                    ))
                
                # Remove from secondary chunk
                self.chunk_manager.remove_document_from_chunk(secondary_chunk, doc_id)
            elif resolution == secondary_chunk:
                # Keep secondary, remove primary
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute("""
                        UPDATE assignments
                        SET status = ?
                        WHERE document_id = ? AND chunk_id = ?
                    """, (
                        AssignmentStatus.CONFLICTED.value,
                        doc_id,
                        primary_chunk
                    ))
                
                # Remove from primary chunk
                self.chunk_manager.remove_document_from_chunk(primary_chunk, doc_id)
            else:
                # New resolution (neither primary nor secondary)
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute("""
                        UPDATE assignments
                        SET status = ?
                        WHERE document_id = ? AND chunk_id IN (?, ?)
                    """, (
                        AssignmentStatus.CONFLICTED.value,
                        doc_id,
                        primary_chunk,
                        secondary_chunk
                    ))
                
                # Remove from both chunks
                self.chunk_manager.remove_document_from_chunk(primary_chunk, doc_id)
                self.chunk_manager.remove_document_from_chunk(secondary_chunk, doc_id)
                
                # Create new assignment
                self._create_assignment(
                    document_id=doc_id,
                    chunk_id=resolution,
                    score=1.0,
                    strategy=strategy,
                    metadata={"source": "conflict_resolution"}
                )
                
                changes["reassigned"] += 1
            
            # Record conflict resolution
            now = datetime.now().isoformat()
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO assignment_conflicts
                    (document_id, primary_chunk_id, secondary_chunk_id,
                     primary_score, secondary_score, resolution, resolved_at, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    doc_id,
                    primary_chunk,
                    secondary_chunk,
                    conflict["primary_score"],
                    conflict["secondary_score"],
                    resolution,
                    now,
                    now
                ))
            
            changes["resolved"] += 1
        
        return changes
    
    def get_assignment_history(self, document_id: str) -> List[Dict]:
        """Get assignment history for a document"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            rows = conn.execute("""
                SELECT * FROM assignment_history
                WHERE document_id = ?
                ORDER BY timestamp DESC
            """, (document_id,)).fetchall()
            
            return [dict(row) for row in rows]
    
    def get_assignment_stats(self) -> Dict[str, Any]:
        """Get statistics about assignments"""
        with sqlite3.connect(self.db_path) as conn:
            # Overall counts
            counts = conn.execute("""
                SELECT status, COUNT(*) as count
                FROM assignments
                GROUP BY status
            """).fetchall()
            
            status_counts = {status: count for status, count in counts}
            
            # Strategy counts
            strategies = conn.execute("""
                SELECT strategy, COUNT(*) as count
                FROM assignments
                WHERE status = ?
                GROUP BY strategy
            """, (AssignmentStatus.ASSIGNED.value,)).fetchall()
            
            strategy_counts = {strategy: count for strategy, count in strategies}
            
            # Conflict counts
            conflict_count = conn.execute("""
                SELECT COUNT(*) FROM assignment_conflicts
            """).fetchone()[0]
            
            resolved_count = conn.execute("""
                SELECT COUNT(*) FROM assignment_conflicts
                WHERE resolution IS NOT NULL
            """).fetchone()[0]
            
            # Average scores
            avg_score = conn.execute("""
                SELECT AVG(score) FROM assignments
                WHERE status = ?
            """, (AssignmentStatus.ASSIGNED.value,)).fetchone()[0]
            
            return {
                "total_assignments": sum(status_counts.values()),
                "by_status": status_counts,
                "by_strategy": strategy_counts,
                "conflicts": {
                    "total": conflict_count,
                    "resolved": resolved_count,
                    "unresolved": conflict_count - resolved_count
                },
                "average_score": avg_score
            }import sqlite3
from typing import List, Dict, Tuple, Set, Any, Optional
from dataclasses import dataclass
import json
from datetime import datetime
from pathlib import Path
import heapq
import hashlib
from enum import Enum
import logging
import time
import os

# Import internal components
from core.chunk_manager import ChunkManager, ChunkState
from core.similarity_calculator import SimilarityCalculator


class AssignmentStrategy(Enum):
    """Strategies for assigning documents to chunks"""
    SIMILARITY = "similarity"  # Based on content similarity
    BALANCED = "balanced"      # Prioritize load balancing
    HYBRID = "hybrid"          # Balance similarity and load
    METADATA = "metadata"      # Based on metadata matching
    MANUAL = "manual"          # Manual assignments


class AssignmentStatus(Enum):
    """Status of a document assignment"""
    PENDING = "pending"       # Assignment is pending
    ASSIGNED = "assigned"     # Successfully assigned
    FAILED = "failed"         # Assignment failed
    CONFLICTED = "conflicted" # Conflicting assignment exists
    REASSIGNED = "reassigned" # Document was reassigned


@dataclass
class AssignmentRecord:
    """Record of a document assignment to a chunk"""
    document_id: str
    chunk_id: str
    status: AssignmentStatus
    score: float
    strategy: AssignmentStrategy
    assigned_at: str
    previous_chunk_id: Optional[str] = None
    conflict_details: Optional[Dict] = None
    metadata: Optional[Dict] = None