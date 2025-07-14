# File: prompts/templates.py
#
# This file centralizes all the prompt templates used by the agent nodes.
# ENHANCED VERSION: Added validation and improved analysis prompts

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

# ENHANCED: More detailed analysis prompt for better dependency detection
ENHANCED_CODE_ANALYSIS_PROMPT_TEMPLATE = """
You are an expert Python code analyzer. Your task is to identify ALL dependencies within the provided code snippet.

**Code Snippet:**
```python
{source_code}
```

**Instructions:**
1. Identify every unique function, method, class, or module that is:
   - Called as a function: `func()`, `module.func()`
   - Instantiated as a class: `MyClass()`, `module.MyClass()`
   - Used as a method: `obj.method()`, `self.method()`
   - Imported: `import module`, `from module import func`
   - Used as an attribute: `module.constant`, `class.attribute`

2. Include both:
   - Internal dependencies (from the same codebase)
   - External dependencies (from standard library or third-party packages)

3. For method calls on objects, include both:
   - The method name (e.g., `append` for `list.append()`)
   - The object's class if identifiable (e.g., `list` for a list object)

4. Do NOT include:
   - The name of the function/class being defined in this snippet
   - Python keywords (if, for, while, etc.)
   - Built-in functions unless explicitly called (print, len, etc.)

5. For chained calls like `obj.method1().method2()`, include both methods.

**Output Format:**
Return a JSON object with categorized dependencies:
{{
    "internal_functions": ["function1", "function2"],
    "internal_classes": ["MyClass", "AnotherClass"],
    "internal_methods": ["self.helper", "obj.process"],
    "external_imports": ["os", "json", "numpy"],
    "external_calls": ["os.path.join", "json.dumps", "np.array"],
    "uncertain": ["might_be_internal_or_external"]
}}

**Your JSON Output:**
"""

# NEW: Context validation prompt
CONTEXT_VALIDATION_PROMPT_TEMPLATE = """
You are a code documentation expert validator. Review the gathered context and verify its completeness for documentation purposes.

**Original Code Being Analyzed:**
```python
{source_code}
```

**Identified Dependencies:** 
{dependencies}

**Gathered Context Summary:**
{context_summary}

**Task:** 
Analyze if all necessary dependencies have been found and if the context is sufficient for creating comprehensive documentation.

Consider:
1. Are all function/method calls properly resolved?
2. Are there any critical dependencies that seem to be missing?
3. Is the context detailed enough to understand how this code interacts with its dependencies?
4. Are there any ambiguous references that need clarification?

Return a JSON object with:
{{
    "is_complete": boolean,  // true if context is sufficient for documentation
    "missing_critical": [],   // list of critical missing dependencies that would impact documentation
    "confidence_score": 0.0,  // float between 0-1 indicating confidence in completeness
    "suggestions": [],        // list of specific suggestions for improving context
    "ambiguous_refs": []      // list of references that could have multiple interpretations
}}

**JSON Output:**
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

# ENHANCED: Documentation prompt with quality awareness
ENHANCED_DOCUMENTATION_PROMPT_TEMPLATE = """
You are an expert technical writer creating comprehensive documentation for a Python codebase.

**Your Goal:** Document the following code node: `{node_name}`

**Node Information:**
- **Category:** {node_category}
- **File Path:** {node_fname}
- **Lines:** {node_line_start} to {node_line_end}
- **Existing Docstring:** {node_docstring}

**Context from Dependencies:**
{dependencies_context}

**Context Quality Metadata:**
{context_metadata}

---
**Instructions:**

Create a comprehensive Markdown-formatted documentation that includes:

1. **Function/Class Signature**
   - Full signature with type hints if available
   - Clear indication of required vs optional parameters

2. **Purpose & Overview**
   - What problem does this code solve?
   - How does it fit into the larger system?

3. **Parameters/Attributes**
   - Name, type, and description for each parameter
   - Default values and constraints
   - For classes: key attributes and their purposes

4. **Returns**
   - Type and description of return value
   - Possible return states or conditions
   - Error/exception cases

5. **Detailed Behavior**
   - Step-by-step explanation of the logic
   - Key algorithms or design patterns used
   - How it interacts with dependencies
   - Any side effects or state changes

6. **Usage Examples**
   - Basic usage example
   - Advanced usage if applicable
   - Common patterns or best practices

7. **Dependencies & Integration**
   - How this code uses its dependencies
   - What other parts of the system depend on this
   - Any coupling or cohesion concerns

8. **Notes & Warnings**
   - Performance considerations
   - Known limitations or edge cases
   - Security implications if any
   - Future improvement suggestions

**Special Instructions:**
- If context quality is low (confidence < 0.7), add a note about potential missing information
- Highlight any ambiguous dependencies that couldn't be fully resolved
- Do NOT include actual source code blocks in the documentation
- Focus on explaining behavior and purpose rather than implementation details

Generate the documentation now.
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
5. Summarize the node's primary responsibility in a single, clear sentence. Focus on what it does and why it exists.
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

# ENHANCED: Conceptual graph prompt with confidence awareness
ENHANCED_CONCEPTUAL_GRAPH_PROMPT_TEMPLATE = """
You are a senior software architect analyzing code to build a high-level conceptual graph.

**Context Provided:**
- **Node Name:** `{node_name}`
- **Generated Documentation:** {documentation}
- **Dependencies Context:** {dependencies_context}
- **Dependency Resolution Metadata:** {dependency_metadata}
- **Source Code:**
```python
{source_code}
```

**Instructions:**

1. **Analyze the node's conceptual role** considering:
   - Its primary responsibility in the system
   - The design pattern it implements (if any)
   - Its architectural layer (presentation, business, data, etc.)

2. **Create semantic metadata** that captures:
   - A descriptive label that would make sense to someone unfamiliar with the code
   - A conceptual type from this enhanced list:
     * "Data Model" - Represents domain entities
     * "Business Logic" - Implements business rules
     * "Controller" - Handles request/response flow
     * "Service" - Provides specific functionality
     * "Repository" - Manages data access
     * "Utility" - Helper functions/classes
     * "Configuration" - System configuration
     * "API Endpoint" - External interface
     * "Event Handler" - Responds to events
     * "Validator" - Input/data validation
     * "Transformer" - Data transformation
     * "Factory" - Object creation
     * "Decorator" - Adds functionality
     * "Middleware" - Request/response pipeline
   - A clear, single-sentence summary of its purpose

3. **Map semantic relationships** using these precise labels:
   - "USES" - Directly uses functionality
   - "IMPLEMENTS" - Implements an interface/protocol
   - "EXTENDS" - Inherits from
   - "COMPOSES" - Contains as a component
   - "DECORATES" - Adds behavior to
   - "VALIDATES" - Performs validation for
   - "TRANSFORMS" - Converts data for/from
   - "ORCHESTRATES" - Coordinates multiple components
   - "PUBLISHES" - Emits events/messages
   - "SUBSCRIBES" - Listens to events/messages
   - "CONFIGURES" - Sets up configuration
   - "CREATES" - Factory relationship
   - "DEPENDS_ON" - Has a dependency on

4. **Consider dependency confidence** when creating edges:
   - Only include edges for dependencies with confidence > 0.5
   - Note uncertain relationships in metadata

**Output JSON Structure:**
{{
  "semantic_metadata": {{
    "label": "Descriptive concept label",
    "type": "One of the conceptual types listed above",
    "summary": "One-sentence description of primary responsibility",
    "patterns": ["List", "of", "design", "patterns", "if", "any"],
    "layer": "architectural layer (e.g., 'business', 'data', 'presentation')",
    "complexity": "low|medium|high based on dependencies and logic"
  }},
  "semantic_edges": [
    {{
      "target": "Dependency node name",
      "label": "Relationship type from list above",
      "confidence": 0.95,  // Confidence in this relationship
      "reason": "Brief explanation of why this relationship exists"
    }}
  ],
  "quality_notes": {{
    "unresolved_deps": ["List of dependencies that couldn't be fully resolved"],
    "assumptions": ["Any assumptions made due to missing context"]
  }}
}}

Only output the JSON object.
"""

# Fallback prompts for error handling
FALLBACK_DEPENDENCY_ANALYSIS_TEMPLATE = """
Analyze this Python code and list all function calls, method calls, and class instantiations.

Code:
```python
{source_code}
```

List each dependency on a separate line, one per line, nothing else:
"""

COMPREHENSIVE_DOCUMENTATION_PROMPT_TEMPLATE = """
You are a senior technical writer creating enterprise-grade documentation for a production codebase.

**Node: `{node_name}`**
**Type:** {node_category} | **File:** {node_fname} | **Lines:** {node_line_start}-{node_line_end}

**Source Code:**
```python
{source_code}
```
"""