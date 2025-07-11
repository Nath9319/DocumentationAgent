import os
import json
import hashlib
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime

@dataclass
class DocumentObject:
    """Unified document representation"""
    content: str
    metadata: Dict[str, Any]
    entities: List[Dict[str, Any]]
    sections: List[Dict[str, Any]]
    fingerprint: str

class BaseDocumentParser(ABC):
    """Base class for format-specific parsers"""
    
    @abstractmethod
    def can_parse(self, file_path: str) -> bool:
        pass
    
    @abstractmethod
    def parse(self, file_path: str) -> DocumentObject:
        pass

class MarkdownParser(BaseDocumentParser):
    """Parser for markdown documentation files"""
    
    def can_parse(self, file_path: str) -> bool:
        return file_path.endswith('.md')
    
    def parse(self, file_path: str) -> DocumentObject:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        metadata = {
            'format': 'markdown',
            'file_path': file_path,
            'file_size': os.path.getsize(file_path),
            'modified_time': datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
        }
        
        # Extract title from first heading
        lines = content.split('\n')
        title = next((line.lstrip('# ') for line in lines if line.startswith('#')), 
                    Path(file_path).stem)
        metadata['title'] = title
        
        return DocumentObject(
            content=content,
            metadata=metadata,
            entities=[],  # Will be populated by EntityExtractor
            sections=[],  # Will be populated by DocumentPreprocessor
            fingerprint=hashlib.md5(content.encode()).hexdigest()
        )

class JSONParser(BaseDocumentParser):
    """Parser for JSON documentation data"""
    
    def can_parse(self, file_path: str) -> bool:
        return file_path.endswith('.json')
    
    def parse(self, file_path: str) -> DocumentObject:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        content = json.dumps(data, indent=2)
        metadata = {
            'format': 'json',
            'file_path': file_path,
            'keys': list(data.keys()) if isinstance(data, dict) else [],
            'file_size': os.path.getsize(file_path)
        }
        
        return DocumentObject(
            content=content,
            metadata=metadata,
            entities=[],
            sections=[],
            fingerprint=hashlib.md5(content.encode()).hexdigest()
        )

class DocumentParserManager:
    """Main parser manager with plugin architecture"""
    
    def __init__(self):
        self.parsers = [MarkdownParser(), JSONParser()]
    
    def register_parser(self, parser: BaseDocumentParser):
        self.parsers.append(parser)
    
    def parse_document(self, file_path: str) -> Optional[DocumentObject]:
        for parser in self.parsers:
            if parser.can_parse(file_path):
                return parser.parse(file_path)
        return None