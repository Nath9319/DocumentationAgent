# prompt_compression.py
import json
import hashlib
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod
from prompts.templates import DOCUMENTATION_PROMPT_TEMPLATE


@dataclass
class CompressionResult:
    compressed_prompt: str
    original_length: int
    compressed_length: int
    compression_ratio: float
    metadata: Dict[str, Any]

class BaseCompressor(ABC):
    @abstractmethod
    def compress(self, prompt: str, context: Dict[str, Any] = None) -> CompressionResult:
        pass

class SemanticCompressor(BaseCompressor):
    """Compresses prompts by removing redundant information while preserving meaning"""
    
    def __init__(self):
        self.stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
            'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during',
            'before', 'after', 'above', 'below', 'between', 'among', 'this', 'that',
            'these', 'those', 'very', 'quite', 'rather', 'really', 'extremely'
        }
        
    def compress(self, prompt: str, context: Dict[str, Any] = None) -> CompressionResult:
        original_length = len(prompt)
        
        # Step 1: Remove excessive whitespace
        compressed = re.sub(r'\s+', ' ', prompt).strip()
        
        # Step 2: Compress repetitive patterns
        compressed = self._compress_repetitive_patterns(compressed)
        
        # Step 3: Abbreviate common technical terms
        compressed = self._abbreviate_technical_terms(compressed)
        
        # Step 4: Remove redundant phrases
        compressed = self._remove_redundant_phrases(compressed)
        
        # Step 5: Optimize code examples
        compressed = self._optimize_code_examples(compressed)
        
        compressed_length = len(compressed)
        compression_ratio = (original_length - compressed_length) / original_length
        
        return CompressionResult(
            compressed_prompt=compressed,
            original_length=original_length,
            compressed_length=compressed_length,
            compression_ratio=compression_ratio,
            metadata={
                'compression_type': 'semantic',
                'techniques_applied': ['whitespace', 'patterns', 'abbreviation', 'redundancy', 'code_optimization']
            }
        )
    
    def _compress_repetitive_patterns(self, text: str) -> str:
        """Compress repetitive patterns in the text"""
        # Find repeated phrases and compress them
        patterns = [
            (r'(\bgenerate documentation for\b.*?\bgenerate documentation for\b)', 
             r'generate documentation for (multiple items)'),
            (r'(\bthe following code\b.*?\bthe following code\b)', 
             r'the code blocks'),
            (r'(\bplease create\b.*?\bplease create\b)', 
             r'create (multiple items)'),
        ]
        
        for pattern, replacement in patterns:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        return text
    
    def _abbreviate_technical_terms(self, text: str) -> str:
        """Abbreviate common technical terms"""
        abbreviations = {
            'documentation': 'docs',
            'function': 'func',
            'parameter': 'param',
            'variable': 'var',
            'configuration': 'config',
            'application': 'app',
            'component': 'comp',
            'interface': 'iface',
            'implementation': 'impl',
            'repository': 'repo',
            'directory': 'dir',
            'environment': 'env'
        }
        
        for full_term, abbrev in abbreviations.items():
            # Only abbreviate if it appears multiple times
            if text.lower().count(full_term.lower()) > 2:
                text = re.sub(rf'\b{full_term}\b', abbrev, text, flags=re.IGNORECASE)
        
        return text
    
    def _remove_redundant_phrases(self, text: str) -> str:
        """Remove redundant phrases that don't add value"""
        redundant_phrases = [
            r'\bplease note that\b',
            r'\bit is important to\b',
            r'\bwe need to\b',
            r'\byou should\b',
            r'\bmake sure to\b',
            r'\bin order to\b',
            r'\bfor the purpose of\b',
            r'\bdue to the fact that\b'
        ]
        
        for phrase in redundant_phrases:
            text = re.sub(phrase, '', text, flags=re.IGNORECASE)
        
        return text
    
    def _optimize_code_examples(self, text: str) -> str:
        """Optimize code examples by removing unnecessary comments and whitespace"""
        # Find code blocks (assuming they're between triple backticks)
        code_pattern = r'```(\w+)?\n(.*?)\n```'
        
        def compress_code_block(match):
            language = match.group(1) or ''
            code = match.group(2)
            
            # Remove excessive comments
            lines = code.split('\n')
            compressed_lines = []
            
            for line in lines:
                # Keep important comments, remove obvious ones
                if line.strip().startswith('#'):
                    if any(keyword in line.lower() for keyword in ['todo', 'fixme', 'important', 'note']):
                        compressed_lines.append(line)
                else:
                    compressed_lines.append(line)
            
            compressed_code = '\n'.join(compressed_lines)
            return f'```{language}\n{compressed_code}\n```'
        
        return re.sub(code_pattern, compress_code_block, text, flags=re.DOTALL)

class StructuralCompressor(BaseCompressor):
    """Compresses prompts by restructuring content hierarchically"""
    
    def compress(self, prompt: str, context: Dict[str, Any] = None) -> CompressionResult:
        original_length = len(prompt)
        
        # Parse the prompt into sections
        sections = self._parse_sections(prompt)
        
        # Compress each section
        compressed_sections = []
        for section in sections:
            compressed_section = self._compress_section(section)
            compressed_sections.append(compressed_section)
        
        # Reconstruct the prompt
        compressed = self._reconstruct_prompt(compressed_sections)
        
        compressed_length = len(compressed)
        compression_ratio = (original_length - compressed_length) / original_length
        
        return CompressionResult(
            compressed_prompt=compressed,
            original_length=original_length,
            compressed_length=compressed_length,
            compression_ratio=compression_ratio,
            metadata={
                'compression_type': 'structural',
                'sections_count': len(sections),
                'techniques_applied': ['section_parsing', 'hierarchical_restructuring']
            }
        )
    
    def _parse_sections(self, prompt: str) -> List[Dict[str, Any]]:
        """Parse prompt into logical sections"""
        sections = []
        current_section = {"type": "text", "content": "", "priority": 1}
        
        lines = prompt.split('\n')
        for line in lines:
            if line.startswith('##') or line.startswith('###'):
                # New section
                if current_section["content"]:
                    sections.append(current_section)
                current_section = {
                    "type": "header",
                    "content": line,
                    "priority": self._get_section_priority(line)
                }
            elif line.startswith('```'):
                # Code section
                if current_section["type"] != "code":
                    if current_section["content"]:
                        sections.append(current_section)
                    current_section = {"type": "code", "content": line, "priority": 3}
                else:
                    current_section["content"] += '\n' + line
                    sections.append(current_section)
                    current_section = {"type": "text", "content": "", "priority": 1}
            else:
                current_section["content"] += '\n' + line if current_section["content"] else line
        
        if current_section["content"]:
            sections.append(current_section)
        
        return sections
    
    def _get_section_priority(self, header: str) -> int:
        """Assign priority to sections based on content"""
        high_priority_keywords = ['example', 'code', 'implementation', 'api', 'function']
        medium_priority_keywords = ['usage', 'configuration', 'setup']
        
        header_lower = header.lower()
        if any(keyword in header_lower for keyword in high_priority_keywords):
            return 3
        elif any(keyword in header_lower for keyword in medium_priority_keywords):
            return 2
        return 1
    
    def _compress_section(self, section: Dict[str, Any]) -> Dict[str, Any]:
        """Compress individual section based on its type and priority"""
        if section["priority"] == 1:  # Low priority - heavy compression
            content = section["content"]
            # Remove examples, verbose explanations
            content = re.sub(r'for example.*?\.', '', content, flags=re.IGNORECASE)
            content = re.sub(r'in other words.*?\.', '', content, flags=re.IGNORECASE)
            section["content"] = content
        
        return section
    
    def _reconstruct_prompt(self, sections: List[Dict[str, Any]]) -> str:
        """Reconstruct prompt from compressed sections"""
        # Sort by priority (higher priority first)
        sections.sort(key=lambda x: x["priority"], reverse=True)
        
        return '\n'.join(section["content"] for section in sections if section["content"].strip())

class ContextAwareCompressor(BaseCompressor):
    """Compresses prompts based on context and previous interactions"""
    
    def __init__(self):
        self.context_cache = {}
    
    def compress(self, prompt: str, context: Dict[str, Any] = None) -> CompressionResult:
        original_length = len(prompt)
        
        if not context:
            context = {}
        
        # Extract reusable context
        context_hash = self._get_context_hash(context)
        
        # Check if we have similar context cached
        if context_hash in self.context_cache:
            # Use reference to cached context instead of repeating it
            compressed = self._use_context_reference(prompt, context_hash)
        else:
            # First time - cache the context
            compressed = self._extract_and_cache_context(prompt, context, context_hash)
        
        compressed_length = len(compressed)
        compression_ratio = (original_length - compressed_length) / original_length
        
        return CompressionResult(
            compressed_prompt=compressed,
            original_length=original_length,
            compressed_length=compressed_length,
            compression_ratio=compression_ratio,
            metadata={
                'compression_type': 'context_aware',
                'context_hash': context_hash,
                'cached_context': context_hash in self.context_cache
            }
        )
    
    def _get_context_hash(self, context: Dict[str, Any]) -> str:
        """Generate hash for context to identify similar contexts"""
        context_str = json.dumps(context, sort_keys=True)
        return hashlib.md5(context_str.encode()).hexdigest()[:8]
    
    def _use_context_reference(self, prompt: str, context_hash: str) -> str:
        """Replace repeated context with reference"""
        cached_context = self.context_cache[context_hash]
        
        # Replace repeated context with reference
        for key, value in cached_context.items():
            if value in prompt:
                prompt = prompt.replace(value, f"[REF:{context_hash}:{key}]")
        
        return prompt
    
    def _extract_and_cache_context(self, prompt: str, context: Dict[str, Any], context_hash: str) -> str:
        """Extract reusable context and cache it"""
        # Find repeated patterns that can be cached
        patterns = {
            'project_structure': r'(project structure:.*?(?=\n\n|\n#|\n-|\Z))',
            'code_examples': r'(```.*?```)',
            'api_definitions': r'(def \w+.*?(?=\ndef|\Z))'
        }
        
        cached_context = {}
        compressed_prompt = prompt
        
        for key, pattern in patterns.items():
            matches = re.findall(pattern, prompt, re.DOTALL)
            if matches:
                # Cache the first occurrence
                cached_context[key] = matches[0]
                # Replace subsequent occurrences with references
                for i, match in enumerate(matches):
                    if i > 0:  # Keep first occurrence
                        compressed_prompt = compressed_prompt.replace(match, f"[REF:{context_hash}:{key}]")
        
        if cached_context:
            self.context_cache[context_hash] = cached_context
        
        return compressed_prompt

class HybridCompressor(BaseCompressor):
    """Combines multiple compression techniques for optimal results"""
    
    def __init__(self):
        self.compressors = [
            SemanticCompressor(),
            StructuralCompressor(),
            ContextAwareCompressor()
        ]
    
    def compress(self, prompt: str, context: Dict[str, Any] = None) -> CompressionResult:
        original_length = len(prompt)
        current_prompt = prompt
        applied_techniques = []
        
        # Apply each compressor in sequence
        for compressor in self.compressors:
            result = compressor.compress(current_prompt, context)
            if result.compression_ratio > 0.1:  # Only apply if significant compression
                current_prompt = result.compressed_prompt
                applied_techniques.append(result.metadata.get('compression_type', 'unknown'))
        
        compressed_length = len(current_prompt)
        compression_ratio = (original_length - compressed_length) / original_length
        
        return CompressionResult(
            compressed_prompt=current_prompt,
            original_length=original_length,
            compressed_length=compressed_length,
            compression_ratio=compression_ratio,
            metadata={
                'compression_type': 'hybrid',
                'techniques_applied': applied_techniques,
                'compression_stages': len(applied_techniques)
            }
        )

class DocumentationPromptCompressor:
    """Main class for compressing documentation generation prompts"""
    
    def __init__(self, compression_strategy: str = 'hybrid'):
        self.compressor = self._get_compressor(compression_strategy)
        self.compression_stats = []
    
    def _get_compressor(self, strategy: str) -> BaseCompressor:
        compressors = {
            'semantic': SemanticCompressor(),
            'structural': StructuralCompressor(),
            'context_aware': ContextAwareCompressor(),
            'hybrid': HybridCompressor()
        }
        return compressors.get(strategy, HybridCompressor())
    
    def compress_documentation_prompt(self, 
                                    component_info: Dict[str, Any],
                                    template: str,
                                    context: Dict[str, Any] = None) -> str:
        """Compress a documentation generation prompt"""
        
        # Build the full prompt
        full_prompt = self._build_full_prompt(component_info, template, context)
        
        # Compress it
        result = self.compressor.compress(full_prompt, context)
        
        # Store stats
        self.compression_stats.append({
            'timestamp': json.dumps({}),  # Current timestamp would go here
            'original_length': result.original_length,
            'compressed_length': result.compressed_length,
            'compression_ratio': result.compression_ratio,
            'metadata': result.metadata
        })
        
        return result.compressed_prompt
    
    def _build_full_prompt(self, 
                          component_info: Dict[str, Any],
                          template: str,
                          context: Dict[str, Any] = None) -> str:
        """Build the full prompt before compression"""
        
        prompt_parts = [
            f"Component: {component_info.get('name', 'Unknown')}",
            f"Type: {component_info.get('type', 'Unknown')}",
            f"Dependencies: {', '.join(component_info.get('dependencies', []))}",
            f"Code:\n{component_info.get('code', '')}",
            f"Template:\n{template}"
        ]
        
        if context:
            prompt_parts.append(f"Context:\n{json.dumps(context, indent=2)}")
        
        return '\n\n'.join(prompt_parts)
    
    def get_compression_stats(self) -> Dict[str, Any]:
        """Get compression statistics"""
        if not self.compression_stats:
            return {}
        
        avg_ratio = sum(stat['compression_ratio'] for stat in self.compression_stats) / len(self.compression_stats)
        total_saved = sum(stat['original_length'] - stat['compressed_length'] for stat in self.compression_stats)
        
        return {
            'total_compressions': len(self.compression_stats),
            'average_compression_ratio': avg_ratio,
            'total_characters_saved': total_saved,
            'latest_stats': self.compression_stats[-5:]  # Last 5 compressions
        }

# Usage example
if __name__ == "__main__":
    # Example usage
    compressor = DocumentationPromptCompressor('hybrid')
    
    component_info = {
    'name': 'ExampleNode',
    'type': 'function',
    'dependencies': [],
    'code': ''
}

    template = DOCUMENTATION_PROMPT_TEMPLATE

    
    context = {}
        
    
    
    compressed_prompt = compressor.compress_documentation_prompt(
        component_info, template, context
    )
    
    print("Compressed Prompt:")
    print(compressed_prompt)
    print("\nCompression Stats:")
    print(json.dumps(compressor.get_compression_stats(), indent=2))