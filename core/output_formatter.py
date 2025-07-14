# core/output_formatter.py

import os
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import json
import markdown
from datetime import datetime
import re
import networkx as nx
from jinja2 import Environment, FileSystemLoader

class CrossReferenceResolver:
    """Resolves cross-references in documentation"""
    
    def __init__(self, documentation_graph: nx.MultiDiGraph):
        self.graph = documentation_graph
        self.ref_map = {}
        self._build_reference_map()
    
    def _build_reference_map(self):
        """Build a map of reference keys to node names"""
        for node in self.graph.nodes():
            # Create various forms of reference for this node
            node_key = node.lower().replace('.', '_')
            self.ref_map[node_key] = node
            
            # Add shortened forms for methods
            if '.' in node:
                class_name, method_name = node.split('.', 1)
                method_key = method_name.lower()
                
                # Only add if not ambiguous
                if method_key not in self.ref_map:
                    self.ref_map[method_key] = node
                else:
                    # Mark as ambiguous
                    self.ref_map[method_key] = None
    
    def resolve_references(self, content: str) -> str:
        """Resolve cross-references in content"""
        # Find references in the format [[ref]]
        def replace_ref(match):
            ref = match.group(1).lower().replace('.', '_')
            if ref in self.ref_map and self.ref_map[ref]:
                node = self.ref_map[ref]
                return f"[`{node}`](#{node.lower().replace('.', '-')})"
            return match.group(0)
        
        return re.sub(r'\[\[([^\]]+)\]\]', replace_ref, content)
    
    def extract_references(self, content: str) -> List[str]:
        """Extract all cross-references from content"""
        refs = re.findall(r'\[\[([^\]]+)\]\]', content)
        return refs


class TableOfContentsGenerator:
    """Generates table of contents from documentation"""
    
    @staticmethod
    def generate_toc(content: str, max_depth: int = 3) -> str:
        """Generate TOC from markdown headings"""
        lines = content.splitlines()
        toc_lines = []
        
        for line in lines:
            if line.startswith('#'):
                # Count heading level
                level = 0
                for char in line:
                    if char == '#':
                        level += 1
                    else:
                        break
                
                if level <= max_depth:
                    # Extract heading text
                    heading = line[level:].strip()
                    
                    # Create TOC entry with proper indentation
                    indent = '  ' * (level - 1)
                    anchor = heading.lower().replace(' ', '-').replace('.', '-')
                    anchor = re.sub(r'[^\w\-]', '', anchor)
                    
                    toc_lines.append(f"{indent}- [{heading}](#{anchor})")
        
        return '\n'.join(toc_lines)


class TemplateManager:
    """Manages documentation templates"""
    
    def __init__(self, templates_dir: str = "templates"):
        self.templates_dir = Path(templates_dir)
        self.env = Environment(loader=FileSystemLoader(str(self.templates_dir)))
        self._ensure_default_templates()
    
    def _ensure_default_templates(self):
        """Ensure default templates exist"""
        self.templates_dir.mkdir(exist_ok=True)
        
        # Create default templates if they don't exist
        default_templates = {
            "markdown.md": """# {{title}}

{{toc}}

{% for section in sections %}
## {{section.title}}

{{section.content}}

{% endfor %}

---
Generated on {{timestamp}}
""",
            "html.html": """<!DOCTYPE html>
<html>
<head>
    <title>{{title}}</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: system-ui, -apple-system, sans-serif; line-height: 1.5; margin: 0; padding: 20px; }
        .container { max-width: 900px; margin: 0 auto; }
        pre { background: #f5f5f5; padding: 10px; border-radius: 5px; overflow-x: auto; }
        code { font-family: 'Courier New', monospace; }
        h1, h2, h3 { margin-top: 1.5em; }
        .toc { background: #f9f9f9; padding: 15px; border-radius: 5px; }
        a { color: #0366d6; }
    </style>
</head>
<body>
    <div class="container">
        <h1>{{title}}</h1>
        
        <div class="toc">
            <h2>Table of Contents</h2>
            {{toc|safe}}
        </div>
        
        {% for section in sections %}
            <h2 id="{{section.id}}">{{section.title}}</h2>
            {{section.content|safe}}
        {% endfor %}
        
        <hr>
        <footer>
            <p>Generated on {{timestamp}}</p>
        </footer>
    </div>
</body>
</html>
"""
        }
        
        for name, content in default_templates.items():
            template_path = self.templates_dir / name
            if not template_path.exists():
                with open(template_path, 'w', encoding='utf-8') as f:
                    f.write(content)
    
    def get_template(self, template_name: str):
        """Get a template by name"""
        return self.env.get_template(template_name)
    
    def render_template(self, template_name: str, data: Dict[str, Any]) -> str:
        """Render a template with data"""
        template = self.get_template(template_name)
        return template.render(**data)


# core/output_formatter.py (continued)

class OutputFormatter:
    """Multi-format documentation output system"""
    
    def __init__(self, 
                 documentation_graph: Optional[nx.MultiDiGraph] = None,
                 templates_dir: str = "templates",
                 output_dir: str = "output/documentation"):
        self.documentation_graph = documentation_graph
        self.template_manager = TemplateManager(templates_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        if documentation_graph:
            self.reference_resolver = CrossReferenceResolver(documentation_graph)
        else:
            self.reference_resolver = None
        
        self.toc_generator = TableOfContentsGenerator()
        self.style_config = self._load_style_config()
    
    def _load_style_config(self) -> Dict[str, Any]:
        """Load style configuration"""
        config_path = Path("config/style_config.json")
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        
        # Default style config
        return {
            "markdown": {
                "heading_style": "atx",  # atx = # Heading, setext = Heading\n=======
                "code_block_style": "fenced",  # fenced = ```code```, indented = 4 spaces
                "emphasis_style": "asterisk",  # asterisk = *italic*, underscore = _italic_
                "link_style": "inline"  # inline = [text](url), reference = [text][ref]
            },
            "html": {
                "theme": "light",
                "code_highlighting": True,
                "include_css": True,
                "include_toc": True,
                "responsive": True
            },
            "pdf": {
                "page_size": "A4",
                "include_toc": True,
                "include_cover": True,
                "include_footer": True
            }
        }
    
    def format_document(self, 
                       content: Dict[str, Any],
                       output_format: str = "markdown",
                       filename: str = None) -> str:
        """
        Format document content in the specified format
        
        Args:
            content: Document content dictionary
            output_format: Target format (markdown, html, pdf)
            filename: Output filename (if None, one will be generated)
            
        Returns:
            Path to the generated file
        """
        # Process content
        processed_content = self._preprocess_content(content)
        
        # Generate output
        if output_format == "markdown":
            return self._generate_markdown(processed_content, filename)
        elif output_format == "html":
            return self._generate_html(processed_content, filename)
        elif output_format == "pdf":
            return self._generate_pdf(processed_content, filename)
        else:
            raise ValueError(f"Unsupported output format: {output_format}")
    
    def _preprocess_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Preprocess content before formatting"""
        processed = content.copy()
        
        # Resolve cross-references
        if self.reference_resolver and 'sections' in processed:
            for section in processed['sections']:
                if 'content' in section:
                    section['content'] = self.reference_resolver.resolve_references(section['content'])
        
        # Generate section IDs
        if 'sections' in processed:
            for section in processed['sections']:
                if 'title' in section:
                    section['id'] = re.sub(r'[^\w\-]', '', section['title'].lower().replace(' ', '-'))
        
        # Add timestamp
        processed['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # Generate TOC if not provided
        if 'toc' not in processed and 'sections' in processed:
            # Construct a temporary markdown document to generate TOC
            temp_md = ""
            for section in processed['sections']:
                if 'title' in section:
                    temp_md += f"## {section['title']}\n\n"
                    if 'subsections' in section:
                        for subsection in section['subsections']:
                            temp_md += f"### {subsection['title']}\n\n"
            
            processed['toc'] = self.toc_generator.generate_toc(temp_md)
        
        return processed
    
    def _generate_markdown(self, content: Dict[str, Any], filename: str = None) -> str:
        """Generate markdown documentation"""
        if not filename:
            filename = f"{content.get('title', 'documentation').lower().replace(' ', '_')}.md"
        
        # Render template
        markdown_content = self.template_manager.render_template("markdown.md", content)
        
        # Apply style
        style_config = self.style_config['markdown']
        if style_config['heading_style'] == 'setext':
            # Convert ATX headings to setext headings
            lines = markdown_content.splitlines()
            styled_lines = []
            
            i = 0
            while i < len(lines):
                if lines[i].startswith('# '):
                    styled_lines.append(lines[i][2:])
                    styled_lines.append('=' * len(lines[i][2:]))
                elif lines[i].startswith('## '):
                    styled_lines.append(lines[i][3:])
                    styled_lines.append('-' * len(lines[i][3:]))
                else:
                    styled_lines.append(lines[i])
                i += 1
            
            markdown_content = '\n'.join(styled_lines)
        
        # Save to file
        output_path = self.output_dir / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        return str(output_path)
    
    def _generate_html(self, content: Dict[str, Any], filename: str = None) -> str:
        """Generate HTML documentation"""
        if not filename:
            filename = f"{content.get('title', 'documentation').lower().replace(' ', '_')}.html"
        
        # Convert markdown content to HTML
        if 'sections' in content:
            for section in content['sections']:
                if 'content' in section:
                    # Convert markdown to HTML
                    section['content'] = markdown.markdown(
                        section['content'],
                        extensions=['fenced_code', 'tables', 'toc']
                    )
        
        # Convert TOC to HTML if it's in markdown format
        if 'toc' in content and not content['toc'].startswith('<'):
            content['toc'] = markdown.markdown(
                content['toc'],
                extensions=['toc']
            )
        
        # Render template
        html_content = self.template_manager.render_template("html.html", content)
        
        # Save to file
        output_path = self.output_dir / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(output_path)
    
    def _generate_pdf(self, content: Dict[str, Any], filename: str = None) -> str:
        """Generate PDF documentation"""
        if not filename:
            filename = f"{content.get('title', 'documentation').lower().replace(' ', '_')}.pdf"
        
        # First generate HTML
        html_path = self._generate_html(content, f"{filename.replace('.pdf', '.html')}")
        
        # Convert HTML to PDF
        try:
            # Check for weasyprint or alternative PDF libraries
            pdf_path = self.output_dir / filename
            
            # This requires external libraries; the implementation will depend on what's available
            # For now, we'll just leave a placeholder
            print(f"PDF generation from {html_path} would create {pdf_path}")
            
            # In a real implementation, you'd use something like:
            # from weasyprint import HTML
            # HTML(html_path).write_pdf(pdf_path)
            
            return str(pdf_path)
        except ImportError:
            print("PDF generation requires additional libraries (e.g., weasyprint)")
            return html_path
    
    def format_multiple_documents(self, 
                                 documents: List[Dict[str, Any]],
                                 output_format: str = "markdown",
                                 combined: bool = False) -> Union[List[str], str]:
        """
        Format multiple documents, either separately or combined
        
        Args:
            documents: List of document content dictionaries
            output_format: Target format (markdown, html, pdf)
            combined: Whether to combine documents into a single output
            
        Returns:
            List of output file paths or single output path if combined
        """
        if combined:
            # Combine documents into one
            combined_content = {
                "title": "Combined Documentation",
                "sections": []
            }
            
            # Extract sections from all documents
            for doc in documents:
                if 'title' in doc:
                    # Add document title as a section
                    section = {
                        "title": doc['title'],
                        "content": "",
                        "subsections": []
                    }
                    
                    # Add document sections as subsections
                    if 'sections' in doc:
                        for doc_section in doc['sections']:
                            subsection = doc_section.copy()
                            section["subsections"].append(subsection)
                    
                    combined_content["sections"].append(section)
            
            # Format combined document
            return self.format_document(combined_content, output_format, "combined_documentation")
        else:
            # Format each document separately
            output_paths = []
            for doc in documents:
                output_path = self.format_document(doc, output_format)
                output_paths.append(output_path)
            
            return output_paths
    
    def generate_index(self, documents: List[Dict[str, Any]], output_format: str = "html") -> str:
        """
        Generate an index page for multiple documents
        
        Args:
            documents: List of document content dictionaries
            output_format: Target format (markdown, html, pdf)
            
        Returns:
            Path to the generated index file
        """
        index_content = {
            "title": "Documentation Index",
            "sections": [
                {
                    "title": "Available Documents",
                    "content": "",
                    "items": []
                }
            ]
        }
        
        # Build list of documents
        for doc in documents:
            if 'title' in doc:
                filename = f"{doc['title'].lower().replace(' ', '_')}.{output_format}"
                index_content["sections"][0]["items"].append({
                    "title": doc['title'],
                    "filename": filename,
                    "description": doc.get('description', '')
                })
        
        # Generate link list
        item_list = []
        for item in index_content["sections"][0]["items"]:
            desc = f" - {item['description']}" if item['description'] else ""
            item_list.append(f"- [{item['title']}]({item['filename']}){desc}")
        
        index_content["sections"][0]["content"] = "\n".join(item_list)
        
        # Format index document
        return self.format_document(index_content, output_format, f"index.{output_format}")