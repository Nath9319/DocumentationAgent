# File: prompts/templates.py
#
# This file centralizes all the prompt templates used by the agent nodes.
# Keeping them in one place makes them easier to manage, version, and share.

CODE_ANALYSIS_PROMPT_TEMPLATE = """
You are an expert Python code analyzer. Your task is to identify all function calls, method calls, and class instantiations within the provided code snippet.

**Code Snippet:**
```python
{source_code}
```

**Instructions:**
1.  Analyze the code and identify every unique function, method, or class that is called or instantiated.
2.  Do NOT include the name of the function or class being defined in the snippet itself.
3.  List the names of these dependencies as a JSON array of strings.
4.  If no dependencies are found, return an empty array.

**JSON Output Example:**
["os.path.join", "MyHelperClass", "another_function", "self.helper_method"]

**Your JSON Output:**
"""

DOCUMENTATION_PROMPT_TEMPLATE = """
You are an expert technical writer, tasked with creating clear, comprehensive, and precise documentation for a function or class within a larger codebase.

**Your Goal:** Document the following code node: `{node_name}`

**Node Information:**
- **Category:** {node_category}
- **File Path:** {node_fname}
- **Lines:** {node_line_start} to {node_line_end}
- **Existing Docstring:** {node_docstring}

**Context from Dependencies (what `{node_name}` uses):**
{dependencies_context}

---
**Instructions:**

Based on all the information provided (source code, existing docstring, and the documentation of its dependencies), generate a comprehensive Markdown-formatted documentation block.

IMPORTANT: Do NOT include the actual code or code blocks from the source in your documentation output. Only summarize and explain the code's behavior, logic, and usage.
Do NOT include the actual code or code blocks from the source in your documentation output. Only summarize and explain.

Your documentation MUST include the following sections:
1.  **Function/Class Name and Signature:** Clearly state the function or class name, its arguments, and their types.
2.  **Description:** A high-level summary of what the function/class does, including the overall task and logic.
3.  **Parameters/Attributes:** List all parameters (for functions) or key attributes (for classes), their types, and a description of each. If there are none, state "None".
4.  **Expected Input:** Describe what kind of data or objects are expected as input, including any constraints or special cases.
5.  **Returns:** Describe the return value, its type, and what it represents. If it returns nothing, state "None".
6.  **Detailed Logic:** Explain the main steps, algorithms, or logic used. Mention what functions or objects are called, and how they interact within this code.

---

**Example Documentation:**


### calculate_payment(principal: float, annual_rate: float, num_payments: int) -> float

**Description:**
Calculates the fixed periodic payment required to fully amortize a loan over a specified number of payments, using the net present value formula.

**Parameters:**
- `principal` (`float`): The initial amount of the loan.
- `annual_rate` (`float`): The annual interest rate as a decimal (e.g., 0.05 for 5%).
- `num_payments` (`int`): The total number of periodic payments to be made.

**Expected Input:**
- `principal` should be a positive float representing the loan amount.
- `annual_rate` should be a non-negative float (0.0 means no interest).
- `num_payments` should be a positive integer.

**Returns:**
`float`: The fixed payment amount to be made in each period.

**Detailed Logic:**
- The function first checks if the interest rate is zero. If so, it divides the principal evenly across all payments.
- If the interest rate is non-zero, it calculates the periodic interest rate by dividing the annual rate by 12.
- It then applies the standard amortization formula to compute the payment.
- This function does not interact with external modules, but relies on basic arithmetic and the `pow` function.


Begin the documentation now.
"""

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