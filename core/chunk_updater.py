# core/chunk_updater.py

from typing import Dict, Any, List, Optional, Tuple, Set
import difflib
import json
import hashlib
from datetime import datetime
from pathlib import Path

class ChunkDiff:
    """Represents differences between chunk versions"""
    
    def __init__(self, original: str, updated: str, chunk_id: str):
        self.original = original
        self.updated = updated
        self.chunk_id = chunk_id
        self.diff = self._generate_diff()
        self.change_summary = self._summarize_changes()
    
    def _generate_diff(self) -> List[str]:
        """Generate unified diff between original and updated content"""
        return list(difflib.unified_diff(
            self.original.splitlines(),
            self.updated.splitlines(),
            lineterm='',
            n=3  # Context lines
        ))
    
    def _summarize_changes(self) -> Dict[str, int]:
        """Summarize the types and extent of changes"""
        adds = 0
        removes = 0
        changes = 0
        
        for line in self.diff:
            if line.startswith('+') and not line.startswith('+++'):
                adds += 1
            elif line.startswith('-') and not line.startswith('---'):
                removes += 1
        
        # Estimate changed lines (heuristic)
        changes = min(adds, removes)
        adds -= changes
        removes -= changes
        
        return {
            'additions': adds,
            'deletions': removes,
            'modifications': changes,
            'total_lines_affected': adds + removes + changes
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert diff to a dictionary representation"""
        return {
            'chunk_id': self.chunk_id,
            'timestamp': datetime.now().isoformat(),
            'diff': self.diff,
            'summary': self.change_summary,
            'original_hash': hashlib.md5(self.original.encode()).hexdigest(),
            'updated_hash': hashlib.md5(self.updated.encode()).hexdigest()
        }


class ThreeWayMerger:
    """Implements three-way merge for content conflicts"""
    
    @staticmethod
    def merge(base: str, ours: str, theirs: str) -> Tuple[str, bool, List[str]]:
        """
        Perform three-way merge between versions
        
        Args:
            base: Original content (common ancestor)
            ours: Our updated version
            theirs: Their updated version
            
        Returns:
            Tuple of (merged_content, has_conflicts, conflict_regions)
        """
        # Convert to lines for diffing
        base_lines = base.splitlines()
        ours_lines = ours.splitlines()
        theirs_lines = theirs.splitlines()
        
        # Get diffs
        ours_diff = list(difflib.ndiff(base_lines, ours_lines))
        theirs_diff = list(difflib.ndiff(base_lines, theirs_lines))
        
        # Initialize merge result
        merged_lines = []
        conflicts = []
        has_conflict = False
        
        # Build line maps for changes
        ours_changes = {}
        theirs_changes = {}
        
        # Process our changes
        base_idx = 0
        for line in ours_diff:
            if line.startswith('- '):
                # Line removed in ours
                ours_changes[base_idx] = ('remove', None)
                base_idx += 1
            elif line.startswith('+ '):
                # Line added in ours
                ours_changes[base_idx-0.5] = ('add', line[2:])
            elif line.startswith('  '):
                # Unchanged line
                base_idx += 1
        
        # Process their changes
        base_idx = 0
        for line in theirs_diff:
            if line.startswith('- '):
                # Line removed in theirs
                theirs_changes[base_idx] = ('remove', None)
                base_idx += 1
            elif line.startswith('+ '):
                # Line added in theirs
                theirs_changes[base_idx-0.5] = ('add', line[2:])
            elif line.startswith('  '):
                # Unchanged line
                base_idx += 1
        
        # Merge changes
        base_idx = 0
        while base_idx < len(base_lines):
            our_change = ours_changes.get(base_idx, None)
            their_change = theirs_changes.get(base_idx, None)
            
            if our_change is None and their_change is None:
                # No changes from either side
                merged_lines.append(base_lines[base_idx])
            elif our_change and their_change:
                # Both sides changed the same line
                if our_change[0] == 'remove' and their_change[0] == 'remove':
                    # Both removed - skip
                    pass
                else:
                    # Conflict
                    has_conflict = True
                    conflict_region = [
                        "<<<<<<< OURS",
                        ours_lines[base_idx] if our_change[0] != 'remove' else "",
                        "=======",
                        theirs_lines[base_idx] if their_change[0] != 'remove' else "",
                        ">>>>>>> THEIRS"
                    ]
                    merged_lines.extend(conflict_region)
                    conflicts.append('\n'.join(conflict_region))
            elif our_change:
                # Only we changed
                if our_change[0] != 'remove':
                    merged_lines.append(ours_lines[base_idx])
            elif their_change:
                # Only they changed
                if their_change[0] != 'remove':
                    merged_lines.append(theirs_lines[base_idx])
            
            base_idx += 1
        
        # Handle added lines
        for idx in sorted(set(list(ours_changes.keys()) + list(theirs_changes.keys()))):
            if isinstance(idx, float):  # Added lines have float indices
                our_add = ours_changes.get(idx, None)
                their_add = theirs_changes.get(idx, None)
                
                if our_add and their_add:
                    if our_add[1] == their_add[1]:
                        # Both added the same line
                        merged_lines.append(our_add[1])
                    else:
                        # Conflict in additions
                        has_conflict = True
                        conflict_region = [
                            "<<<<<<< OURS",
                            our_add[1],
                            "=======",
                            their_add[1],
                            ">>>>>>> THEIRS"
                        ]
                        merged_lines.extend(conflict_region)
                        conflicts.append('\n'.join(conflict_region))
                elif our_add:
                    merged_lines.append(our_add[1])
                elif their_add:
                    merged_lines.append(their_add[1])
        
        return '\n'.join(merged_lines), has_conflict, conflicts


class ChunkUpdater:
    """Manages incremental updates to documentation chunks"""
    
    def __init__(self, chunk_manager: 'ChunkManager', storage_path: str = "chunk_updates"):
        self.chunk_manager = chunk_manager
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        self.merger = ThreeWayMerger()
        self.update_history = {}
        self._load_update_history()
    
    def _load_update_history(self):
        """Load update history from storage"""
        history_file = self.storage_path / "update_history.json"
        if history_file.exists():
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    self.update_history = json.load(f)
            except:
                self.update_history = {}
    
    def _save_update_history(self):
        """Save update history to storage"""
        history_file = self.storage_path / "update_history.json"
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(self.update_history, f, indent=2)
    
    def update_chunk(self, chunk_id: str, updated_content: str) -> Dict[str, Any]:
        """
        Update a chunk with new content, handling potential conflicts
        
        Args:
            chunk_id: ID of the chunk to update
            updated_content: New content for the chunk
            
        Returns:
            Dictionary with update status and details
        """
        # Get current chunk content
        chunk = self.chunk_manager.get_chunk(chunk_id)
        if not chunk:
            return {
                'success': False,
                'error': f"Chunk {chunk_id} not found",
                'chunk_id': chunk_id
            }
        
        # Get content (this would depend on how chunk manager stores content)
        chunk_content = self.chunk_manager.get_chunk_content(chunk_id)
        original_content = chunk_content.get('documents', [{}])[0].get('content', '')
        
        # Create diff
        diff = ChunkDiff(original_content, updated_content, chunk_id)
        
        # Check for conflicts with concurrent updates
        base_content = self._get_base_content(chunk_id)
        if base_content and base_content != original_content:
            # Three-way merge needed
            merged_content, has_conflicts, conflicts = self.merger.merge(
                base_content, updated_content, original_content
            )
            
            if has_conflicts:
                # Store conflict information for manual resolution
                conflict_file = self.storage_path / f"{chunk_id}_conflict.json"
                with open(conflict_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        'chunk_id': chunk_id,
                        'timestamp': datetime.now().isoformat(),
                        'base_content': base_content,
                        'our_content': updated_content,
                        'their_content': original_content,
                        'merged_content': merged_content,
                        'conflicts': conflicts
                    }, f, indent=2)
                
                return {
                    'success': False,
                    'has_conflicts': True,
                    'conflict_file': str(conflict_file),
                    'conflicts': conflicts,
                    'chunk_id': chunk_id
                }
            
            # Use merged content
            updated_content = merged_content
        
        # Validate update
        validation_result = self._validate_update(chunk_id, original_content, updated_content)
        if not validation_result['valid']:
            return {
                'success': False,
                'error': validation_result['reason'],
                'chunk_id': chunk_id
            }
        
        # Store update information
        update_id = f"{chunk_id}_{datetime.now().isoformat().replace(':', '-')}"
        diff_file = self.storage_path / f"{update_id}.diff"
        with open(diff_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(diff.diff))
        
        # Update history
        if chunk_id not in self.update_history:
            self.update_history[chunk_id] = []
        
        self.update_history[chunk_id].append({
            'update_id': update_id,
            'timestamp': datetime.now().isoformat(),
            'diff_file': str(diff_file),
            'summary': diff.change_summary
        })
        
        self._save_update_history()
        
        # Update chunk content through chunk manager
        # This would depend on how the chunk manager implements updates
        update_result = self._update_chunk_content(chunk_id, updated_content)
        
        if update_result:
            return {
                'success': True,
                'chunk_id': chunk_id,
                'update_id': update_id,
                'changes': diff.change_summary
            }
        else:
            return {
                'success': False,
                'error': "Failed to update chunk content",
                'chunk_id': chunk_id
            }
    
    def _get_base_content(self, chunk_id: str) -> Optional[str]:
        """Get the base content for the chunk from the last update"""
        if chunk_id not in self.update_history or not self.update_history[chunk_id]:
            return None
        
        last_update = self.update_history[chunk_id][-1]
        diff_file = last_update['diff_file']
        
        # We would need to reconstruct the base content from the diff
        # This is a simplified approach
        with open(diff_file, 'r', encoding='utf-8') as f:
            diff_lines = f.readlines()
        
        # Extract original content from diff
        base_lines = []
        for line in diff_lines[3:]:  # Skip diff header
            if not line.startswith('+'):
                if line.startswith('-'):
                    base_lines.append(line[1:])
                else:
                    base_lines.append(line)
        
        return '\n'.join(base_lines)
    
    def _validate_update(self, chunk_id: str, original: str, updated: str) -> Dict[str, Any]:
        """Validate a chunk update"""
        # Check for drastic content changes
        if len(updated) < len(original) * 0.5:
            return {
                'valid': False,
                'reason': "Update removes more than 50% of original content"
            }
        
        # Check for structure preservation (simplified)
        orig_sections = [l for l in original.splitlines() if l.startswith('#')]
        updated_sections = [l for l in updated.splitlines() if l.startswith('#')]
        
        if len(orig_sections) > 0 and len(updated_sections) == 0:
            return {
                'valid': False,
                'reason': "Update removes all section headers"
            }
        
        # Could add more validation rules here
        
        return {'valid': True}
    
    def _update_chunk_content(self, chunk_id: str, content: str) -> bool:
        """Update chunk content through chunk manager"""
        # This implementation would depend on how the chunk manager works
        # For now, a placeholder that assumes the chunk manager has an update method
        try:
            # Placeholder for how you might update a chunk
            # The actual implementation depends on your chunk manager's API
            
            # Mock implementation - in reality, would use chunk manager's method
            documents = [{'content': content}]
            updated_chunk = {
                'chunk_id': chunk_id,
                'document_count': 1,
                'content': content
            }
            
            # Normally would call something like:
            # self.chunk_manager.update_chunk_content(chunk_id, documents)
            
            return True
        except Exception as e:
            print(f"Error updating chunk: {e}")
            return False
    
    def resolve_conflict(self, chunk_id: str, resolution: str) -> Dict[str, Any]:
        """Resolve a conflict by applying the resolved content"""
        conflict_file = self.storage_path / f"{chunk_id}_conflict.json"
        if not conflict_file.exists():
            return {
                'success': False,
                'error': f"No conflict file found for chunk {chunk_id}"
            }
        
        try:
            with open(conflict_file, 'r', encoding='utf-8') as f:
                conflict_data = json.load(f)
            
            # Apply resolution
            update_result = self._update_chunk_content(chunk_id, resolution)
            
            if update_result:
                # Clean up conflict file
                conflict_file.unlink()
                
                return {
                    'success': True,
                    'chunk_id': chunk_id,
                    'message': "Conflict resolved successfully"
                }
            else:
                return {
                    'success': False,
                    'error': "Failed to update chunk with resolved content",
                    'chunk_id': chunk_id
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f"Error resolving conflict: {str(e)}",
                'chunk_id': chunk_id
            }