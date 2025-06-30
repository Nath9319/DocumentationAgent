# File: prompts/templates.py
#
# This file contains the prompt templates used by the AI Documentation Agent.
# Centralizing them here makes it easy to experiment with different phrasings
# and instructions for the language model.

DOCUMENTATION_PROMPT_TEMPLATE = """
You are an expert technical writer. Your task is to generate clear, accurate, and concise documentation for a function or class in a Python codebase.

**Document this code node:** `{node_name}`

**Node Details:**
- **Category:** {node_category}
- **File Path:** {node_fname}
- **Lines:** {node_line_start} to {node_line_end}
- **Existing Docstring:** {node_docstring}

**Dependency Context:**  
{dependencies_context}

**Source Code:**
```python
{source_code}
```

---

**Instructions:**
- Use all provided information (source code, existing docstring, dependency context).
- If the existing docstring is sufficient, improve its clarity and formatting. If it is missing or inadequate, write a new one.
- Write the documentation as a Markdown block, suitable for inclusion in a codebase or documentation site.

**Your documentation must include these sections:**
1. **Description:** A concise, high-level summary of what the function or class does and its purpose in the codebase.
2. **Parameters/Attributes:** List all parameters (for functions) or key attributes (for classes), including their types and a brief description. If none, state "None".
3. **Returns:** Describe the return value and its type. If nothing is returned, state "None".
4. **Example Usage:** (Optional, but recommended) Provide a short, clear code snippet showing typical usage.

**Formatting requirements:**
- Use Markdown headings for each section.
- Be precise and avoid unnecessary repetition.
- Do not include any text outside the documentation block.

Begin the documentation now.
"""

# --- NEW PROMPT FOR CONCEPTUAL GRAPH ---
CONCEPTUAL_GRAPH_PROMPT_TEMPLATE = """
You are a senior software architect. Your task is to analyze the provided code node and its documentation, then generate a high-level conceptual graph in JSON format.

**Context:**
- **Node Name:** `{node_name}`
- **Documentation:** {documentation}
- **Dependencies:** {dependencies_context}

**Source Code:**
```python
{source_code}
```

**Instructions:**
1. Identify the main conceptual entity represented by this node.
2. For each dependency, define a relationship from this node to the dependency.
3. Use clear, descriptive labels for both nodes and relationships.
4. Categorize each node as one of: "Data Model", "Business Logic", "Utility", "Configuration", or another concise type.
5. Write a one-sentence summary for each node's role.
6. Output only a single valid JSON object, matching the structure below. Do not include any extra text or formatting.

**JSON Output Format:**
{{
  "nodes": [
    {{
      "id": "Unique identifier for the concept (usually `{node_name}`)",
      "label": "Short, descriptive label (e.g., 'User Authentication Logic')",
      "type": "Category (e.g., 'Business Logic')",
      "description": "One-sentence summary of this concept's role."
    }}
  ],
  "edges": [
    {{
      "source": "Source node id (e.g., `{node_name}`)",
      "target": "Target node id (a dependency)",
      "label": "Relationship type (e.g., 'USES', 'MODIFIES', 'CONFIGURES', 'INHERITS_FROM')"
    }}
  ]
}}

**Example:**
{{
  "nodes": [
    {{
      "id": "process_user_data",
      "label": "User Data Processor",
      "type": "Business Logic",
      "description": "Processes raw user input and prepares it for database insertion."
    }}
  ],
  "edges": [
    {{
      "source": "process_user_data",
      "target": "DatabaseConfig",
      "label": "USES"
    }},
    {{
      "source": "process_user_data",
      "target": "UserRecord",
      "label": "MODIFIES"
    }}
  ]
}}

Output only the JSON object. Do not include markdown, explanations, or any other text.
"""