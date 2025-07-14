import os
import json
import hashlib
import subprocess
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import PromptTemplate

class CompressionLevel(Enum):
    LOSSLESS = "lossless"
    CONSERVATIVE = "conservative"
    BALANCED = "balanced"
    AGGRESSIVE = "aggressive"

@dataclass
class CompressionResult:
    original_size: int
    compressed_size: int
    compression_ratio: float
    quality_score: float
    method: str
    compressed_content: str
    metadata: Dict[str, Any]

class DocumentationCompressor:
    """Compression engine using external toolkit + Azure OpenAI"""
    
    def __init__(self):
        self.llm = AzureChatOpenAI(
            deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            temperature=0.1,
            max_tokens=2048
        )
        
        # Compression templates for different levels
        self.compression_prompts = {
            CompressionLevel.LOSSLESS: """
            Compress the following technical documentation while preserving ALL technical details, function signatures, and parameter descriptions:
            
            {content}
            
            Rules:
            - Keep all function names, parameters, and return types
            - Preserve code examples and technical specifications
            - Only remove redundant explanations and verbose descriptions
            - Maintain structural integrity
            """,
            
            CompressionLevel.CONSERVATIVE: """
            Compress this documentation by removing redundancy while keeping essential technical information:
            
            {content}
            
            Rules:
            - Preserve function signatures and key parameters
            - Keep critical technical details and warnings
            - Remove verbose examples but keep one representative example
            - Condense explanations while maintaining clarity
            """,
            
            CompressionLevel.BALANCED: """
            Create a balanced compression of this documentation:
            
            {content}
            
            Rules:
            - Keep essential function information and primary use cases
            - Preserve critical technical details and error conditions
            - Remove verbose descriptions and redundant examples
            - Focus on practical usage information
            """,
            
            CompressionLevel.AGGRESSIVE: """
            Create a highly compressed summary focusing only on essential information:
            
            {content}
            
            Rules:
            - Keep only function signatures and essential parameters
            - Preserve critical warnings and limitations
            - Remove all examples except the most basic one
            - Use concise, technical language
            """
        }
    
    def compress_documentation(self, content: str, level: CompressionLevel, 
                             section_type: str = "general") -> CompressionResult:
        """Main compression method"""
        original_size = len(content.encode('utf-8'))
        
        # Apply domain-specific rules first
        preprocessed = self._apply_domain_rules(content, section_type)
        
        # Apply LLM compression
        compressed = self._llm_compress(preprocessed, level)
        
        # Post-process and validate
        final_compressed = self._post_process(compressed, level)
        compressed_size = len(final_compressed.encode('utf-8'))
        
        # Calculate quality metrics
        quality_score = self._calculate_quality(content, final_compressed, level)
        
        return CompressionResult(
            original_size=original_size,
            compressed_size=compressed_size,
            compression_ratio=compressed_size / original_size,
            quality_score=quality_score,
            method=f"llm_{level.value}",
            compressed_content=final_compressed,
            metadata={
                'section_type': section_type,
                'level': level.value,
                'preprocessing_applied': True
            }
        )
    
    def _apply_domain_rules(self, content: str, section_type: str) -> str:
        """Apply domain-specific compression rules"""
        lines = content.split('\n')
        processed_lines = []
        
        for line in lines:
            # Keep function signatures and class definitions
            if any(pattern in line for pattern in ['def ', 'class ', '###', '####']):
                processed_lines.append(line)
            # Compress repetitive parameter descriptions
            elif line.strip().startswith('- ') and 'parameter' in line.lower():
                processed_lines.append(self._compress_parameter_line(line))
            # Keep critical sections
            elif any(keyword in line.lower() for keyword in ['warning', 'error', 'critical', 'required']):
                processed_lines.append(line)
            else:
                processed_lines.append(line)
        
        return '\n'.join(processed_lines)
    
    def _compress_parameter_line(self, line: str) -> str:
        """Compress parameter descriptions"""
        # Extract parameter name and type, compress description
        import re
        param_match = re.match(r'- `(\w+)` \(`([^`]+)`\): (.+)', line)
        if param_match:
            name, type_info, description = param_match.groups()
            # Keep first sentence of description
            short_desc = description.split('.')[0] + '.'
            return f"- `{name}` (`{type_info}`): {short_desc}"
        return line
    
    def _llm_compress(self, content: str, level: CompressionLevel) -> str:
        """Use LLM for semantic compression"""
        prompt_template = PromptTemplate.from_template(self.compression_prompts[level])
        
        try:
            response = self.llm.invoke(prompt_template.format(content=content))
            return response.content
        except Exception as e:
            print(f"LLM compression failed: {e}")
            return content  # Fallback to original
    
    def _post_process(self, compressed: str, level: CompressionLevel) -> str:
        """Post-process compressed content"""
        lines = compressed.split('\n')
        
        # Remove excessive empty lines
        processed_lines = []
        prev_empty = False
        
        for line in lines:
            if line.strip():
                processed_lines.append(line)
                prev_empty = False
            elif not prev_empty:
                processed_lines.append(line)
                prev_empty = True
        
        return '\n'.join(processed_lines)
    
    def _calculate_quality(self, original: str, compressed: str, level: CompressionLevel) -> float:
        """Calculate compression quality score"""
        # Simple heuristic: check if key technical terms are preserved
        key_terms = ['def ', 'class ', 'parameter', 'return', 'error', 'warning']
        
        orig_terms = sum(1 for term in key_terms if term in original.lower())
        comp_terms = sum(1 for term in key_terms if term in compressed.lower())
        
        preservation_score = comp_terms / orig_terms if orig_terms > 0 else 1.0
        
        # Adjust based on compression level expectations
        level_adjustments = {
            CompressionLevel.LOSSLESS: 0.9,
            CompressionLevel.CONSERVATIVE: 0.8,
            CompressionLevel.BALANCED: 0.7,
            CompressionLevel.AGGRESSIVE: 0.6
        }
        
        return min(1.0, preservation_score * level_adjustments[level])