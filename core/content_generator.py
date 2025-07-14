# core/content_generator.py

import os
import json
import time
from typing import Dict, Any, List, Optional, Union, Callable
import importlib.util

class PromptManager:
    """Manages prompt templates with version control and optimization"""
    
    def __init__(self, templates_dir: str = "prompts/templates"):
        self.templates_dir = templates_dir
        self.templates_cache = {}
        self.template_stats = {}  # Track usage and performance
        self._load_templates()
    
    def _load_templates(self):
        """Load templates from files and modules"""
        # Check if templates.py exists as a module
        if importlib.util.find_spec("prompts.templates"):
            from prompts.templates import *
            # Get all uppercase variables from the module
            import prompts.templates as templates_module
            for name in dir(templates_module):
                if name.isupper() and "_TEMPLATE" in name:
                    self.templates_cache[name] = getattr(templates_module, name)
        
        # Load any additional templates from JSON files
        if os.path.exists(self.templates_dir):
            for file in os.listdir(self.templates_dir):
                if file.endswith('.json'):
                    with open(os.path.join(self.templates_dir, file), 'r') as f:
                        templates = json.load(f)
                        self.templates_cache.update(templates)
    
    def get_template(self, template_id: str, version: str = "latest") -> str:
        """Get a specific prompt template"""
        if template_id in self.templates_cache:
            # Track usage
            if template_id not in self.template_stats:
                self.template_stats[template_id] = {"uses": 0, "success_rate": 0, "avg_time": 0}
            self.template_stats[template_id]["uses"] += 1
            return self.templates_cache[template_id]
        raise KeyError(f"Template '{template_id}' not found")
    
    def optimize_template(self, template_id: str, performance_data: Dict[str, Any]):
        """Update template stats based on performance data"""
        if template_id in self.template_stats:
            stats = self.template_stats[template_id]
            # Update success rate and average time
            new_success = performance_data.get("success", False)
            old_success_count = stats["success_rate"] * stats["uses"]
            stats["success_rate"] = (old_success_count + (1 if new_success else 0)) / (stats["uses"])
            
            # Update average time
            if "generation_time" in performance_data:
                old_total_time = stats["avg_time"] * (stats["uses"] - 1)
                new_time = performance_data["generation_time"]
                stats["avg_time"] = (old_total_time + new_time) / stats["uses"]


class LLMProvider:
    """Abstraction over different LLM providers"""
    
    def __init__(self, provider_type: str = "azure", config: Dict[str, Any] = None):
        self.provider_type = provider_type
        self.config = config or {}
        self.client = self._initialize_client()
        self.rate_limit_retries = 3
        self.backoff_factor = 2
    
    def _initialize_client(self):
        """Initialize the appropriate LLM client"""
        if self.provider_type == "azure":
            from langchain_openai import AzureChatOpenAI
            return AzureChatOpenAI(
                deployment_name=self.config.get("deployment_name", os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")),
                temperature=self.config.get("temperature", 0.2),
                max_tokens=self.config.get("max_tokens", 2048)
            )
        # Add other providers as needed
        raise ValueError(f"Unsupported provider: {self.provider_type}")
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate content with retry logic"""
        attempt = 0
        while attempt < self.rate_limit_retries:
            try:
                start_time = time.time()
                response = self.client.invoke(prompt)
                generation_time = time.time() - start_time
                return {
                    "content": response.content,
                    "generation_time": generation_time,
                    "success": True
                }
            except Exception as e:
                attempt += 1
                if "rate limit" in str(e).lower() and attempt < self.rate_limit_retries:
                    wait_time = self.backoff_factor ** attempt
                    time.sleep(wait_time)
                else:
                    return {
                        "content": "",
                        "error": str(e),
                        "success": False
                    }


class ContentGenerator:
    """LLM-powered content generation with quality control"""
    
    def __init__(self, 
                 style_guide: Dict[str, Any] = None,
                 llm_config: Dict[str, Any] = None):
        self.prompt_manager = PromptManager()
        self.llm_provider = LLMProvider(config=llm_config)
        self.style_guide = style_guide or {
            "tone": "professional",
            "max_paragraph_length": 5,  # sentences
            "heading_style": "atx",  # # Heading vs. Heading\n=======
            "code_style": "fenced"   # ```code``` vs. indented
        }
        self.validation_rules = []
    
    def generate_content(self, 
                        template_id: str, 
                        variables: Dict[str, Any],
                        validation_fn: Callable = None,
                        max_retries: int = 2) -> Dict[str, Any]:
        """Generate content using a template and variables"""
        template = self.prompt_manager.get_template(template_id)
        
        # Format template with variables
        try:
            formatted_prompt = template.format(**variables)
        except KeyError as e:
            return {
                "success": False,
                "error": f"Missing template variable: {e}",
                "content": None
            }
        
        # Generate content with retries
        for attempt in range(max_retries + 1):
            result = self.llm_provider.generate(formatted_prompt)
            
            if not result["success"]:
                if attempt < max_retries:
                    continue
                return result
            
            content = result["content"]
            
            # Validate content
            if validation_fn and not validation_fn(content):
                if attempt < max_retries:
                    # Try again with more specific instructions
                    formatted_prompt += "\n\nYour previous response did not meet the requirements. Please try again and ensure you follow all guidelines."
                    continue
                return {
                    "success": False,
                    "error": "Failed validation after retries",
                    "content": content
                }
            
            # Apply style guide
            styled_content = self._apply_style_guide(content)
            
            # Update template statistics
            self.prompt_manager.optimize_template(template_id, {
                "success": True,
                "generation_time": result["generation_time"],
                "attempts": attempt + 1
            })
            
            return {
                "success": True,
                "content": styled_content,
                "generation_time": result["generation_time"],
                "attempts": attempt + 1
            }
    
    def _apply_style_guide(self, content: str) -> str:
        """Apply style guide rules to content"""
        # This would contain logic to enforce style guide rules
        # For now, just a simple implementation
        
        if self.style_guide["heading_style"] == "atx":
            # Convert setext headings (=== or ---) to ATX (# or ##)
            lines = content.splitlines()
            for i in range(1, len(lines)):
                if lines[i].strip() == "=" * len(lines[i].strip()):
                    lines[i-1] = f"# {lines[i-1]}"
                    lines[i] = ""
                elif lines[i].strip() == "-" * len(lines[i].strip()):
                    lines[i-1] = f"## {lines[i-1]}"
                    lines[i] = ""
            content = "\n".join(lines)
        
        return content
    
    def add_validation_rule(self, rule_fn: Callable):
        """Add a validation rule function"""
        self.validation_rules.append(rule_fn)
        
    def validate_content(self, content: str) -> bool:
        """Validate content against all rules"""
        return all(rule(content) for rule in self.validation_rules)