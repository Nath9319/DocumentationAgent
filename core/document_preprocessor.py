import re
import hashlib
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class DocumentSection:
    title: str
    content: str
    level: int
    start_line: int
    end_line: int

class DocumentPreprocessor:
    """Normalize and prepare documents for analysis"""
    
    def __init__(self):
        self.normalization_rules = {
            'whitespace': r'\s+',
            'code_blocks': r'```[\s\S]*?```',
            'inline_code': r'`[^`]+`',
            'markdown_links': r'\[([^\]]+)\]\([^)]+\)',
        }
    
    def preprocess(self, document: 'DocumentObject') -> 'DocumentObject':
        """Main preprocessing pipeline"""
        # Normalize text
        normalized_content = self._normalize_text(document.content)
        
        # Extract sections
        sections = self._extract_sections(normalized_content)
        
        # Generate similarity fingerprint
        fingerprint = self._generate_fingerprint(normalized_content)
        
        # Update document
        document.content = normalized_content
        document.sections = sections
        document.fingerprint = fingerprint
        
        return document
    
    def _normalize_text(self, content: str) -> str:
        """Normalize whitespace and encoding"""
        # Normalize line endings
        content = content.replace('\r\n', '\n').replace('\r', '\n')
        
        # Normalize whitespace (but preserve code blocks)
        lines = content.split('\n')
        normalized_lines = []
        
        in_code_block = False
        for line in lines:
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                normalized_lines.append(line)
            elif in_code_block:
                normalized_lines.append(line)  # Preserve code formatting
            else:
                # Normalize whitespace in regular text
                normalized_lines.append(re.sub(r'\s+', ' ', line.strip()))
        
        return '\n'.join(normalized_lines)
    
    def _extract_sections(self, content: str) -> List[DocumentSection]:
        """Extract document sections based on headings"""
        sections = []
        lines = content.split('\n')
        current_section = None
        
        for i, line in enumerate(lines):
            # Markdown heading detection
            heading_match = re.match(r'^(#{1,6})\s+(.+)', line)
            if heading_match:
                # Save previous section
                if current_section:
                    current_section['end_line'] = i - 1
                    sections.append(DocumentSection(**current_section))
                
                # Start new section
                level = len(heading_match.group(1))
                title = heading_match.group(2)
                current_section = {
                    'title': title,
                    'content': '',
                    'level': level,
                    'start_line': i,
                    'end_line': i
                }
            elif current_section:
                current_section['content'] += line + '\n'
        
        # Add final section
        if current_section:
            current_section['end_line'] = len(lines) - 1
            sections.append(DocumentSection(**current_section))
        
        return sections
    
    def _generate_fingerprint(self, content: str) -> str:
        """Generate similarity fingerprint for duplicate detection"""
        # Remove code blocks and inline code for similarity comparison
        clean_content = re.sub(self.normalization_rules['code_blocks'], '', content)
        clean_content = re.sub(self.normalization_rules['inline_code'], '', clean_content)
        clean_content = re.sub(self.normalization_rules['markdown_links'], r'\1', clean_content)
        
        # Convert to lowercase and remove extra whitespace
        clean_content = re.sub(r'\s+', ' ', clean_content.lower().strip())
        
        return hashlib.sha256(clean_content.encode()).hexdigest()
