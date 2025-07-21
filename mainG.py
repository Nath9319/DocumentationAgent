import os
import json
import pickle
import networkx as nx
from typing import TypedDict, List, Dict, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers.string import StrOutputParser
from langchain_core.output_parsers.json import JsonOutputParser
from langchain_openai import AzureChatOpenAI
from langgraph.graph import StateGraph, END

# --- 1. Environment Setup & Model Initialization ---
llm = AzureChatOpenAI(
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("OPENAI_API_VERSION", "2024-02-01"),
    temperature=0.2, # Increased for more creative and better-structured writing
    max_tokens=4000
)

# --- 2. Define the Hierarchical Documentation Structure & Agent Prompts ---

HIERARCHICAL_STRUCTURE = {
    "Core Repository Documentation": [
        "Project Introduction",
        "Installation & Setup",
    ],
    "Architecture & Design Documentation": [
        "System Architecture",
        "Design Decision Logs",
        "Logical Architecture",
        "Physical Architecture",
        "Data Architecture",
        "Security Architecture",
    ],
    "Development & Operations Documentation": [
        "Code Documentation",
        "Contributing Guide",
        "Build & Deployment",
        "Development Environment",
        "Code Review Process",
    ],
    "API & Integration Documentation": [
        "API Documentation",
        "Integration Guide",
        "Sequence Diagrams",
    ],
    "Technical Implementation Details": [
        "Implementation View",
        "Database Schemas",
        "Error Handling",
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


# --- 3. Define the Graph's State ---
class DocumentationState(TypedDict):
    unprocessed_components: List[str]
    all_data: Dict
    nx_graph: nx.Graph
    document_content: Dict[str, str]
    current_component_name: Optional[str]
    current_component_doc: Optional[str]
    current_component_context: Optional[str]
    target_sections: List[str]
    final_document: Optional[str]
    # --- FIX: Add a key to store the scrapper's decision ---
    scrapper_decision: str

# --- 4. Agent Node Functions ---

def load_all_data(json_path: str, graph_path: str) -> Dict:
    """Loads all initial data."""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            doc_data = json.load(f)
        with open(graph_path, 'rb') as f:
            graph_data = pickle.load(f)
        return {"all_data": doc_data, "nx_graph": graph_data}
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return {}

def component_loader_node(state: DocumentationState) -> DocumentationState:
    """Pops the next component and loads its data into the state."""
    if not state["unprocessed_components"]:
        return state
    component_name = state["unprocessed_components"].pop(0)
    print(f"\n--- 📥 Loader: Loading component '{component_name}' ---")
    state["current_component_name"] = component_name
    component_data = state["all_data"][component_name]
    state["current_component_doc"] = component_data["documentation"]
    graph = state["nx_graph"]
    context = "This component operates independently."
    if component_name in graph:
        neighbors = list(nx.all_neighbors(graph, component_name))
        if neighbors:
            summaries = [f"- `{n}`: {state['all_data'][n]['conceptual_data']['semantic_metadata']['summary']}" for n in neighbors if n in state['all_data']]
            if summaries:
                context = "It interacts with or depends on:\n" + "\n".join(summaries)
    state["current_component_context"] = context
    return state

# --- FIX: Modify scrapper_node to return a dictionary for state update ---
def scrapper_node(state: DocumentationState) -> dict:
    """Decides if the component's documentation is substantial and updates the state with the decision."""
    print(f"--- 🗑️ Scrapper: Analyzing '{state['current_component_name']}' ---")
    doc_length = len(state['current_component_doc'].split())
    
    decision = "proceed" # Default decision
    if doc_length < 10:
        print(f"--- 🗑️ Scrapper: Decision is to SCRAP (too short). ---")
        decision = "scrap"
    else:
        prompt = ChatPromptTemplate.from_template(
            """Analyze the documentation for component `{component_name}`. Is it trivial (e.g., a simple import, a variable declaration) or substantial (describes logic, a class, a function, configuration)?
            Documentation: --- {component_doc} ---
            Respond with a single word: "Proceed" if substantial, or "Scrap" if trivial."""
        )
        chain = prompt | llm | StrOutputParser()
        llm_decision = chain.invoke({"component_name": state["current_component_name"], "component_doc": state["current_component_doc"]})
        
        if "Scrap" in llm_decision:
            print(f"--- 🗑️ Scrapper: Decision is to SCRAP. ---")
            decision = "scrap"
        else:
            print(f"--- 🗑️ Scrapper: Decision is to PROCEED. ---")
            decision = "proceed"
            
    # Return a dictionary to update the state, this is the main fix.
    return {"scrapper_decision": decision}

def selector_node(state: DocumentationState) -> DocumentationState:
    """Selects which documentation sections are relevant for the current component."""
    print(f"--- 🎯 Selector: Choosing sections for '{state['current_component_name']}' ---")
    prompt = ChatPromptTemplate.from_template(
        """You are a document routing expert. Based on the documentation for component `{component_name}`, select ALL sections where this information would be relevant.
        Component Documentation: --- {component_doc} ---
        Available Sections: {sections}
        Respond with a JSON object containing a single key "relevant_sections" which is a list of strings from the available sections.
        Example: {{"relevant_sections": ["API Documentation", "Error Handling"]}}"""
    )
    section_list_str = "\n".join([f"- {s}" for s in ALL_SECTIONS])
    chain = prompt | llm | JsonOutputParser()
    response = chain.invoke({"component_name": state["current_component_name"], "component_doc": state["current_component_doc"], "sections": section_list_str})
    relevant_sections = response.get("relevant_sections", [])
    state["target_sections"] = [s for s in relevant_sections if s in ALL_SECTIONS]
    print(f"--- 🎯 Selector: Chosen sections: {state['target_sections']} ---")
    return state

def parallel_writer_node(state: DocumentationState) -> DocumentationState:
    """Invokes the specialist writer agents in parallel for the selected sections."""
    print(f"--- ✍️ Parallel Writers: Starting for '{state['current_component_name']}' ---")
    for section_name in state["target_sections"]:
        print(f"    - Invoking writer for section: '{section_name}'")
        writer_prompt_template = AGENT_PROMPTS.get(section_name, 
            """You are a technical writer. Your task is to update the "{section_name}" section.
            Analyze `{component_name}` and integrate any relevant information into the existing content.
            Use rich markdown like code blocks, tables, and lists to format the information clearly.
            EXISTING CONTENT: --- {existing_content} ---
            NEW INFORMATION: --- {component_doc} ---
            Respond with the complete, updated markdown for the "{section_name}" section."""
        )
        existing_content = state["document_content"].get(section_name, "")
        prompt = ChatPromptTemplate.from_template(writer_prompt_template)
        chain = prompt | llm | StrOutputParser()
        updated_section_content = chain.invoke({
            "section_name": section_name,
            "existing_content": existing_content or "This section is empty. Please start it.",
            "component_name": state["current_component_name"],
            "component_doc": state["current_component_doc"],
            "component_context": state["current_component_context"]
        })
        state["document_content"][section_name] = updated_section_content
        print(f"    - ✅ Writer for '{section_name}' finished.")
    return state

def compiler_node(state: DocumentationState) -> DocumentationState:
    """Assembles all the final sections into the complete, hierarchical document."""
    print("--- 📚 Compiler: Assembling Final Document ---")
    final_doc_parts = []
    for main_section, subsections in HIERARCHICAL_STRUCTURE.items():
        # Check if any subsection within this main section has content
        section_has_content = any(state["document_content"].get(sub, "").strip() for sub in subsections)
        
        # Only add the main section header if it has content
        if section_has_content:
            final_doc_parts.append(f"# {main_section}")
            for subsection_name in subsections:
                content = state["document_content"].get(subsection_name, "").strip()
                if content:
                    final_doc_parts.append(f"## {subsection_name}\n\n{content}")
    
    state["final_document"] = "\n\n---\n\n".join(final_doc_parts)
    print("--- 🎉 Compiler: Final document assembled! ---")
    return state

# --- 5. Define Graph Edges & Control Flow ---

def should_continue_processing(state: DocumentationState) -> str:
    """Determines if there are more components to process."""
    return "continue" if state["unprocessed_components"] else "end"

# --- 6. Build and Run the Graph ---

workflow = StateGraph(DocumentationState)
workflow.add_node("loader", component_loader_node)
workflow.add_node("scrapper", scrapper_node)
workflow.add_node("selector", selector_node)
workflow.add_node("parallel_writers", parallel_writer_node)
workflow.add_node("compiler", compiler_node)

workflow.set_entry_point("loader")
workflow.add_conditional_edges("loader", should_continue_processing, {"continue": "scrapper", "end": "compiler"})

# --- FIX: Update the conditional edge to read the decision from the state ---
workflow.add_conditional_edges(
    "scrapper",
    lambda state: state["scrapper_decision"], # Read the decision from the state key
    {"scrap": "loader", "proceed": "selector"}
)

workflow.add_edge("selector", "parallel_writers")
workflow.add_edge("parallel_writers", "loader")
workflow.add_edge("compiler", END)

app = workflow.compile()

# --- Main execution block ---
if __name__ == "__main__":
    JSON_FILE = "output/CalculatorCode/documentation_and_graph_data.json"
    GRAPH_FILE = "output/CalculatorCode/conceptual_graph.pkl"
    OUTPUT_FILE = "Complete_Technical_Documentation_v5.md"
    initial_data = load_all_data(JSON_FILE, GRAPH_FILE)
    if initial_data:
        initial_state = DocumentationState(
            unprocessed_components=sorted(initial_data["all_data"].keys()),
            all_data=initial_data["all_data"],
            nx_graph=initial_data["nx_graph"],
            document_content={section: "" for section in ALL_SECTIONS},
            current_component_name=None,
            current_component_doc=None,
            current_component_context=None,
            target_sections=[],
            final_document=None,
            # --- FIX: Initialize the new state key ---
            scrapper_decision=""
        )
        num_components = len(initial_data["all_data"])
        config = {"recursion_limit": num_components * 4 + 15}
        print(f"--- ⚙️ Running graph with recursion limit: {config['recursion_limit']} ---")
        final_state = app.invoke(initial_state, config=config)
        if final_state and final_state.get("final_document"):
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                f.write(final_state["final_document"])
            print(f"\n🚀 Success! Documentation saved to '{OUTPUT_FILE}'")
        else:
            print("\n❌ Failure: The final document could not be generated.")