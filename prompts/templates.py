# File: prompts/templates.py
#
# This file contains the prompt templates used by the AI Documentation Agent.
# The conceptual graph prompt is updated to generate richer, more structured metadata.

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
```

---
**Instructions:**

Based on all the information provided (source code, existing docstring, and the documentation of its dependencies), generate a comprehensive Markdown-formatted documentation block.

If the existing docstring is good, refine and format it. If it's missing or poor, create a new one from scratch.

Your documentation MUST include the following sections:
1.  **Description:** A clear, high-level summary of what the function/class does.
2.  **Parameters/Attributes:** A list of all parameters (for functions) or key attributes (for classes), their types, and a description of each. If there are none, state "None".
3.  **Returns:** A description of the value returned by the function. If it returns nothing, state "None".
4.  **Example Usage:** (Optional but Recommended) A short, clear code snippet showing how to use the function or class.

Begin the documentation now.
"""

# --- MODIFIED PROMPT FOR RICH CONCEPTUAL GRAPH METADATA ---
CONCEPTUAL_GRAPH_PROMPT_TEMPLATE = """
You are a senior software architect. Your task is to deeply analyze the provided code node and generate a high-level conceptual graph that captures its semantic meaning and relationships within the codebase.

**Context Provided:**
- **Node Name:** `{node_name}`
- **Generated Documentation:** {documentation}
- **Dependencies:** {dependencies_context}
- **Source Code:**
```python
{source_code}
```

**Instructions:**

1. Carefully read the provided documentation and source code for `{node_name}`. Consider its purpose, responsibilities, and how it interacts with other components.
2. Identify the main conceptual role of this node. Think about what it represents in the system (e.g., a data model, a business logic component, a utility, a configuration, or an API endpoint).
3. Write a concise, descriptive label for this node that would make sense to a software architect or developer unfamiliar with the codebase.
4. Assign a conceptual type to this node. Use one of: "Data Model", "Business Logic", "Utility", "Configuration", "API Endpoint", or another concise, meaningful category if none of these fit.
5. Summarize the node’s primary responsibility in a single, clear sentence. Focus on what it does and why it exists.
6. Examine the dependencies and the code to determine all meaningful relationships from this node to others. For each, specify:
    - The target node (dependency name).
    - The relationship label, using terms like "USES", "MODIFIES", "CONFIGURES", "INHERITS_FROM", "CREATES", or another precise verb that best describes the connection.
    - Only include relationships that are directly relevant and supported by the code or documentation.
7. Be as specific and informative as possible in your analysis. Avoid vague or generic descriptions.
8. Output a single, valid JSON object in the exact structure below. Do not include any extra text, explanations, or markdown formatting.

**Output JSON Structure:**
{{
  "semantic_metadata": {{
    "label": "A short, descriptive label for the concept (e.g., 'User Data Processor').",
    "type": "A conceptual category, like 'Data Model', 'Business Logic', 'Utility', 'Configuration', 'API Endpoint'.",
    "summary": "A one-sentence summary of this concept's role, explaining its primary responsibility."
  }},
  "semantic_edges": [
    {{
      "target": "The name of a dependency node.",
      "label": "The relationship, like 'USES', 'MODIFIES', 'CONFIGURES', 'INHERITS_FROM', 'CREATES'."
    }}
    // ...repeat for each relevant dependency...
  ]
}}

**Example Response:**
{{
  "semantic_metadata": {{
    "label": "User Data Processor",
    "type": "Business Logic",
    "summary": "Processes raw user input and prepares it for database insertion."
  }},
  "semantic_edges": [
    {{
      "target": "DatabaseConfig",
      "label": "USES"
    }},
    {{
      "target": "UserRecord",
      "label": "MODIFIES"
    }}
  ]
}}

Only output the JSON object. Do not include any other text or markdown formatting.
"""
