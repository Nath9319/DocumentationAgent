# This file contains the prompt templates used by the AI Documentation Agent.
# Centralizing them here makes it easy to experiment with different phrasings
# and instructions for the language model.

DOCUMENTATION_PROMPT_TEMPLATE = """
You are an expert technical writer, tasked with creating clear and concise documentation for a function or class within a larger codebase.

**Your Goal:** Document the following code node: `{node_name}`

**Node Information:**
- **Category:** {node_category}
- **File Path:** {node_fname}
- **Lines:** {node_line_start} to {node_line_end}
- **Existing Docstring:** {node_docstring}

**Context from Dependencies (what `{node_name}` uses):**
{dependencies_context}

**Source Code:**
```python
{source_code}
"""