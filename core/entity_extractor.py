import re
import ast
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass

@dataclass
class EntityMatch:
    name: str
    type: str  # 'function', 'class', 'variable', 'method'
    context: str
    confidence: float
    line_number: int
    extraction_method: str

class EntityExtractor:
    """Advanced entity recognition for code documentation"""
    
    def __init__(self):
        # Patterns for different entity types
        self.patterns = {
            'function': [
                r'def\s+(\w+)\s*\(',  # Python function definitions
                r'function\s+(\w+)\s*\(',  # JavaScript functions
                r'`(\w+)\(`',  # Markdown code references
                r'### (\w+)\(',  # Markdown function headers
            ],
            'class': [
                r'class\s+(\w+)\s*[:\(]',  # Python class definitions
                r'class\s+(\w+)\s*{',  # JavaScript/Java classes
                r'`(\w+)`.*class',  # Markdown class references
                r'## (\w+)\s*class',  # Markdown class headers
            ],
            'method': [
                r'def\s+(\w+)\s*\(.*self',  # Python methods
                r'(\w+)\s*\(.*\)\s*->',  # Method signatures
                r'`(\w+\.\w+)\(`',  # Qualified method calls
            ],
            'variable': [
                r'(\w+)\s*=\s*',  # Variable assignments
                r'`(\w+)`(?!\()',  # Variables in markdown (not functions)
            ]
        }
    
    def extract_entities(self, document: 'DocumentObject') -> List[EntityMatch]:
        entities = []
        content = document.content
        
        # Try AST-based extraction for Python code
        if self._looks_like_python_code(content):
            entities.extend(self._extract_ast_entities(content))
        
        # Regex-based extraction
        entities.extend(self._extract_regex_entities(content))
        
        # Deduplicate and score
        return self._deduplicate_entities(entities)
    
    def _looks_like_python_code(self, content: str) -> bool:
        python_indicators = ['def ', 'class ', 'import ', 'from ', 'if __name__']
        return any(indicator in content for indicator in python_indicators)
    
    def _extract_ast_entities(self, content: str) -> List[EntityMatch]:
        entities = []
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    entities.append(EntityMatch(
                        name=node.name,
                        type='function',
                        context=f"Function definition at line {node.lineno}",
                        confidence=0.95,
                        line_number=node.lineno,
                        extraction_method='ast'
                    ))
                elif isinstance(node, ast.ClassDef):
                    entities.append(EntityMatch(
                        name=node.name,
                        type='class',
                        context=f"Class definition at line {node.lineno}",
                        confidence=0.95,
                        line_number=node.lineno,
                        extraction_method='ast'
                    ))
        except:
            pass  # Fall back to regex
        
        return entities
    
    def _extract_regex_entities(self, content: str) -> List[EntityMatch]:
        entities = []
        lines = content.split('\n')
        
        for entity_type, patterns in self.patterns.items():
            for pattern in patterns:
                for line_num, line in enumerate(lines, 1):
                    matches = re.findall(pattern, line)
                    for match in matches:
                        entities.append(EntityMatch(
                            name=match,
                            type=entity_type,
                            context=line.strip(),
                            confidence=0.7,
                            line_number=line_num,
                            extraction_method='regex'
                        ))
        
        return entities
    
    def _deduplicate_entities(self, entities: List[EntityMatch]) -> List[EntityMatch]:
        seen = {}
        for entity in entities:
            key = (entity.name, entity.type)
            if key not in seen or entity.confidence > seen[key].confidence:
                seen[key] = entity
        return list(seen.values())
