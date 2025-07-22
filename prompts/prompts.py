
HIERARCHICAL_STRUCTURE = {
    "Core Repository Documentation": [
        "Project Introduction",
        "Installation & Setup",
    ],
    "Architecture & Design Documentation": [
        "System Architecture",
        "Logical Architecture",
        #"Physical Architecture",
        "Data Architecture",
    ],
    "Development & Operations Documentation": [
        "Code Documentation",
        #"Contributing Guide",
        "Build & Deployment",
        #"Development Environment",
        #"Code Review Process",
    ],
    "API & Integration Documentation": [
        "API Documentation",
        #"Integration Guide",
        #"Sequence Diagrams",
    ],
    "Technical Implementation Details": [
        "Implementation View",
        "Database Schemas",
        #"Error Handling",
        "Performance Considerations",
    ]
}

ALL_SECTIONS = [subsection for section_list in HIERARCHICAL_STRUCTURE.values() for subsection in section_list]

# --- NEW: Hyper-specific, format-aware prompts ---
AGENT_PROMPTS = {
    "Project Introduction": """
        You are an expert technical writer creating the "Project Introduction". Your tone is engaging and clear.
        Your task is to UPDATE the existing introduction by integrating insights from the component `{component_name}`.
        Focus on high-level purpose, scope, and what problem this project solves.

        **Formatting Instructions:**
        - Use bold (`**...**`) for the project name and key concepts.
        - Use bulleted lists (`- ...`) to highlight primary objectives or features.
        - Keep paragraphs concise and easy to read.

        EXISTING INTRODUCTION:
        ---
        {existing_content}
        ---

        Respond with the complete, updated markdown for the "Project Introduction" section.
    """,
    "Installation & Setup": """
        You are a technical writer creating a crystal-clear "Installation & Setup" guide.
        Analyze the documentation for `{component_name}` for any prerequisites, dependencies, environment variables, or setup commands.
        Your task is to UPDATE the existing guide by integrating these new steps logically.

        **Formatting Instructions:**
        - Use subheadings like `### Prerequisites` and `### Installation Steps`.
        - Use numbered lists for sequential steps.
        - **ALL** shell commands **MUST** be in code blocks (e.g., ```bash\nnpm install\n```).
        - **ALL** package names, filenames, and environment variables **MUST** be in inline code (e.g., `requests`, `.env`, `DATABASE_URL`).

        EXISTING SETUP GUIDE:
        ---
        {existing_content}
        ---

        Respond with the complete, updated markdown for the "Installation & Setup" section.
    """,
    "System Architecture": """
        You are a system architect documenting the "System Architecture".
        Analyze `{component_name}` and its dependencies (`{component_context}`) to explain its role.
        Your task is to UPDATE the existing architecture document.

        **Formatting Instructions:**
        - Use subheadings (`###`) for each major component or architectural pattern.
        - Use bold (`**...**`) to emphasize key architectural terms (e.g., **Microservices**, **API Gateway**).
        - Use bullet points to describe relationships between components.
        - Use blockquotes (`> **Architectural Note:** ...`) to add rationale or important notes.

        EXISTING ARCHITECTURE DOCUMENTATION:
        ---
        {existing_content}
        ---

        Respond with the complete, updated markdown for the "System Architecture" section.
    """,
    "API Documentation": """
        You are a meticulous API documentarian creating the "API Documentation".
        From `{component_name}`'s documentation, extract endpoint details, methods, parameters, and example request/response bodies.
        Your task is to UPDATE the existing API reference by adding a new, clearly-defined section for this component.

        **Formatting Instructions:**
        - Use a main subheading (`###`) for the component/endpoint (e.g., `### POST /api/v1/calculate`).
        - **MUST** use a Markdown table for parameters with headers: `| Parameter | Type | Description |`.
        - **MUST** use code blocks with language identifiers for examples (e.g., ```json\n{{"key": "value"}}\n```).
        - Use blockquotes (`> **Note:**`) for important implementation details.

        EXISTING API DOCUMENTATION:
        ---
        {existing_content}
        ---

        Respond with the complete, updated markdown for the "API Documentation" section.
    """,
    "Code Documentation": """
        You are a senior developer documenting the codebase in the "Code Documentation" section.
        Review `{component_name}` and explain its logic, class structure, and key functions.
        Your task is to UPDATE the existing documentation by adding a detailed subsection for `{component_name}`.

        **Formatting Instructions:**
        - Use a subheading (`###`) for the component/module name (e.g., `### Module: 'stats_service.py'`).
        - For key functions, use smaller subheadings (`####`) and describe their purpose.
        - **MUST** use a Markdown table for parameters and return values.
        - **MUST** include well-commented code snippets in code blocks (e.g., ```python\n# code here\n```).

        EXISTING CODE DOCUMENTATION:
        ---
        {existing_content}
        ---

        Respond with the complete, updated markdown for the "Code Documentation" section.
    """,
    "Error Handling": """
        You are a reliability engineer documenting "Error Handling" strategies.
        Analyze `{component_name}` for custom exceptions, error codes, and handling logic.
        Your task is to UPDATE the error handling guide.

        **Formatting Instructions:**
        - **MUST** use a Markdown table to list custom exceptions with headers: `| Exception Name | Status Code | Description |`.
        - Provide code examples (```python ... ```) showing how to `try...except` these exceptions.
        - Use blockquotes (`> **Best Practice:** ...`) for important warnings or advice.

        EXISTING ERROR HANDLING GUIDE:
        ---
        {existing_content}
        ---

        Respond with the complete, updated markdown for the "Error Handling" section.
    """,
    "Data Architecture": """
        You are a data architect documenting the "Data Architecture".
        From `{component_name}`, extract information about database interactions, schemas, data models, or data flow.
        Your task is to UPDATE the existing data architecture documentation.

        **Formatting Instructions:**
        - Use subheadings (`###`) for different data models or database tables.
        - **MUST** use Markdown tables to describe table schemas with headers: `| Column | Type | Constraints | Description |`.
        - **MUST** use code blocks (```sql ... ```) for SQL schema definitions or important queries.

        EXISTING DATA ARCHITECTURE DOCUMENTATION:
        ---
        {existing_content}
        ---

        Respond with the complete, updated markdown for the "Data Architecture" section.
    """
}
