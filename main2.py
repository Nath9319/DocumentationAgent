import os
import json
import pickle
import networkx as nx
import asyncio
import logging
import re
import sys
from datetime import datetime
from typing import TypedDict, List, Dict, Optional, Any
from dotenv import load_dotenv
# --- tqdm for progress bar ---
from tqdm import tqdm
import threading
from datetime import datetime, timedelta  # timedelta is new, datetime already exists
import asyncio  # if not already imported
from diagrams import Diagram
from diagrams.programming.language import Python
from diagrams.generic.compute import Rack
from diagrams import Diagram, Cluster, Edge
from diagrams.azure.compute import AppServices, FunctionApps
from diagrams.azure.database import SQLDatabases
from diagrams.azure.integration import APIManagement
from diagrams.programming.language import Python

# Much cleaner code, better visuals

# Set UTF-8 encoding for Windows console to handle emojis
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

# Load environment variables from .env file
load_dotenv()

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers.string import StrOutputParser
from langchain_core.output_parsers.json import JsonOutputParser
from langchain_openai import AzureChatOpenAI
from langgraph.graph import StateGraph, END

# --- Configure logging ---

# --- Custom StreamHandler with UTF-8 encoding for emoji support ---
import sys
class StreamHandlerUTF8(logging.StreamHandler):
    def __init__(self, stream=None):
        if stream is None:
            stream = sys.stdout
        # Wrap the stream with UTF-8 encoding if possible
        try:
            stream = open(stream.fileno(), mode='w', encoding='utf-8', buffering=1)
        except Exception:
            pass  # fallback to default if not possible
        super().__init__(stream)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('documentation_generation.log', encoding='utf-8'),
        StreamHandlerUTF8()
    ]
)
logger = logging.getLogger(__name__)

# --- Create output directory for incremental saves ---
INCREMENTAL_SAVE_DIR = "incremental_saves"
os.makedirs(INCREMENTAL_SAVE_DIR, exist_ok=True)

# --- Global progress bar variable ---
progress_bar = None

# --- 1. Environment Setup & Model Initialization ---
llm = AzureChatOpenAI(
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("OPENAI_API_VERSION", "2024-02-01"),
    temperature=0.1, # Increased for more creative and better-structured writing
    # max_tokens=40000
)

# --- 2. Define the Hierarchical Documentation Structure & Agent Prompts ---

HIERARCHICAL_STRUCTURE = {
    "Core Repository Documentation": [
        "Project Introduction",
        "Installation & Setup",
    ],
    "Architecture & Design Documentation": [
        "System Architecture",
        "Logical Architecture",
        "Data Architecture",
    ],
    "Development & Operations Documentation": [
        "Code Documentation",
    ],
    "API & Integration Documentation": [
        "API Documentation",
        "Integration Guide",
    ],
    "Technical Implementation Details": [
        "Implementation View",
        "Database Schemas",
    ]
}

ALL_SECTIONS = [subsection for section_list in HIERARCHICAL_STRUCTURE.values() for subsection in section_list]

# --- NEW: Hyper-specific, format-aware prompts ---
AGENT_PROMPTS = {
    "Project Introduction": """
        You are an expert technical writer creating the "Project Introduction". Your tone is engaging and clear.
        Your task is to UPDATE the existing introduction by integrating insights from the component `{component_name}`.
        
        **PRIMARY FOCUS**: Analyze `{component_name}` thoroughly and focus on its high-level purpose, scope, and problem-solving capabilities.
        **REFERENCE CONTEXT**: Use connected components as contextual reference only: {component_context}
        
        **CRITICAL INFORMATION POLICY**:
        - ONLY include information that is explicitly present in the provided documents
        - DO NOT create, infer, or assume any information that is not directly stated
        - If you are uncertain about any detail, it is better to OMIT it rather than include potentially incorrect information
        - Base your documentation strictly on the factual content provided in the component documentation and connected components
         - DO NOT ADD ANY DATABASE OR TABLE THAT IS NOT MENTIONED IN THE CODE. DO NOT CREATE ANY NEW EXAMPLE DATABASES OR TABLES ANYWHERE.
         
        **ITERATIVE INTEGRATION POLICY**:
        - This is an ITERATIVE process - preserve all existing valuable information
        - DO NOT overwrite or remove important segments from existing content
        - INTEGRATE new information seamlessly with existing content
        - AVOID creating contradictory information - if there's a conflict, prioritize the most recent and specific information
        - ENHANCE and EXPAND existing sections rather than replacing them
        - Maintain consistency across all iterations
        
        **Output Requirements**:
        - Produce articulated, detailed, technical documentation
        - Use precise technical terminology and industry-standard language
        - Be comprehensive yet concise, covering all relevant aspects
        - Integrate information from all important connected components as supporting context

        **Formatting Instructions:**
        - Use bold (`**...**`) for the project name and key concepts.
        - Use bulleted lists (`- ...`) to highlight primary objectives or features.
        - Keep paragraphs concise and easy to read.

        EXISTING INTRODUCTION:
        ---
        {existing_content}
        ---

        Respond with the complete, updated markdown for the "Project Introduction" section. Do NOT wrap the entire output in triple backticks or code blocks. Only use code blocks for actual code, not for the whole section.
    """,
    "Installation & Setup": """
        You are a technical writer creating a crystal-clear "Installation & Setup" guide.
        
        **PRIMARY FOCUS**: Analyze `{component_name}` for prerequisites, dependencies, environment variables, and setup commands.
        **REFERENCE CONTEXT**: Use connected components as contextual reference only: {component_context}
        
          **ZERO-HALLUCINATION DIRECTIVES**
        **The Rule of Evidence (Mandatory)**: For every single statement you add, you must be able to trace it back to a specific line, keyword, function name, or code block in the provided context. **If you cannot find direct, unambiguous evidence, you MUST NOT write the statement.**
        **Strict Prohibition of Inference**: You are FORBIDDEN from making logical leaps, inferring developer intent, or assuming "best practices."
            -   **Example (Allowed)**: If the code contains `db = SQLAlchemy()`, you can state: "This component uses SQLAlchemy for database interaction."
            -   **Example (Forbidden)**: You CANNOT state: "This component follows a clean architecture repository pattern." unless the code explicitly uses that terminology (e.g., in comments, class names like `UserRepository`).
        **Handling Ambiguity**: If a specific architectural pattern (e.g., Microservices, Event-Sourcing) is not explicitly named in the code or its dependencies (`docker-compose.yml`, framework names), you MUST state: **"No specific high-level architectural pattern was explicitly identified in the code."** DO NOT guess or suggest a pattern based on loose interpretations.
        **Accuracy Over Completeness**: Your only metric for success is accuracy. Do not fabricate any details to make the introduction "complete" or "comprehensive." If you cannot find explicit evidence, simply state that the information is not available.

        **CRITICAL INFORMATION POLICY**:
        - ONLY include information that is explicitly present in the provided documents
        - DO NOT create, infer, or assume any information that is not directly stated
        - If you are uncertain about any detail, it is better to OMIT it rather than include potentially incorrect information
        - Base your documentation strictly on the factual content provided in the component documentation and connected components
         - DO NOT ADD ANY DATABASE OR TABLE THAT IS NOT MENTIONED IN THE CODE. DO NOT CREATE ANY NEW EXAMPLE DATABASES OR TABLES ANYWHERE.

        **ITERATIVE INTEGRATION POLICY**:
        - This is an ITERATIVE process - preserve all existing valuable information
        - DO NOT overwrite or remove important segments from existing content
        - INTEGRATE new information seamlessly with existing content
        - AVOID creating contradictory information - if there's a conflict, prioritize the most recent and specific information
        - ENHANCE and EXPAND existing sections rather than replacing them
        - Maintain consistency across all iterations
        
        **Output Requirements**:
        - Produce articulated, detailed, technical documentation
        - Use precise technical terminology for all setup procedures
        - Be comprehensive yet concise, covering all installation aspects
        - Integrate information from all important connected components as supporting context

        **Formatting Instructions:**
        - Use subheadings like `### Prerequisites` and `### Installation Steps`.
        - Use numbered lists for sequential steps.
        - **ALL** shell commands **MUST** be in code blocks (e.g., ```bash\nnpm install\n```).
        - **ALL** package names, filenames, and environment variables **MUST** be in inline code (e.g., `requests`, `.env`, `DATABASE_URL`).

        EXISTING SETUP GUIDE:
        ---
        {existing_content}
        ---

        Respond with the complete, updated markdown for the "Installation & Setup" section. Do NOT wrap the entire output in triple backticks or code blocks. Only use code blocks for actual code, not for the whole section.
    """,
    "System Architecture": """
        You are a system architect documenting the "System Architecture".
        
        **PRIMARY FOCUS**: Analyze `{component_name}` and explain its architectural role, patterns, and design principles.
        **REFERENCE CONTEXT**: Use connected components as contextual reference only: {component_context}
          **ZERO-HALLUCINATION DIRECTIVES**
        **The Rule of Evidence (Mandatory)**: For every single statement you add, you must be able to trace it back to a specific line, keyword, function name, or code block in the provided context. **If you cannot find direct, unambiguous evidence, you MUST NOT write the statement.**
        **Strict Prohibition of Inference**: You are FORBIDDEN from making logical leaps, inferring developer intent, or assuming "best practices."
            -   **Example (Allowed)**: If the code contains `db = SQLAlchemy()`, you can state: "This component uses SQLAlchemy for database interaction."
            -   **Example (Forbidden)**: You CANNOT state: "This component follows a clean architecture repository pattern." unless the code explicitly uses that terminology (e.g., in comments, class names like `UserRepository`).
        **Handling Ambiguity**: If a specific architectural pattern (e.g., Microservices, Event-Sourcing) is not explicitly named in the code or its dependencies (`docker-compose.yml`, framework names), you MUST state: **"No specific high-level architectural pattern was explicitly identified in the code."** DO NOT guess or suggest a pattern based on loose interpretations.
        **Accuracy Over Completeness**: Your only metric for success is accuracy. Do not fabricate any details to make the introduction "complete" or "comprehensive." If you cannot find explicit evidence, simply state that the information is not available.

        **CRITICAL INFORMATION POLICY**:
        - ONLY include information that is explicitly present in the provided documents
        - DO NOT create, infer, or assume any information that is not directly stated
        - If you are uncertain about any detail, it is better to OMIT it rather than include potentially incorrect information
        - Base your documentation strictly on the factual content provided in the component documentation and connected components
         - DO NOT ADD ANY DATABASE OR TABLE THAT IS NOT MENTIONED IN THE CODE. DO NOT CREATE ANY NEW EXAMPLE DATABASES OR TABLES ANYWHERE.

        **ITERATIVE INTEGRATION POLICY**:
        - This is an ITERATIVE process - preserve all existing valuable information
        - DO NOT overwrite or remove important segments from existing content
        - INTEGRATE new information seamlessly with existing content
        - AVOID creating contradictory information - if there's a conflict, prioritize the most recent and specific information
        - ENHANCE and EXPAND existing sections rather than replacing them
        - Maintain consistency across all iterations
        
        **Output Requirements**:
        - Produce articulated, detailed, technical documentation
        - Use precise architectural terminology and design patterns
        - Be comprehensive yet concise, covering all architectural aspects
        - Integrate information from all important connected components as supporting context

        **Formatting Instructions:**
        - Use subheadings (`###`) for each major component or architectural pattern.
        - Use bold (`**...**`) to emphasize key architectural terms (e.g., **Microservices**, **API Gateway**).
        - Use bullet points to describe relationships between components.
        - Use blockquotes (`> **Architectural Note:** ...`) to add rationale or important notes.

        EXISTING ARCHITECTURE DOCUMENTATION:
        ---
        {existing_content}
        ---

        Respond with the complete, updated markdown for the "System Architecture" section. Do NOT wrap the entire output in triple backticks or code blocks. Only use code blocks for actual code, not for the whole section.
    """,
    "API Documentation": """
        You are a meticulous API documentarian creating the "API Documentation".
        
        **PRIMARY FOCUS**: Analyze `{component_name}` for endpoint details, methods, parameters, request/response schemas, and API contracts.
        **REFERENCE CONTEXT**: Use connected components as contextual reference only: {component_context}
          **ZERO-HALLUCINATION DIRECTIVES**
        **The Rule of Evidence (Mandatory)**: For every single statement you add, you must be able to trace it back to a specific line, keyword, function name, or code block in the provided context. **If you cannot find direct, unambiguous evidence, you MUST NOT write the statement.**
        **Strict Prohibition of Inference**: You are FORBIDDEN from making logical leaps, inferring developer intent, or assuming "best practices."
            -   **Example (Allowed)**: If the code contains `db = SQLAlchemy()`, you can state: "This component uses SQLAlchemy for database interaction."
            -   **Example (Forbidden)**: You CANNOT state: "This component follows a clean architecture repository pattern." unless the code explicitly uses that terminology (e.g., in comments, class names like `UserRepository`).
        **Handling Ambiguity**: If a specific architectural pattern (e.g., Microservices, Event-Sourcing) is not explicitly named in the code or its dependencies (`docker-compose.yml`, framework names), you MUST state: **"No specific high-level architectural pattern was explicitly identified in the code."** DO NOT guess or suggest a pattern based on loose interpretations.
        **Accuracy Over Completeness**: Your only metric for success is accuracy. Do not fabricate any details to make the introduction "complete" or "comprehensive." If you cannot find explicit evidence, simply state that the information is not available.

        **CRITICAL INFORMATION POLICY**:
        - ONLY include information that is explicitly present in the provided documents
        - DO NOT create, infer, or assume any information that is not directly stated
        - If you are uncertain about any detail, it is better to OMIT it rather than include potentially incorrect information
        - Base your documentation strictly on the factual content provided in the component documentation and connected components
         - DO NOT ADD ANY DATABASE OR TABLE THAT IS NOT MENTIONED IN THE CODE. DO NOT CREATE ANY NEW EXAMPLE DATABASES OR TABLES ANYWHERE.

        **ITERATIVE INTEGRATION POLICY**:
        - This is an ITERATIVE process - preserve all existing valuable information
        - DO NOT overwrite or remove important segments from existing content
        - INTEGRATE new information seamlessly with existing content
        - AVOID creating contradictory information - if there's a conflict, prioritize the most recent and specific information
        - ENHANCE and EXPAND existing sections rather than replacing them
        - Maintain consistency across all iterations
        
        **Output Requirements**:
        - Produce articulated, detailed, technical documentation
        - Use precise API terminology and HTTP standards
        - Be comprehensive yet concise, covering all API aspects
        - Integrate information from all important connected components as supporting context

        **Formatting Instructions:**
        - Use a main subheading (`###`) for the component/endpoint (e.g., `### POST /api/v1/calculate`).
        - **MUST** use a Markdown table for parameters with headers: `| Parameter | Type | Description |`.
        - **MUST** use code blocks with language identifiers for examples (e.g., ```json\n{{"key": "value"}}\n```).
        - Use blockquotes (`> **Note:**`) for important implementation details.
        - Include information about connected components and their relationships.

        EXISTING API DOCUMENTATION:
        ---
        {existing_content}
        ---

        Respond with the complete, updated markdown for the "API Documentation" section. Do NOT wrap the entire output in triple backticks or code blocks. Only use code blocks for actual code, not for the whole section.
    """,
    "Code Documentation": """
        You are a senior developer documenting the codebase in the "Code Documentation" section.
        
        **PRIMARY FOCUS**: Analyze `{component_name}` for its logic, class structure, key functions, algorithms, and implementation details.
        **REFERENCE CONTEXT**: Use connected components as contextual reference only: {component_context}
          **ZERO-HALLUCINATION DIRECTIVES**
        **The Rule of Evidence (Mandatory)**: For every single statement you add, you must be able to trace it back to a specific line, keyword, function name, or code block in the provided context. **If you cannot find direct, unambiguous evidence, you MUST NOT write the statement.**
        **Strict Prohibition of Inference**: You are FORBIDDEN from making logical leaps, inferring developer intent, or assuming "best practices."
            -   **Example (Allowed)**: If the code contains `db = SQLAlchemy()`, you can state: "This component uses SQLAlchemy for database interaction."
            -   **Example (Forbidden)**: You CANNOT state: "This component follows a clean architecture repository pattern." unless the code explicitly uses that terminology (e.g., in comments, class names like `UserRepository`).
        **Handling Ambiguity**: If a specific architectural pattern (e.g., Microservices, Event-Sourcing) is not explicitly named in the code or its dependencies (`docker-compose.yml`, framework names), you MUST state: **"No specific high-level architectural pattern was explicitly identified in the code."** DO NOT guess or suggest a pattern based on loose interpretations.
        **Accuracy Over Completeness**: Your only metric for success is accuracy. Do not fabricate any details to make the introduction "complete" or "comprehensive." If you cannot find explicit evidence, simply state that the information is not available.

        **CRITICAL INFORMATION POLICY**:
        - ONLY include information that is explicitly present in the provided documents
        - DO NOT create, infer, or assume any information that is not directly stated
        - If you are uncertain about any detail, it is better to OMIT it rather than include potentially incorrect information
        - Base your documentation strictly on the factual content provided in the component documentation and connected components
         - DO NOT ADD ANY DATABASE OR TABLE THAT IS NOT MENTIONED IN THE CODE. DO NOT CREATE ANY NEW EXAMPLE DATABASES OR TABLES ANYWHERE.

        **ITERATIVE INTEGRATION POLICY**:
        - This is an ITERATIVE process - preserve all existing valuable information
        - DO NOT overwrite or remove important segments from existing content
        - INTEGRATE new information seamlessly with existing content
        - AVOID creating contradictory information - if there's a conflict, prioritize the most recent and specific information
        - ENHANCE and EXPAND existing sections rather than replacing them
        - Maintain consistency across all iterations
        
        **Output Requirements**:
        - Produce articulated, detailed, technical documentation
        - Use precise programming terminology and software engineering concepts
        - Be comprehensive yet concise, covering all code aspects
        - Integrate information from all important connected components as supporting context

        **Formatting Instructions:**
        - Use a subheading (`###`) for the component/module name (e.g., `### Module: 'stats_service.py'`).
        - For key functions, use smaller subheadings (`####`) and describe their purpose.
        - **MUST** use a Markdown table for parameters and return values.
        - **MUST** include well-commented code snippets in code blocks (e.g., ```python\n# code here\n```).

        EXISTING CODE DOCUMENTATION:
        ---
        {existing_content}
        ---

        Respond with the complete, updated markdown for the "Code Documentation" section. Do NOT wrap the entire output in triple backticks or code blocks. Only use code blocks for actual code, not for the whole section.
    """,
    "Data Architecture": """
        You are a data architect documenting the "Data Architecture".
        
        **PRIMARY FOCUS**: Analyze `{component_name}` for database interactions, schemas, data models, data flow, and storage patterns.
        **REFERENCE CONTEXT**: Use connected components as contextual reference only: {component_context}
          **ZERO-HALLUCINATION DIRECTIVES**
        **The Rule of Evidence (Mandatory)**: For every single statement you add, you must be able to trace it back to a specific line, keyword, function name, or code block in the provided context. **If you cannot find direct, unambiguous evidence, you MUST NOT write the statement.**
        **Strict Prohibition of Inference**: You are FORBIDDEN from making logical leaps, inferring developer intent, or assuming "best practices."
            -   **Example (Allowed)**: If the code contains `db = SQLAlchemy()`, you can state: "This component uses SQLAlchemy for database interaction."
            -   **Example (Forbidden)**: You CANNOT state: "This component follows a clean architecture repository pattern." unless the code explicitly uses that terminology (e.g., in comments, class names like `UserRepository`).
        **Handling Ambiguity**: If a specific architectural pattern (e.g., Microservices, Event-Sourcing) is not explicitly named in the code or its dependencies (`docker-compose.yml`, framework names), you MUST state: **"No specific high-level architectural pattern was explicitly identified in the code."** DO NOT guess or suggest a pattern based on loose interpretations.
        **Accuracy Over Completeness**: Your only metric for success is accuracy. Do not fabricate any details to make the introduction "complete" or "comprehensive." If you cannot find explicit evidence, simply state that the information is not available.

        **CRITICAL INFORMATION POLICY**:
        - ONLY include information that is explicitly present in the provided documents
        - DO NOT create, infer, or assume any information that is not directly stated
        - If you are uncertain about any detail, it is better to OMIT it rather than include potentially incorrect information
        - Base your documentation strictly on the factual content provided in the component documentation and connected components
         - DO NOT ADD ANY DATABASE OR TABLE THAT IS NOT MENTIONED IN THE CODE. DO NOT CREATE ANY NEW EXAMPLE DATABASES OR TABLES ANYWHERE.
        **ITERATIVE INTEGRATION POLICY**:
        - This is an ITERATIVE process - preserve all existing valuable information
        - DO NOT overwrite or remove important segments from existing content
        - INTEGRATE new information seamlessly with existing content
        - AVOID creating contradictory information - if there's a conflict, prioritize the most recent and specific information
        - ENHANCE and EXPAND existing sections rather than replacing them
        - Maintain consistency across all iterations
        
        **Output Requirements**:
        - Produce articulated, detailed, technical documentation
        - Use precise data architecture terminology and database concepts
        - Be comprehensive yet concise, covering all data aspects
        - Integrate information from all important connected components as supporting context

        **Formatting Instructions:**
        - Use subheadings (`###`) for different data models or database tables.
        - **MUST** use Markdown tables to describe table schemas with headers: `| Column | Type | Constraints | Description |`.
        - **MUST** use code blocks (```sql ... ```) for SQL schema definitions or important queries.

        EXISTING DATA ARCHITECTURE DOCUMENTATION:
        ---
        {existing_content}
        ---

        Respond with the complete, updated markdown for the "Data Architecture" section. Do NOT wrap the entire output in triple backticks or code blocks. Only use code blocks for actual code, not for the whole section.
    """,
    "Logical Architecture": """
        You are a software architect documenting the "Logical Architecture".
        
        **PRIMARY FOCUS**: Analyze `{component_name}` for its logical structure, component relationships, interfaces, and architectural patterns.
        **REFERENCE CONTEXT**: Use connected components as contextual reference only: {component_context}
          **ZERO-HALLUCINATION DIRECTIVES**
        **The Rule of Evidence (Mandatory)**: For every single statement you add, you must be able to trace it back to a specific line, keyword, function name, or code block in the provided context. **If you cannot find direct, unambiguous evidence, you MUST NOT write the statement.**
        **Strict Prohibition of Inference**: You are FORBIDDEN from making logical leaps, inferring developer intent, or assuming "best practices."
            -   **Example (Allowed)**: If the code contains `db = SQLAlchemy()`, you can state: "This component uses SQLAlchemy for database interaction."
            -   **Example (Forbidden)**: You CANNOT state: "This component follows a clean architecture repository pattern." unless the code explicitly uses that terminology (e.g., in comments, class names like `UserRepository`).
        **Handling Ambiguity**: If a specific architectural pattern (e.g., Microservices, Event-Sourcing) is not explicitly named in the code or its dependencies (`docker-compose.yml`, framework names), you MUST state: **"No specific high-level architectural pattern was explicitly identified in the code."** DO NOT guess or suggest a pattern based on loose interpretations.
        **Accuracy Over Completeness**: Your only metric for success is accuracy. Do not fabricate any details to make the introduction "complete" or "comprehensive." If you cannot find explicit evidence, simply state that the information is not available.

        **CRITICAL INFORMATION POLICY**:
        - ONLY include information that is explicitly present in the provided documents
        - DO NOT create, infer, or assume any information that is not directly stated
        - If you are uncertain about any detail, it is better to OMIT it rather than include potentially incorrect information
        - Base your documentation strictly on the factual content provided in the component documentation and connected components
        - DO NOT ADD ANY DATABASE OR TABLE THAT IS NOT MENTIONED IN THE CODE. DO NOT CREATE ANY NEW EXAMPLE DATABASES OR TABLES ANYWHERE.        **ITERATIVE INTEGRATION POLICY**:
        - This is an ITERATIVE process - preserve all existing valuable information
        - DO NOT overwrite or remove important segments from existing content
        - INTEGRATE new information seamlessly with existing content
        - AVOID creating contradictory information - if there's a conflict, prioritize the most recent and specific information
        - ENHANCE and EXPAND existing sections rather than replacing them
        - Maintain consistency across all iterations
        
        **Output Requirements**:
        - Produce articulated, detailed, technical documentation
        - Use precise logical architecture terminology and design patterns
        - Be comprehensive yet concise, covering all logical aspects
        - Integrate information from all important connected components as supporting context

        **Formatting Instructions:**
        - Use subheadings (`###`) for logical components and layers.
        - Use bullet points to describe component interactions and data flow.
        - Use blockquotes (`> **Design Principle:** ...`) for architectural decisions.

        EXISTING LOGICAL ARCHITECTURE DOCUMENTATION:
        ---
        {existing_content}
        ---

        Respond with the complete, updated markdown for the "Logical Architecture" section. Do NOT wrap the entire output in triple backticks or code blocks. Only use code blocks for actual code, not for the whole section.
    """,
    "Integration Guide": """
        You are an integration specialist documenting the "Integration Guide".
        
        **PRIMARY FOCUS**: Analyze `{component_name}` for integration patterns, APIs, protocols, and connectivity requirements.
        **REFERENCE CONTEXT**: Use connected components as contextual reference only: {component_context}
          **ZERO-HALLUCINATION DIRECTIVES**
        **The Rule of Evidence (Mandatory)**: For every single statement you add, you must be able to trace it back to a specific line, keyword, function name, or code block in the provided context. **If you cannot find direct, unambiguous evidence, you MUST NOT write the statement.**
        **Strict Prohibition of Inference**: You are FORBIDDEN from making logical leaps, inferring developer intent, or assuming "best practices."
            -   **Example (Allowed)**: If the code contains `db = SQLAlchemy()`, you can state: "This component uses SQLAlchemy for database interaction."
            -   **Example (Forbidden)**: You CANNOT state: "This component follows a clean architecture repository pattern." unless the code explicitly uses that terminology (e.g., in comments, class names like `UserRepository`).
        **Handling Ambiguity**: If a specific architectural pattern (e.g., Microservices, Event-Sourcing) is not explicitly named in the code or its dependencies (`docker-compose.yml`, framework names), you MUST state: **"No specific high-level architectural pattern was explicitly identified in the code."** DO NOT guess or suggest a pattern based on loose interpretations.
        **Accuracy Over Completeness**: Your only metric for success is accuracy. Do not fabricate any details to make the introduction "complete" or "comprehensive." If you cannot find explicit evidence, simply state that the information is not available.

        **CRITICAL INFORMATION POLICY**:
        - ONLY include information that is explicitly present in the provided documents
        - DO NOT create, infer, or assume any information that is not directly stated
        - If you are uncertain about any detail, it is better to OMIT it rather than include potentially incorrect information
        - Base your documentation strictly on the factual content provided in the component documentation and connected components
        - DO NOT ADD ANY DATABASE OR TABLE THAT IS NOT MENTIONED IN THE CODE. DO NOT CREATE ANY NEW EXAMPLE DATABASES OR TABLES ANYWHERE.
        **ITERATIVE INTEGRATION POLICY**:
        - This is an ITERATIVE process - preserve all existing valuable information
        - DO NOT overwrite or remove important segments from existing content
        - INTEGRATE new information seamlessly with existing content
        - AVOID creating contradictory information - if there's a conflict, prioritize the most recent and specific information
        - ENHANCE and EXPAND existing sections rather than replacing them
        - Maintain consistency across all iterations
        
        **Output Requirements**:
        - Produce articulated, detailed, technical documentation
        - Use precise integration terminology and protocol specifications
        - Be comprehensive yet concise, covering all integration aspects
        - Integrate information from all important connected components as supporting context

        **Formatting Instructions:**
        - Use subheadings (`###`) for different integration scenarios.
        - Use code blocks for configuration examples and API calls.
        - Use bullet points for step-by-step integration procedures.

        EXISTING INTEGRATION GUIDE:
        ---
        {existing_content}
        ---

        Respond with the complete, updated markdown for the "Integration Guide" section. Do NOT wrap the entire output in triple backticks or code blocks. Only use code blocks for actual code, not for the whole section.
    """,
    "Implementation View": """
        You are a technical architect documenting the "Implementation View".
        
        **PRIMARY FOCUS**: Analyze `{component_name}` for implementation details, deployment patterns, runtime behavior, and technical specifications.
        **REFERENCE CONTEXT**: Use connected components as contextual reference only: {component_context}
          **ZERO-HALLUCINATION DIRECTIVES**
        **The Rule of Evidence (Mandatory)**: For every single statement you add, you must be able to trace it back to a specific line, keyword, function name, or code block in the provided context. **If you cannot find direct, unambiguous evidence, you MUST NOT write the statement.**
        **Strict Prohibition of Inference**: You are FORBIDDEN from making logical leaps, inferring developer intent, or assuming "best practices."
            -   **Example (Allowed)**: If the code contains `db = SQLAlchemy()`, you can state: "This component uses SQLAlchemy for database interaction."
            -   **Example (Forbidden)**: You CANNOT state: "This component follows a clean architecture repository pattern." unless the code explicitly uses that terminology (e.g., in comments, class names like `UserRepository`).
        **Handling Ambiguity**: If a specific architectural pattern (e.g., Microservices, Event-Sourcing) is not explicitly named in the code or its dependencies (`docker-compose.yml`, framework names), you MUST state: **"No specific high-level architectural pattern was explicitly identified in the code."** DO NOT guess or suggest a pattern based on loose interpretations.
        **Accuracy Over Completeness**: Your only metric for success is accuracy. Do not fabricate any details to make the introduction "complete" or "comprehensive." If you cannot find explicit evidence, simply state that the information is not available.

        **CRITICAL INFORMATION POLICY**:
        - ONLY include information that is explicitly present in the provided documents
        - DO NOT create, infer, or assume any information that is not directly stated
        - If you are uncertain about any detail, it is better to OMIT it rather than include potentially incorrect information
        - Base your documentation strictly on the factual content provided in the component documentation and connected components
        - DO NOT ADD ANY DATABASE OR TABLE THAT IS NOT MENTIONED IN THE CODE. DO NOT CREATE ANY NEW EXAMPLE DATABASES OR TABLES ANYWHERE.

        **ITERATIVE INTEGRATION POLICY**:
        - This is an ITERATIVE process - preserve all existing valuable information
        - DO NOT overwrite or remove important segments from existing content
        - INTEGRATE new information seamlessly with existing content
        - AVOID creating contradictory information - if there's a conflict, prioritize the most recent and specific information
        - ENHANCE and EXPAND existing sections rather than replacing them
        - Maintain consistency across all iterations
        
        **Output Requirements**:
        - Produce articulated, detailed, technical documentation
        - Use precise implementation terminology and technical specifications
        - Be comprehensive yet concise, covering all implementation aspects
        - Integrate information from all important connected components as supporting context

        **Formatting Instructions:**
        - Use subheadings (`###`) for implementation aspects and deployment scenarios.
        - Use code blocks for configuration and deployment scripts.
        - Use tables for technical specifications and requirements.

        EXISTING IMPLEMENTATION VIEW:
        ---
        {existing_content}
        ---

        Respond with the complete, updated markdown for the "Implementation View" section. Do NOT wrap the entire output in triple backticks or code blocks. Only use code blocks for actual code, not for the whole section.
    """,
    "Database Schemas": """
       
    You are a technical writer whose task is to document any explicit data schemas found in the provided code.

    PRIMARY FOCUS: Analyze {component_name} to identify and document data schemas, structures, and constraints.
    REFERENCE CONTEXT: Use connected components as contextual reference only: {component_context}

    EXECUTION RULES & ANTI-HALLUCINATION POLICY:

    Core Directive: Your single most important rule is to never invent, infer, or assume information. Your entire output must be based strictly and literally on the provided source code.

    Definition of a "Data Schema": A schema is considered "defined" if you find any of the following patterns that explicitly structure data:

    Relational Databases: SQL CREATE TABLE statements, ORM model classes, or Python data structures used to create tables (e.g., via pandas.to_sql).

    APIs & Validation: Models that define the structure of API bodies or other data objects (e.g., Pydantic, Marshmallow).

    File Formats: Hardcoded column headers or schema definitions for structured files (e.g., CSV, Parquet).

    Document Databases: Models or dictionaries defining the structure of a NoSQL document.

    Conditional Logic (Strictly Enforced):

    IF you find one or more data schemas matching the criteria above, you MUST document them according to the output requirements.

    ELSE (if no data schemas are found), your entire response for this section MUST be only the following text: No explicit data schemas were found in the provided code.

    OUTPUT REQUIREMENTS:

    Produce articulated, detailed, and factual technical documentation based only on the source files.

    For each schema identified, you must state the source file or class where it was defined.

    Be comprehensive yet concise, covering all specified aspects of the found schemas.

    FORMATTING INSTRUCTIONS:

    Use subheadings (###) for different schemas or groups.

    MUST use Markdown tables for schema definitions with the headers: | Field / Column | Type | Notes / Constraints |.

    Use code blocks (sql ... ) for any explicit DDL statements found.

    EXISTING CONTENT TO UPDATE:
    {existing_content}
    Respond with the complete, updated markdown for the documentation. Do NOT wrap the entire output in triple backticks or code blocks. Only use code blocks for actual code, not for the whole section.
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
    connected_nodes: List[Dict]  # New field for connected nodes information
    # --- NEW: Architectural diagram fields ---
    architectural_components: Dict[str, Dict]  # Store component info for diagram
    architectural_relationships: List[Dict]  # Store relationships between components
    diagram_mermaid_code: str  # Current mermaid diagram code
    diagram_description: str  # Natural language description of architecture


# --- Helper Functions for Incremental Saving ---

# --- Sanitize filenames for Windows compatibility ---
def sanitize_filename(name: str) -> str:
    """Replace invalid filename characters with underscores."""
    return re.sub(r'[:\\/*?"<>|]', '_', name)

def save_incremental_progress(state: DocumentationState, operation: str):
    """Save incremental progress after each major operation."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    current_component = state.get("current_component_name", "unknown")
    safe_component = sanitize_filename(str(current_component))
    safe_operation = sanitize_filename(str(operation))
    # Create filename with timestamp and operation, sanitized
    filename = f"{timestamp}_{safe_operation}_{safe_component}.json"
    filepath = os.path.join(INCREMENTAL_SAVE_DIR, filename)
    
    # Create a serializable version of the state
    serializable_state = {
        "timestamp": timestamp,
        "operation": operation,
        "current_component_name": state.get("current_component_name"),
        "processed_components": len(state.get("all_data", {})) - len(state.get("unprocessed_components", [])),
        "total_components": len(state.get("all_data", {})),
        "target_sections": state.get("target_sections", []),
        "document_content": state.get("document_content", {}),
        "connected_nodes_count": len(state.get("connected_nodes", [])),
        "scrapper_decision": state.get("scrapper_decision", ""),
        # Add architectural data to incremental saves
        "architectural_components_count": len(state.get("architectural_components", {})),
        "architectural_relationships_count": len(state.get("architectural_relationships", [])),
        "diagram_mermaid_lines": len(state.get("diagram_mermaid_code", "").split('\n')),
        "diagram_description_length": len(state.get("diagram_description", ""))
    }
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(serializable_state, f, indent=2, ensure_ascii=False)
        logger.info(f" Incremental progress saved: {filepath}")
    except Exception as e:
        logger.error(f" Failed to save incremental progress: {e}")



def save_section_content(component_name: str, section_name: str, content: str):
    """Save individual section content after each LLM call."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_component = sanitize_filename(str(component_name))
    safe_section = sanitize_filename(str(section_name.replace(' ', '_')))
    # Create section-specific directory (sanitized)
    section_dir = os.path.join(INCREMENTAL_SAVE_DIR, "sections", safe_component)
    os.makedirs(section_dir, exist_ok=True)
    # Save section content (sanitized)
    filename = f"{timestamp}_{safe_section}.md"
    filepath = os.path.join(section_dir, filename)
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# {section_name}\n\n")
            f.write(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
            f.write(f"*Component: {component_name}*\n\n")
            f.write("---\n\n")
            f.write(content)
        logger.info(f" Section content saved: {filepath}")
    except Exception as e:
        logger.error(f" Failed to save section content: {e}")

def save_llm_interaction(component_name: str, interaction_type: str, prompt: str, response: str, metadata: dict = None):
    """Save detailed LLM interaction for debugging and analysis."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_component = sanitize_filename(str(component_name))
    safe_interaction = sanitize_filename(str(interaction_type))
    
    # Create LLM-specific directory
    llm_dir = os.path.join(INCREMENTAL_SAVE_DIR, "llm_interactions", safe_component)
    os.makedirs(llm_dir, exist_ok=True)
    
    # Create detailed interaction record
    interaction_record = {
        "timestamp": timestamp,
        "component": component_name,
        "interaction_type": interaction_type,
        "metadata": metadata or {},
        "prompt": prompt,
        "response": response,
        "response_length": len(response),
        "prompt_length": len(prompt)
    }
    
    filename = f"{timestamp}_{safe_interaction}.json"
    filepath = os.path.join(llm_dir, filename)
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(interaction_record, f, indent=2, ensure_ascii=False)
        logger.info(f" LLM interaction saved: {filepath}")
    except Exception as e:
        logger.error(f" Failed to save LLM interaction: {e}")

def log_processing_summary():
    """Log a comprehensive summary of all saved files and processing stats."""
    logger.info(" PROCESSING SUMMARY:")
    
    # Count files in incremental saves
    if os.path.exists(INCREMENTAL_SAVE_DIR):
        total_files = 0
        
        # Count main progress files
        progress_files = [f for f in os.listdir(INCREMENTAL_SAVE_DIR) if f.endswith('.json')]
        total_files += len(progress_files)
        logger.info(f" Progress files: {len(progress_files)}")
        
        # Count section files
        sections_dir = os.path.join(INCREMENTAL_SAVE_DIR, "sections")
        if os.path.exists(sections_dir):
            section_count = 0
            for component_dir in os.listdir(sections_dir):
                comp_path = os.path.join(sections_dir, component_dir)
                if os.path.isdir(comp_path):
                    section_files = [f for f in os.listdir(comp_path) if f.endswith('.md')]
                    section_count += len(section_files)
            total_files += section_count
            logger.info(f" Section files: {section_count}")
        
        # Count architectural files
        arch_dir = os.path.join(INCREMENTAL_SAVE_DIR, "architecture")
        if os.path.exists(arch_dir):
            arch_files = [f for f in os.listdir(arch_dir) if f.endswith('.json')]
            total_files += len(arch_files)
            logger.info(f" Architectural files: {len(arch_files)}")
        
        # Count LLM interaction files
        llm_dir = os.path.join(INCREMENTAL_SAVE_DIR, "llm_interactions")
        if os.path.exists(llm_dir):
            llm_count = 0
            for component_dir in os.listdir(llm_dir):
                comp_path = os.path.join(llm_dir, component_dir)
                if os.path.isdir(comp_path):
                    llm_files = [f for f in os.listdir(comp_path) if f.endswith('.json')]
                    llm_count += len(llm_files)
            total_files += llm_count
            logger.info(f" LLM interaction files: {llm_count}")
        
        logger.info(f" TOTAL INTERIM FILES SAVED: {total_files}")
        logger.info(f" All files saved in: {INCREMENTAL_SAVE_DIR}")
    else:
        logger.warning(f" Incremental save directory not found: {INCREMENTAL_SAVE_DIR}")


def find_strategic_files(repo_path: str) -> List[str]:
    """
    Scans the repository and returns a list of architecturally significant files.
    """
    strategic_files = []
    
    # Define files and patterns to look for
    exact_matches = [
        'docker-compose.yml', 'Dockerfile', 'requirements.txt', 
        'pyproject.toml', 'package.json'
    ]
    extension_matches = ['.tf'] # For Terraform
    
    logger.info(f" Searching for strategic files in '{repo_path}'...")
    for root, dirs, files in os.walk(repo_path):
        # Exclude common non-source directories
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules', 'venv']]
        
        for file in files:
            file_path = os.path.join(root, file)
            
            if file in exact_matches:
                strategic_files.append(file_path)
                continue

            if any(file.endswith(ext) for ext in extension_matches):
                strategic_files.append(file_path)
                continue

            if file.endswith('.py'):
                # Prioritize key files that define structure and entrypoints
                if file in ['main.py', 'app.py', 'settings.py', 'config.py', 'server.py', 'function_app.py']:
                    strategic_files.append(file_path)
                elif any(keyword in root for keyword in ['models', 'schemas', 'routers', 'controllers', 'api']):
                    strategic_files.append(file_path)

    logger.info(f" Found {len(strategic_files)} strategic files for analysis.")
    return strategic_files


def analyze_files_to_data(file_paths: List[str], repo_root: str) -> Dict[str, Any]:
    """
    Analyzes the content of strategic files to create a low-level data dictionary.
    """
    logger.info("  Extracting content from strategic files...")
    analyzed_data = {}
    for file_path in file_paths:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                relative_path = os.path.relpath(file_path, repo_root)
                analyzed_data[relative_path] = {
                    "content": f.read(),
                    "path": relative_path,
                }
        except Exception as e:
            logger.warning(f"Could not read file {file_path}: {e}")
            continue
    return analyzed_data


def synthesize_architecture_model(analyzed_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Uses a two-step AI agent process to create a high-level conceptual architecture model.
    Step 1: Identify components.
    Step 2: Map relationships between them.
    """
    logger.info(" Starting advanced two-step architecture synthesis...")

    # Prepare a consolidated text block of all strategic file contents
    condensed_context = ""
    for path, data in analyzed_data.items():
        condensed_context += f"--- FILE: {path} ---\n{data['content']}\n\n"

    # --- Step 1: Identify Components ---
    logger.info(" Step 1: Identifying high-level components...")
    component_prompt = ChatPromptTemplate.from_template(
        """
        You are an expert System Architect. Your first task is to identify the primary, high-level components from the provided source code.
        Analyze the file contents and list all logical components. A component could be a user-facing API, a backend service, a data processing worker, or a database.

        Think step-by-step:
        1.  Scan for entrypoints like `main.py` or `app.py` to find APIs.
        2.  Look for files in `services`, `workers`, or `tasks` folders to identify backend services.
        3.  Identify database models or connection strings to find data stores.
        4.  Look at `Dockerfile` or `docker-compose.yml` to see how services are containerized.

        Based on your analysis, provide a JSON list of these components with a unique `id`, a clear `label`, a `type` (API, Service, Worker, Database), and a `group` (e.g., 'API Layer', 'Backend Services', 'Data Tier').

        SOURCE CODE CONTEXT:
        ---
        {context}
        ---

        Respond with a JSON object containing a single key "components" like this:
        {{
            "components": [
                {{
                    "id": "api_gateway",
                    "label": "API Gateway",
                    "type": "API",
                    "group": "API Layer"
                }},
                {{
                    "id": "user_service",
                    "label": "User Service",
                    "type": "Service",
                    "group": "Backend Services"
                }}
            ]
        }}
        """
    )
    
    component_chain = component_prompt | llm | JsonOutputParser()
    try:
        component_result = component_chain.invoke({"context": condensed_context})
        components = component_result.get("components", [])
        if not components:
            logger.error("AI failed to identify any components.")
            return {}
        logger.info(f" Identified {len(components)} components.")
    except Exception as e:
        logger.error(f" AI component identification failed: {e}")
        return {}

    # --- Step 2: Map Relationships ---
    logger.info(" Step 2: Mapping relationships between components...")
    relationship_prompt = ChatPromptTemplate.from_template(
        """
        You are an expert System Architect. You have been given a list of identified system components and the full source code context.
        Your second task is to determine the relationships and data flow between these components.

        Think step-by-step for each component:
        1.  Read the code associated with the component.
        2.  Identify function calls, API requests, or database queries it makes to OTHER components in the list.
        3.  For each interaction, describe it with a concise label (e.g., "Sends validation request to", "Fetches user data from", "Pushes job to").

        SOURCE CODE CONTEXT:
        ---
        {context}
        ---

        IDENTIFIED COMPONENTS:
        ---
        {components}
        ---

        Based on the source code, map the connections between the components. Respond with a JSON object containing a single key "relationships".
        {{
            "relationships": [
                {{
                    "from": "source_component_id",
                    "to": "target_component_id",
                    "label": "Description of the interaction"
                }}
            ]
        }}
        """
    )

    relationship_chain = relationship_prompt | llm | JsonOutputParser()
    try:
        relationship_result = relationship_chain.invoke({
            "context": condensed_context,
            "components": json.dumps(components, indent=2)
        })
        relationships = relationship_result.get("relationships", [])
        logger.info(f" Mapped {len(relationships)} relationships.")
    except Exception as e:
        logger.error(f" AI relationship mapping failed: {e}")
        relationships = []

    return {"components": components, "relationships": relationships}


def generate_diagram(model: Dict[str, Any], output_filename: str):
    """
    Generates and saves a professional architecture diagram from the high-level model.
    """
    logger.info(f" Generating diagram at {output_filename}.png...")
    
    components = model.get("components", [])
    relationships = model.get("relationships", [])

    if not components:
        logger.warning("No components in the model. Cannot generate diagram.")
        return

    icon_map = {
        "API": APIManagement,
        "Service": AppServices,
        "Worker": FunctionApps,
        "Database": SQLDatabases,
        "DEFAULT": Python
    }

    with Diagram("System Architecture (Azure)", filename=output_filename, show=False, direction="TB"):
        nodes = {}
        grouped_nodes = {}

        for comp_info in components:
            group = comp_info.get("group", "Default Group")
            if group not in grouped_nodes:
                grouped_nodes[group] = []
            grouped_nodes[group].append(comp_info)
        
        for group_name, component_list in grouped_nodes.items():
            with Cluster(group_name):
                for comp_info in component_list:
                    node_id = comp_info.get("id")
                    node_label = comp_info.get("label")
                    node_type = comp_info.get("type", "DEFAULT")
                    
                    Icon = icon_map.get(node_type, icon_map["DEFAULT"])
                    nodes[node_id] = Icon(node_label)

        for rel in relationships:
            from_node = rel.get("from")
            to_node = rel.get("to")
            rel_label = rel.get("label", "")
            
            if from_node in nodes and to_node in nodes:
                nodes[from_node] >> Edge(label=rel_label) >> nodes[to_node]
    
    logger.info(" Diagram generated successfully.")


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
        print(f" Error loading data: {e}")
        return {}

def component_loader_node(state: DocumentationState) -> DocumentationState:
    """Pops the next component and loads its data including connected nodes into the state."""
    if not state["unprocessed_components"]:
        logger.info(" Node: component_loader | Status: completed | No more components to process")
        print("--- Component Loader: All components processed ---")
        return state
    
    component_name = state["unprocessed_components"].pop(0)
    remaining = len(state["unprocessed_components"])
    total_components = len(state["all_data"])
    current_idx = total_components - remaining
    
    # Enhanced logging with node status
    logger.info(f" Node: component_loader | Status: started | Component: '{component_name}'")
    logger.info(f" Loading component: '{component_name}' ({remaining} remaining - {current_idx}/{total_components})")
    print(f"\n--- Component Loader: Loading component '{component_name}' ({current_idx}/{total_components}) ---")
    
    # Update progress bar with detailed information
    global progress_bar
    if progress_bar and threading.current_thread() is threading.main_thread():
        # Set the current position correctly
        progress_bar.n = current_idx - 1
        remaining_count = total_components - current_idx
        percentage = (current_idx / total_components) * 100
        
        # Update description with file details
        progress_bar.set_description(f" {component_name} | {remaining_count} left")
        
        # Update by 1 and refresh
        progress_bar.update(1)
        progress_bar.refresh()
        
        # Log progress without emojis to avoid interference
        print(f"Progress: {current_idx}/{total_components} ({percentage:.1f}%) - Processing: {component_name}")
    
    state["current_component_name"] = component_name
    component_data = state["all_data"][component_name]
    state["current_component_doc"] = component_data["documentation"]
    
    # Log component details
    doc_length = len(state["current_component_doc"].split()) if state["current_component_doc"] else 0
    logger.info(f" Component details | Name: '{component_name}' | Document length: {doc_length} words")
    print(f"    - Document length: {doc_length} words")
    print(f"    - Component type: {component_data.get('type', 'Unknown')}")
    
    # Set simple context without connected nodes
    state["current_component_context"] = f"Processing component: {component_name}"
    
    # Store empty connected nodes info
    state["connected_nodes"] = []
    
    # Save incremental progress
    save_incremental_progress(state, "component_loaded")
    
    logger.info(f" Node: component_loader | Status: completed | Component: '{component_name}' loaded successfully")
    print(f"--- Component Loader: Component '{component_name}' loaded successfully ---")
    return state

def scrapper_node(state: DocumentationState) -> dict:
    """Enhanced scrapper that filters out trivial components more effectively."""
    component_name = state['current_component_name']
    component_doc = state['current_component_doc']
    
    logger.info(f"� Node: scrapper | Status: started | Component: '{component_name}'")
    logger.info(f"� Enhanced Scrapper: Analyzing component '{component_name}'")
    print(f"--- Enhanced Scrapper: Analyzing '{component_name}' ---")
    
    # Pre-filter checks based on component name patterns
    trivial_patterns = [
        r'__init__\.py$',
        r'import[s]?_',
        r'_import[s]?',
        r'^[A-Z_]+$',  # Constants like API_V1_STR, APP_NAME
        r'\.py$'  # Simple module references
    ]
    
    # Check if component name matches trivial patterns
    for pattern in trivial_patterns:
        if re.search(pattern, component_name, re.IGNORECASE):
            logger.info(f" Scrapper Decision: REJECT | Reason: matches trivial pattern '{pattern}' | Component: '{component_name}'")
            logger.info(f" Pre-filter Decision: SCRAP (matches trivial pattern: {pattern})")
            print(f"--- Enhanced Scrapper: Decision is to REJECT (trivial pattern: {pattern}). ---")
            save_incremental_progress(state, "scrapper_scrap")
            return {"scrapper_decision": "scrap"}
    
    # Word count check
    doc_length = len(component_doc.split())
    logger.info(f" Document analysis | Component: '{component_name}' | Length: {doc_length} words")
    print(f"    - Analyzing document length: {doc_length} words")
    
    if doc_length < 15:  # Increased threshold
        logger.info(f" Scrapper Decision: REJECT | Reason: document too short ({doc_length} words) | Component: '{component_name}'")
        logger.info(f" Decision: SCRAP (document too short: {doc_length} words)")
        print(f"--- Enhanced Scrapper: Decision is to REJECT (too short: {doc_length} words). ---")
        save_incremental_progress(state, "scrapper_scrap")
        return {"scrapper_decision": "scrap"}
    
    # Content-based filtering
    doc_lower = component_doc.lower()
    
    # Check for import-only content
    lines = [line.strip() for line in component_doc.split('\n') if line.strip()]
    non_trivial_lines = []
    
    logger.info(f" Content analysis | Component: '{component_name}' | Total lines: {len(lines)}")
    print(f"    - Analyzing content structure: {len(lines)} total lines")
    
    for line in lines:
        line_lower = line.lower()
        # Skip trivial lines
        if any(trivial in line_lower for trivial in [
            'import ', 'from ', '__init__', 'pass', '"""', "'''",
            'coding:', 'encoding:', '#', 'type: ignore'
        ]):
            continue
        # Skip simple assignments without logic
        if re.match(r'^\s*\w+\s*=\s*["\'\w\.\[\]]+\s*$', line):
            continue
        non_trivial_lines.append(line)
    
    logger.info(f" Content structure | Component: '{component_name}' | Non-trivial lines: {len(non_trivial_lines)}")
    print(f"    - Non-trivial lines found: {len(non_trivial_lines)}")
    
    # If less than 3 non-trivial lines, it's probably not substantial
    if len(non_trivial_lines) < 3:
        logger.info(f" Scrapper Decision: REJECT | Reason: insufficient non-trivial content ({len(non_trivial_lines)} lines) | Component: '{component_name}'")
        logger.info(f" Decision: SCRAP (insufficient non-trivial content: {len(non_trivial_lines)} lines)")
        print(f"--- Enhanced Scrapper: Decision is to REJECT (insufficient content: {len(non_trivial_lines)} lines). ---")
        save_incremental_progress(state, "scrapper_scrap")
        return {"scrapper_decision": "scrap"}
    
    # Check for specific trivial content indicators
    trivial_indicators = [
        'this module contains only imports',
        'simple import statement',
        'constant definition',
        'variable declaration',
        'basic configuration',
        'empty module',
        'placeholder'
    ]
    
    trivial_found = [indicator for indicator in trivial_indicators if indicator in doc_lower]
    if trivial_found:
        logger.info(f" Scrapper Decision: REJECT | Reason: contains trivial indicators {trivial_found} | Component: '{component_name}'")
        logger.info(f" Decision: SCRAP (contains trivial indicators)")
        print(f"--- Enhanced Scrapper: Decision is to REJECT (trivial indicators: {trivial_found}). ---")
        save_incremental_progress(state, "scrapper_scrap")
        return {"scrapper_decision": "scrap"}
    
    # Check for substantial content indicators
    substantial_indicators = [
        'class ', 'def ', 'function', 'method', 'algorithm', 'logic',
        'implementation', 'process', 'handle', 'manage', 'calculate',
        'validate', 'parse', 'transform', 'route', 'endpoint',
        'service', 'controller', 'model', 'schema', 'exception',
        'error handling', 'business logic', 'data processing'
    ]
    
    substantial_count = sum(1 for indicator in substantial_indicators if indicator in doc_lower)
    substantial_found = [indicator for indicator in substantial_indicators if indicator in doc_lower]
    
    logger.info(f" Substantial content analysis | Component: '{component_name}' | Indicators found: {substantial_count} | Types: {substantial_found[:5]}")
    print(f"    - Substantial content indicators: {substantial_count} found")
    
    # If it has multiple substantial indicators, likely proceed
    if substantial_count >= 2:
        logger.info(f" Scrapper Decision: ACCEPT | Reason: substantial indicators ({substantial_count}) | Component: '{component_name}'")
        logger.info(f" Pre-approval: PROCEED (substantial indicators: {substantial_count})")
        print(f"--- Enhanced Scrapper: Decision is to ACCEPT (substantial content: {substantial_count} indicators). ---")
        save_incremental_progress(state, "scrapper_proceed")
        return {"scrapper_decision": "proceed"}
    
    # For borderline cases, use LLM with enhanced prompt
    logger.info(f" Scrapper LLM consultation | Component: '{component_name}' | Reason: borderline case")
    logger.info(f" Borderline case - consulting enhanced LLM for '{component_name}'")
    print(f"    - Borderline case: consulting LLM for final decision")
    
    enhanced_prompt = ChatPromptTemplate.from_template(
        """You are an expert code analyst tasked with determining if a component's documentation is substantial enough to include in technical documentation.

Component Name: `{component_name}`
Documentation: 
---
{component_doc}
---

CRITERIA FOR SUBSTANTIAL CONTENT:
- Contains actual business logic, algorithms, or meaningful functionality
- Describes classes, functions, methods with implementation details
- Explains API endpoints, services, or data processing
- Documents configuration, schemas, or architectural components
- Provides error handling, validation, or complex operations

CRITERIA FOR TRIVIAL CONTENT (should be SCRAPPED):
- Only import statements or module references
- Simple variable/constant declarations
- Empty modules or placeholder files
- Basic __init__.py files without logic
- Single-line configurations or aliases
- Documentation that just lists imports or basic assignments

ANALYSIS FACTORS:
1. Code complexity and functionality depth
2. Business value and technical significance  
3. Documentation detail and implementation insights
4. Architectural or design relevance

Respond with exactly one word: "Proceed" if the content is substantial and valuable for technical documentation, or "Scrap" if it's trivial and not worth including.

Decision:"""
    )
    
    chain = enhanced_prompt | llm | StrOutputParser()
    
    try:
        logger.info(f" LLM call initiated | Component: '{component_name}' | Type: enhanced_scrapper")
        llm_decision = llm.invoke({
            "component_name": component_name, 
            "component_doc": component_doc
        })
        
        logger.info(f" LLM response received | Component: '{component_name}' | Decision: '{llm_decision.strip()}'")
        
        # Save LLM interaction for debugging
        save_llm_interaction(
            component_name, 
            "enhanced_scrapper",
            f"Component: {component_name}\nDoc: {component_doc[:500]}...",
            llm_decision,
            {"doc_length": len(component_doc), "substantial_count": substantial_count}
        )
        
        decision_clean = llm_decision.strip().lower()
        
        if "scrap" in decision_clean:
            logger.info(f" Scrapper Decision: REJECT | Reason: LLM decision ('{llm_decision.strip()}') | Component: '{component_name}'")
            logger.info(f" Enhanced LLM Decision: SCRAP for '{component_name}'")
            print(f"--- Enhanced Scrapper: Decision is to REJECT (LLM decision). ---")
            save_incremental_progress(state, "scrapper_scrap")
            return {"scrapper_decision": "scrap"}
        else:
            logger.info(f" Scrapper Decision: ACCEPT | Reason: LLM decision ('{llm_decision.strip()}') | Component: '{component_name}'")
            logger.info(f" Enhanced LLM Decision: PROCEED for '{component_name}'")
            print(f"--- Enhanced Scrapper: Decision is to ACCEPT (LLM decision). ---")
            save_incremental_progress(state, "scrapper_proceed")
            return {"scrapper_decision": "proceed"}
            
    except Exception as e:
        logger.error(f" LLM error | Component: '{component_name}' | Error: {e}")
        logger.error(f" LLM error for '{component_name}': {e}")
        # Default to proceed on error to avoid losing potentially valuable content
        logger.info(f" Scrapper Decision: ACCEPT (default) | Reason: LLM error fallback | Component: '{component_name}'")
        logger.info(f" Defaulting to PROCEED due to LLM error")
        print(f"--- Enhanced Scrapper: Defaulting to ACCEPT (LLM error). ---")
        save_incremental_progress(state, "scrapper_proceed")
        return {"scrapper_decision": "proceed"}

def selector_node(state: DocumentationState) -> DocumentationState:
    """Selects which documentation sections are relevant for the current component and its connections."""
    component_name = state['current_component_name']
    
    logger.info(f" Node: selector | Status: started | Component: '{component_name}'")
    logger.info(f" Selector: Choosing sections for '{component_name}'")
    print(f"--- Selector: Choosing sections for '{component_name}' ---")
    
    # Include connected nodes information in the selection process
    connected_nodes_summary = ""
    if state.get("connected_nodes"):
        connected_nodes_summary = f"\n\nConnected Components:\n"
        for node in state["connected_nodes"]:
            connected_nodes_summary += f"- {node['name']} ({node['type']}): {node['summary']}\n"
        logger.info(f" Connected components | Component: '{component_name}' | Count: {len(state['connected_nodes'])}")
        print(f"    - Found {len(state['connected_nodes'])} connected components")
    else:
        logger.info(f" Connected components | Component: '{component_name}' | Count: 0")
        print(f"    - No connected components found")
    
    logger.info(f" LLM call initiated | Component: '{component_name}' | Type: section_selector")
    logger.info(f" Consulting LLM for section selection for '{component_name}'")
    print(f"    - Consulting LLM for section selection")
    
    prompt = ChatPromptTemplate.from_template(
        """You are a document routing expert. Based on the documentation for component `{component_name}` and its connected components, select ALL sections where this information would be relevant.
        
        Component Documentation: --- {component_doc} ---
        {connected_nodes_summary}
        Available Sections: {sections}
        
        Consider the relationships and dependencies when selecting sections. For example:
        - If connected to API endpoints, include "API Documentation"
        - If connected to database operations, include "Data Architecture"
        - If connected to error handling, include "Error Handling"
        
        Respond with a JSON object containing a single key "relevant_sections" which is a list of strings from the available sections.
        Example: {{"relevant_sections": ["API Documentation", "Error Handling"]}}"""
    )
    
    section_list_str = "\n".join([f"- {s}" for s in ALL_SECTIONS])
    chain = prompt | llm | JsonOutputParser()
    
    try:
        response = chain.invoke({
            "component_name": component_name, 
            "component_doc": state["current_component_doc"], 
            "connected_nodes_summary": connected_nodes_summary,
            "sections": section_list_str
        })
        
        logger.info(f" LLM response received | Component: '{component_name}' | Sections selected: {len(response.get('relevant_sections', []))}")
        
        # Save LLM interaction for section selection
        save_llm_interaction(
            component_name,
            "section_selector",
            f"Component: {component_name}\nSections: {section_list_str[:300]}...",
            str(response),
            {"available_sections": len(ALL_SECTIONS), "connected_nodes": len(state.get("connected_nodes", []))}
        )
        
        relevant_sections = response.get("relevant_sections", [])
        state["target_sections"] = [s for s in relevant_sections if s in ALL_SECTIONS]
        
        logger.info(f" Section selection | Component: '{component_name}' | Selected: {len(state['target_sections'])} sections")
        logger.info(f" Selected sections | Component: '{component_name}' | Sections: {state['target_sections']}")
        logger.info(f" Selected {len(state['target_sections'])} sections for '{component_name}': {state['target_sections']}")
        print(f"--- Selector: Chosen sections ({len(state['target_sections'])}): {state['target_sections']} ---")
        
        # Log each section selection decision
        for section in state['target_sections']:
            print(f"    - Selected: {section}")
        
    except Exception as e:
        logger.error(f" Section selection failed | Component: '{component_name}' | Error: {e}")
        # Fallback to default sections
        state["target_sections"] = ["Project Introduction", "Code Documentation"]
        logger.info(f" Fallback selection | Component: '{component_name}' | Using default sections: {state['target_sections']}")
        print(f"    - Using fallback sections due to error: {state['target_sections']}")
    
    # Save incremental progress
    save_incremental_progress(state, "sections_selected")
    
    logger.info(f" Node: selector | Status: completed | Component: '{component_name}' | Sections: {len(state['target_sections'])}")
    
    return state

async def architectural_diagram_node(state: DocumentationState) -> DocumentationState:
    """Analyzes components and updates the architectural diagram in parallel with documentation writers."""
    component_name = state['current_component_name']
    component_doc = state['current_component_doc']
    
    logger.info(f" Node: architectural_diagram | Status: started | Component: '{component_name}'")
    logger.info(f" Architectural Analyzer: Processing '{component_name}'")
    print(f"--- Architectural Analyzer: Analyzing '{component_name}' ---")
    
    # Initialize architectural data if not present
    if not state.get("architectural_components"):
        state["architectural_components"] = {}
        logger.info(" Initialized architectural components storage")
    if not state.get("architectural_relationships"):
        state["architectural_relationships"] = []
        logger.info(" Initialized architectural relationships storage")
    if not state.get("diagram_mermaid_code"):
        state["diagram_mermaid_code"] = "graph TD\n"
        logger.info(" Initialized mermaid diagram code")
    if not state.get("diagram_description"):
        state["diagram_description"] = "## System Architecture Overview\n\nThis diagram represents the architectural components and their relationships:\n\n"
        logger.info(" Initialized diagram description")
    
    # Log current architectural state
    existing_components = len(state["architectural_components"])
    existing_relationships = len(state["architectural_relationships"])
    logger.info(f" Current architectural state | Components: {existing_components} | Relationships: {existing_relationships}")
    print(f"    - Current state: {existing_components} components, {existing_relationships} relationships")
    
    # Create architectural analysis prompt
    architectural_prompt = ChatPromptTemplate.from_template(
        """You are a software architect analyzing components for architectural diagram generation.

Component Name: `{component_name}`
Component Documentation:
---
{component_doc}
---

Existing Architectural Components: {existing_components}
Existing Relationships: {existing_relationships}

TASK: Analyze this component and extract architectural information.

EXTRACT THE FOLLOWING:
1. Component Type: (e.g., "API_ENDPOINT", "SERVICE", "DATABASE", "CONTROLLER", "MODEL", "UTILITY", "CONFIG", "MIDDLEWARE")
2. Component Layer: (e.g., "PRESENTATION", "BUSINESS", "DATA", "INFRASTRUCTURE", "EXTERNAL")
3. Key Responsibilities: Brief description of what this component does
4. Dependencies: What other components this one depends on
5. Dependents: What components depend on this one
6. Data Flow: How data flows through this component

Respond with a JSON object containing:
{{
    "component_info": {{
        "name": "{component_name}",
        "type": "COMPONENT_TYPE",
        "layer": "LAYER_NAME", 
        "responsibilities": "Brief description",
        "has_substantial_logic": true/false
    }},
    "relationships": [
        {{
            "from": "source_component",
            "to": "target_component", 
            "type": "DEPENDS_ON|CALLS|INHERITS|IMPLEMENTS|CONFIGURES",
            "description": "Brief description of relationship"
        }}
    ],
    "mermaid_update": "Any new mermaid diagram lines to add for this component"
}}

Focus on architectural significance. Only include substantial components and meaningful relationships."""
    )
    
    chain = architectural_prompt | llm | JsonOutputParser()
    
    try:
        logger.info(f" LLM call initiated | Component: '{component_name}' | Type: architectural_analyzer")
        
        # Get architectural analysis
        analysis = await chain.ainvoke({
            "component_name": component_name,
            "component_doc": component_doc,
            "existing_components": list(state["architectural_components"].keys()),
            "existing_relationships": [f"{r['from']} -> {r['to']}" for r in state["architectural_relationships"]]
        })
        
        logger.info(f" LLM response received | Component: '{component_name}' | Analysis completed")
        
        # Save LLM interaction for architectural analysis
        save_llm_interaction(
            component_name,
            "architectural_analyzer",
            f"Component: {component_name}\nDoc: {component_doc[:500]}...",
            str(analysis),
            {
                "existing_components_count": len(state["architectural_components"]),
                "existing_relationships_count": len(state["architectural_relationships"])
            }
        )
        
        # Update architectural components
        if analysis.get("component_info") and analysis["component_info"].get("has_substantial_logic"):
            component_info = analysis["component_info"]
            state["architectural_components"][component_name] = component_info
            comp_type = component_info.get('type', 'UNKNOWN')
            comp_layer = component_info.get('layer', 'UNKNOWN')
            logger.info(f" Architectural component added | Component: '{component_name}' | Type: {comp_type} | Layer: {comp_layer}")
            logger.info(f" Added architectural component: {component_name} ({comp_type})")
            print(f"    - Added component: {component_name} ({comp_type})")
        else:
            logger.info(f" Component not substantial enough for architecture | Component: '{component_name}'")
            print(f"    - Component not added (insufficient architectural significance)")
        
        # Update relationships
        new_relationships = 0
        if analysis.get("relationships"):
            for relationship in analysis["relationships"]:
                # Avoid duplicate relationships
                relationship_key = f"{relationship['from']}-{relationship['to']}-{relationship['type']}"
                existing_keys = [f"{r['from']}-{r['to']}-{r['type']}" for r in state["architectural_relationships"]]
                if relationship_key not in existing_keys:
                    state["architectural_relationships"].append(relationship)
                    new_relationships += 1
                    logger.info(f" Relationship added | From: '{relationship['from']}' | To: '{relationship['to']}' | Type: {relationship['type']}")
                    logger.info(f" Added relationship: {relationship['from']} -> {relationship['to']}")
                    print(f"    - Added relationship: {relationship['from']} -> {relationship['to']}")
        
        if new_relationships == 0:
            logger.info(f" No new relationships found | Component: '{component_name}'")
            print(f"    - No new relationships identified")
        
        # Update mermaid diagram
        if analysis.get("mermaid_update"):
            state["diagram_mermaid_code"] += f"    {analysis['mermaid_update']}\n"
            logger.info(f" Mermaid diagram updated | Component: '{component_name}'")
            print(f"    - Updated mermaid diagram")
        
        # Save architectural progress
        save_architectural_progress(state, component_name)
        
        final_components = len(state["architectural_components"])
        final_relationships = len(state["architectural_relationships"])
        logger.info(f" Architectural analysis completed | Component: '{component_name}' | Total components: {final_components} | Total relationships: {final_relationships}")
        logger.info(f" Architectural analysis completed for '{component_name}'")
        print(f"--- Architectural Analyzer: Analysis completed (Total: {final_components} components, {final_relationships} relationships) ---")
        
    except Exception as e:
        logger.error(f" Architectural analysis failed | Component: '{component_name}' | Error: {e}")
        logger.error(f" Architectural analysis failed for '{component_name}': {e}")
        print(f"--- Architectural Analyzer: Analysis failed: {e} ---")
    
    logger.info(f" Node: architectural_diagram | Status: completed | Component: '{component_name}'")
    
    return state

#..................New code added......................
def system_synthesis_node(state: DocumentationState) -> DocumentationState:
    logger.info(" Node: system_synthesis | Status: started")
    print("--- System Synthesizer: Creating high-level architectural model ---")
    all_components_summary = json.dumps(state.get('architectural_components', []), indent=2)
    all_relationships_summary = json.dumps(state.get('architectural_relationships', []), indent=2)
    synthesis_prompt = ChatPromptTemplate.from_template(
    """
    You are an expert System Architect. You have been provided with a list of all the code components (files) and their direct relationships from a codebase.

    Your task is to synthesize this information into a high-level, logical system architecture diagram model.

    Follow these steps:
    1.  **Group Components**: Group the individual code files into high-level logical blocks (e.g., 'API Gateway', 'Primary Database').
    2.  **Assign a Type**: For each high-level block, assign a `type`. Use one of the following: 'API', 'Service', 'Database', 'Queue', 'Worker'.
    3.  **Assign a Group**: For each high-level block, assign a `group` name. Components in the same group will be clustered together (e.g., 'Backend Services', 'Data Tier').
    4.  **Define Workflow**: Describe the flow between these blocks with a clear `label`.

    Here is the low-level data:
    ---
    COMPONENTS: {components}
    ---
    RELATIONSHIPS: {relationships}
    ---

    Respond with a JSON object that defines the high-level architecture. Use this exact format:
    {{
        "high_level_components": [
            {{
                "id": "api_gateway",
                "label": "API Gateway",
                "type": "API",
                "group": "Backend Services"
            }},
            {{
                "id": "postgres_db",
                "label": "Postgres DB",
                "type": "Database",
                "group": "Data Tier"
            }}
        ],
        "high_level_relationships": [
            {{
                "from": "api_gateway",
                "to": "postgres_db",
                "label": "Reads user data via SQL"
            }}
        ]
    }}
    """
)
    chain = synthesis_prompt | llm | JsonOutputParser()
    try:
        architectural_model = chain.invoke({
            "components": all_components_summary,
            "relationships": all_relationships_summary
        })
        state['architectural_components'] = architectural_model.get("high_level_components", [])
        state['architectural_relationships'] = architectural_model.get("high_level_relationships", [])
        logger.info(" High-level architectural model created successfully.")
        print("--- System Synthesizer: High-level model created ---")
    except Exception as e:
        logger.error(f" System synthesis failed: {e}")
        print(f"--- System Synthesizer: Failed to create model: {e} ---")
    return state
#........................................................................................

def save_architectural_progress(state: DocumentationState, component_name: str):
    """Save architectural diagram progress incrementally."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_component = sanitize_filename(str(component_name))
    
    # Create architecture-specific directory
    arch_dir = os.path.join(INCREMENTAL_SAVE_DIR, "architecture")
    os.makedirs(arch_dir, exist_ok=True)
    
    # Save current architectural state
    arch_state = {
        "timestamp": timestamp,
        "component": component_name,
        "components_count": len(state.get("architectural_components", {})),
        "relationships_count": len(state.get("architectural_relationships", [])),
        "architectural_components": state.get("architectural_components", {}),
        "architectural_relationships": state.get("architectural_relationships", []),
        "diagram_mermaid_code": state.get("diagram_mermaid_code", ""),
        "diagram_description": state.get("diagram_description", "")
    }
    
    filename = f"{timestamp}_arch_progress_{safe_component}.json"
    filepath = os.path.join(arch_dir, filename)
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(arch_state, f, indent=2, ensure_ascii=False)
        logger.info(f" Architectural progress saved: {filepath}")
    except Exception as e:
        logger.error(f" Failed to save architectural progress: {e}")

# Updated parallel processing to include architectural analysis
async def parallel_processing_node(state: DocumentationState) -> DocumentationState:
    """Runs both documentation writers and architectural analyzer in parallel."""
    component_name = state['current_component_name']
    total_sections = len(state["target_sections"])
    
    logger.info(f" Node: parallel_processing | Status: started | Component: '{component_name}' | Tasks: {total_sections + 1}")
    logger.info(f" Parallel Processing: Starting writers + architecture for '{component_name}'")
    print(f"--- Parallel Processing: Starting {total_sections} writers + architecture ---")
    
    # Log what sections will be processed
    logger.info(f" Processing sections | Component: '{component_name}' | Sections: {state['target_sections']}")
    for i, section in enumerate(state["target_sections"], 1):
        print(f"    - Task {i}: Documentation for '{section}'")
    print(f"    - Task {total_sections + 1}: Architectural analysis")
    
    # Create tasks for both documentation and architecture
    tasks = []
    
    # Add documentation writer tasks
    for section_name in state["target_sections"]:
        tasks.append(process_documentation_section(state, section_name))
    
    # Add architectural analysis task
    tasks.append(process_architectural_analysis(state))
    
    try:
        # Execute all tasks concurrently
        logger.info(f" Executing parallel tasks | Component: '{component_name}' | Total tasks: {len(tasks)} ({total_sections} docs + 1 architecture)")
        logger.info(f" Executing {len(tasks)} parallel tasks ({total_sections} docs + 1 architecture)")
        print(f"    - Executing {len(tasks)} tasks concurrently...")
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process documentation results
        successful_sections = 0
        failed_sections = 0
        
        for i, result in enumerate(results[:-1]):  # All except the last (architecture) result
            section_name = state["target_sections"][i]
            if isinstance(result, Exception):
                logger.error(f" Documentation task failed | Component: '{component_name}' | Section: '{section_name}' | Error: {result}")
                logger.error(f" Documentation writer exception: {result}")
                print(f"    - Failed: '{section_name}' - {result}")
                failed_sections += 1
            else:
                section_name, content = result
                state["document_content"][section_name] = content
                logger.info(f" Documentation task completed | Component: '{component_name}' | Section: '{section_name}' | Length: {len(content)} chars")
                print(f"    - Completed: '{section_name}' ({len(content)} chars)")
                successful_sections += 1
        
        # Process architectural result
        arch_result = results[-1]
        if isinstance(arch_result, Exception):
            logger.error(f" Architectural task failed | Component: '{component_name}' | Error: {arch_result}")
            logger.error(f" Architectural analysis exception: {arch_result}")
            print(f"    - Architecture analysis failed: {arch_result}")
        else:
            # Architectural analysis updates state in-place
            logger.info(f" Architectural task completed | Component: '{component_name}'")
            logger.info(f" Architectural analysis completed successfully")
            print(f"    - Architecture analysis completed")
        
        logger.info(f" Parallel processing summary | Component: '{component_name}' | Successful docs: {successful_sections} | Failed docs: {failed_sections}")
        logger.info(f" Parallel processing completed: {successful_sections} docs successful, {failed_sections} docs failed")
        print(f"--- Summary: {successful_sections} successful, {failed_sections} failed ---")
        
    except Exception as exc:
        logger.error(f" Parallel processing failed | Component: '{component_name}' | Error: {exc}")
        logger.error(f" Parallel processing failed: {exc}")
        print(f"--- Parallel processing failed: {exc} ---")
    
    # Save incremental progress
    save_incremental_progress(state, "parallel_processing_completed")
    
    logger.info(f" Node: parallel_processing | Status: completed | Component: '{component_name}'")
    
    return state

async def process_documentation_section(state: DocumentationState, section_name: str) -> tuple[str, str]:
    """Process a single documentation section."""
    component_name = state['current_component_name']
    
    logger.info(f" Processing documentation section | Component: '{component_name}' | Section: '{section_name}'")
    
    writer_prompt_template = AGENT_PROMPTS.get(section_name, 
        """You are a technical writer. Your task is to update the \"{section_name}\" section.
        
        **CRITICAL INFORMATION POLICY**:
        - ONLY include information that is explicitly present in the provided documents
        - DO NOT create, infer, or assume any information that is not directly stated
        - If you are uncertain about any detail, it is better to OMIT it rather than include potentially incorrect information
        - Base your documentation strictly on the factual content provided in the component documentation
        
        Analyze `{component_name}` and integrate any relevant information into the existing content.
        Use rich markdown like code blocks, tables, and lists to format the information clearly.
        EXISTING CONTENT: --- {existing_content} ---
        NEW INFORMATION: --- {component_doc} ---
        Respond with the complete, updated markdown for the \"{section_name}\" section. Do NOT wrap the entire output in triple backticks or code blocks. Only use code blocks for actual code, not for the whole section."""
    )
    
    existing_content = state["document_content"].get(section_name, "")
    existing_length = len(existing_content or "")
    
    logger.info(f" Section context | Component: '{component_name}' | Section: '{section_name}' | Existing content: {existing_length} chars")
    
    prompt = ChatPromptTemplate.from_template(writer_prompt_template)
    chain = prompt | llm | StrOutputParser()
    
    try:
        logger.info(f" LLM call initiated | Component: '{component_name}' | Section: '{section_name}' | Type: documentation_writer")
        
        updated_section_content = chain.ainvoke({
            "section_name": section_name,
            "existing_content": existing_content or "This section is empty. Please start it.",
            "component_name": component_name,
            "component_doc": state["current_component_doc"],
            "component_context": state["current_component_context"]
        })
        
        new_length = len(updated_section_content)
        
        logger.info(f" LLM response received | Component: '{component_name}' | Section: '{section_name}' | New content: {new_length} chars")
        logger.info(f" Section processing completed | Component: '{component_name}' | Section: '{section_name}' | Content generated: {new_length} chars")
        
        # Save LLM interaction for documentation section
        save_llm_interaction(
            component_name,
            f"doc_writer_{section_name.replace(' ', '_')}",
            f"Section: {section_name}\nComponent: {component_name}\nDoc: {state['current_component_doc'][:500]}...",
            updated_section_content,
            {
                "section_name": section_name,
                "existing_content_length": existing_length,
                "new_content_length": new_length
            }
        )
        
        # Save section content
        save_section_content(component_name, section_name, updated_section_content)
        return section_name, updated_section_content
        
    except Exception as e:
        logger.error(f" Section processing failed | Component: '{component_name}' | Section: '{section_name}' | Error: {e}")
        logger.error(f" Error processing section '{section_name}': {e}")
        error_content = f"Error generating content for {section_name}: {str(e)}"
        return section_name, error_content

async def process_architectural_analysis(state: DocumentationState) -> DocumentationState:
    """Process architectural analysis for the current component."""
    return await architectural_diagram_node(state)

# def parallel_processing_node_sync(state: DocumentationState) -> DocumentationState:
#     """Synchronous wrapper for parallel processing."""
#     return asyncio.run(parallel_processing_node(state))

# Updated parallel_writer_node with integrated progress tracking
async def parallel_writer_node(state: DocumentationState) -> DocumentationState:
    """Invokes the specialist writer agents in parallel for the selected sections using async/await."""
    component_name = state['current_component_name']
    total_sections = len(state["target_sections"])
    logger.info(f" Parallel Writers: Starting for '{component_name}' with {total_sections} sections")
    print(f"--- Parallel Writers: Starting for '{component_name}' ---")
    
    # Global progress tracking
    completed_sections = 0
    
    async def process_section(section_name: str) -> tuple[str, str]:
        """Process a single section asynchronously and return (section_name, content)."""
        nonlocal completed_sections
        completed_sections += 1
        
        logger.info(f" Processing section: '{section_name}' for component '{component_name}' ({completed_sections}/{total_sections})")
        print(f"    - Invoking writer for section: '{section_name}' ({completed_sections}/{total_sections})")
        
        writer_prompt_template = AGENT_PROMPTS.get(section_name, 
            """You are a technical writer. Your task is to update the \"{section_name}\" section.
            
            **CRITICAL INFORMATION POLICY**:
            - ONLY include information that is explicitly present in the provided documents
            - DO NOT create, infer, or assume any information that is not directly stated
            - If you are uncertain about any detail, it is better to OMIT it rather than include potentially incorrect information
            - Base your documentation strictly on the factual content provided in the component documentation
            
            Analyze `{component_name}` and integrate any relevant information into the existing content.
            Use rich markdown like code blocks, tables, and lists to format the information clearly.
            EXISTING CONTENT: --- {existing_content} ---
            NEW INFORMATION: --- {component_doc} ---
            Respond with the complete, updated markdown for the \"{section_name}\" section. Do NOT wrap the entire output in triple backticks or code blocks. Only use code blocks for actual code, not for the whole section."""
        )
        
        existing_content = state["document_content"].get(section_name, "")
        prompt = ChatPromptTemplate.from_template(writer_prompt_template)
        chain = prompt | llm | StrOutputParser()
        
        try:
            logger.info(f" Calling LLM for section '{section_name}' in component '{component_name}'")
            updated_section_content = await chain.ainvoke({
                "section_name": section_name,
                "existing_content": existing_content or "This section is empty. Please start it.",
                "component_name": component_name,
                "component_doc": state["current_component_doc"],
                "component_context": state["current_component_context"]
            })
            
            # Save section content after LLM call
            save_section_content(component_name, section_name, updated_section_content)
            
            logger.info(f" Section '{section_name}' completed for component '{component_name}' ({completed_sections}/{total_sections})")
            print(f"    - Writer for '{section_name}' finished.")
            return section_name, updated_section_content
            
        except Exception as e:
            logger.error(f" Error processing section '{section_name}' for component '{component_name}': {e}")
            print(f"    - Error in writer for '{section_name}': {e}")
            return section_name, f"Error generating content for {section_name}: {str(e)}"
    
    # Use asyncio.gather for concurrent execution of all sections
    try:
        # Create tasks for all sections
        tasks = [process_section(section_name) for section_name in state["target_sections"]]

         # --- FIX: ADD THIS LINE ---
        # Add the architectural analysis task to run in parallel
        tasks.append(process_architectural_analysis(state))
        # -------------------------
        
        # Execute all tasks concurrently
        logger.info(f" Executing {len(tasks)} LLM calls concurrently for '{component_name}'")
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results and handle any exceptions
        successful_sections = 0
        failed_sections = 0
        
        for result in results[:-1]:
            if isinstance(result, Exception):
                logger.error(f" Writer exception for '{component_name}': {result}")
                print(f"    - Writer generated an exception: {result}")
                failed_sections += 1
            else:
                section_name, content = result
                state["document_content"][section_name] = content
                successful_sections += 1
                 
        # Optional: Check if the architecture task failed
        arch_result = results[-1]
        if isinstance(arch_result, Exception):
            logger.error(f" Architectural analysis exception for '{component_name}': {arch_result}")
            print(f"     - Architecture analysis failed: {arch_result}")
                
        logger.info(f" Parallel Writers completed for '{component_name}': {successful_sections} successful, {failed_sections} failed")
                
    except Exception as exc:
        logger.error(f" Parallel writers failed for '{component_name}': {exc}")
        print(f"    - Parallel writers failed with exception: {exc}")
    
    # Save incremental progress
    save_incremental_progress(state, "parallel_writers_completed")
    
    logger.info(f" Parallel Writers: Completed all {len(state['target_sections'])} sections for '{component_name}'")
    print(f"--- Parallel Writers: Completed all {len(state['target_sections'])} sections ---")
    return state

# Remove the duplicate patching code and use the consolidated version
# def parallel_writer_node_sync(state: DocumentationState) -> DocumentationState:
#     """Synchronous wrapper for the async parallel_writer_node function."""
#     return asyncio.run(parallel_writer_node(state))

def parallel_writer_node_sync(state: DocumentationState) -> DocumentationState:
    """Synchronous wrapper for the async parallel_writer_node function."""
    try:
        # Add timeout to prevent hanging
        return asyncio.run(asyncio.wait_for(parallel_writer_node(state), timeout=300))  # 5 minutes timeout
    except asyncio.TimeoutError:
        logger.error(f" Parallel processing timed out for component: {state.get('current_component_name')}")
        return state
    except Exception as e:
        logger.error(f" Parallel processing failed: {e}")
        return state
    
def compiler_node(state: DocumentationState) -> DocumentationState:
    """Assembles all the final sections into the complete, hierarchical document."""
    logger.info("� Node: compiler | Status: started")
    logger.info("� Compiler: Starting document assembly")
    print("--- Compiler: Assembling Final Document ---")

    def strip_triple_backticks(text: str) -> str:
        # Remove wrapping triple backticks (with or without language) from the whole section
        pattern = r"^```[a-zA-Z]*\n([\s\S]*?)\n```$"
        return re.sub(pattern, r"\1", text.strip(), flags=re.MULTILINE)

    final_doc_parts = []
    sections_included = 0
    total_sections_available = sum(len(subsections) for subsections in HIERARCHICAL_STRUCTURE.values())
    sections_with_content = 0

    # First pass: count sections with content
    for main_section, subsections in HIERARCHICAL_STRUCTURE.items():
        for subsection_name in subsections:
            content = state["document_content"].get(subsection_name, "").strip()
            if content:
                sections_with_content += 1

    logger.info(f" Document assembly analysis | Total available sections: {total_sections_available} | Sections with content: {sections_with_content}")
    print(f"    - Sections available: {total_sections_available}")
    print(f"    - Sections with content: {sections_with_content}")

    for main_section, subsections in HIERARCHICAL_STRUCTURE.items():
        # Check if any subsection within this main section has content
        section_has_content = any(state["document_content"].get(sub, "").strip() for sub in subsections)

        # Only add the main section header if it has content
        if section_has_content:
            final_doc_parts.append(f"# {main_section}")
            logger.info(f" Adding main section: {main_section}")
            print(f"    - Adding main section: {main_section}")

            for subsection_name in subsections:
                content = state["document_content"].get(subsection_name, "").strip()
                if content:
                    # Remove wrapping triple backticks if present
                    cleaned_content = strip_triple_backticks(content)
                    content_length = len(cleaned_content)
                    final_doc_parts.append(f"## {subsection_name}\n\n{cleaned_content}")
                    sections_included += 1
                    logger.info(f" Added subsection: {subsection_name} | Length: {content_length} chars")
                    logger.info(f" Added subsection: {subsection_name}")
                    print(f"      - Added: {subsection_name} ({content_length} chars)")
                else:
                    logger.info(f" Skipped subsection (empty): {subsection_name}")
        else:
            logger.info(f" Skipped main section (no content): {main_section}")
            print(f"    - Skipped main section: {main_section} (no content)")

    state["final_document"] = "\n\n---\n\n".join(final_doc_parts)
    final_doc_length = len(state["final_document"])

    logger.info(f" Document assembly completed | Sections included: {sections_included}/{sections_with_content} | Total length: {final_doc_length} chars")
    logger.info(f" Compiler: Document assembled with {sections_included} sections")
    print("--- Compiler: Final document assembled! ---")
    print(f"    - Final document: {sections_included} sections, {final_doc_length} characters")

    # Save final document progress
    save_incremental_progress(state, "final_document_compiled")

    logger.info(" Node: compiler | Status: completed")

    return state

def diagram_finalizer_node(state: DocumentationState) -> DocumentationState:
    logger.info(" Diagram Finalizer: Creating final architectural diagram")
    print("--- Diagram Finalizer: Generating final diagram ---")
    try:
        # NOTE: For testing, we only call the diagram generation, not the other helpers
        diagram_output = generate_final_diagrams_diagram(state)
        print(diagram_output)
        logger.info(" Diagram Finalizer: Basic diagram generated successfully")
        print("--- Diagram Finalizer: Basic diagram completed ---")
    except Exception as e:
        logger.error(f" Diagram Finalizer failed: {e}")
        print(f"--- Diagram Finalizer: Failed - {e} ---")
    return state

def generate_final_mermaid_diagram(state: DocumentationState) -> str:
    """Generate a comprehensive mermaid diagram from collected architectural data."""
    components = state.get("architectural_components", {})
    relationships = state.get("architectural_relationships", [])
    
    if not components:
        return "graph TD\n    A[No Components Found]"
    
    # Group components by layer
    layers = {}
    for comp_name, comp_info in components.items():
        layer = comp_info.get("layer", "UNKNOWN")
        if layer not in layers:
            layers[layer] = []
        layers[layer].append((comp_name, comp_info))
    
    # Build mermaid diagram
    mermaid_lines = ["graph TD"]
    
    # Add subgraphs for each layer
    for layer_name, layer_components in layers.items():
        mermaid_lines.append(f"    subgraph {layer_name}_LAYER[\"{layer_name} Layer\"]")
        
        for comp_name, comp_info in layer_components:
            comp_type = comp_info.get("type", "COMPONENT")
            safe_name = sanitize_mermaid_id(comp_name)
            
            # Choose shape based on component type
            if comp_type in ["API_ENDPOINT", "CONTROLLER"]:
                shape = f"{safe_name}([{comp_name}])"
            elif comp_type in ["DATABASE", "DATA"]:
                shape = f"{safe_name}[(Database: {comp_name})]"
            elif comp_type in ["SERVICE", "BUSINESS"]:
                shape = f"{safe_name}[{comp_name}]"
            else:
                shape = f"{safe_name}{{{comp_name}}}"
            
            mermaid_lines.append(f"        {shape}")
        
        mermaid_lines.append("    end")
    
    # Add relationships
    for rel in relationships:
        from_safe = sanitize_mermaid_id(rel["from"])
        to_safe = sanitize_mermaid_id(rel["to"])
        rel_type = rel.get("type", "DEPENDS_ON")
        
        # Choose arrow style based on relationship type
        if rel_type == "CALLS":
            arrow = "-->"
        elif rel_type == "INHERITS":
            arrow = "-..->"
        elif rel_type == "IMPLEMENTS":
            arrow = "==>"
        else:
            arrow = "-->"
        
        mermaid_lines.append(f"    {from_safe} {arrow} {to_safe}")
    
    return "\n".join(mermaid_lines)

def sanitize_mermaid_id(name: str) -> str:
    """Sanitize component names for mermaid diagram IDs."""
    return re.sub(r'[^a-zA-Z0-9_]', '_', name)

def generate_architectural_description(state: DocumentationState) -> str:
    """Generate a natural language description of the architecture."""
    components = state.get("architectural_components", {})
    relationships = state.get("architectural_relationships", [])
    
    if not components:
        return "No architectural components were identified in the codebase."
    
    description = ["# System Architecture Overview\n"]
    description.append(f"The system consists of **{len(components)}** main components with **{len(relationships)}** identified relationships.\n")
    
    # Group by layers
    layers = {}
    for comp_name, comp_info in components.items():
        layer = comp_info.get("layer", "UNKNOWN")
        if layer not in layers:
            layers[layer] = []
        layers[layer].append((comp_name, comp_info))
    
    # Describe each layer
    for layer_name, layer_components in layers.items():
        description.append(f"## {layer_name} Layer\n")
        
        for comp_name, comp_info in layer_components:
            comp_type = comp_info.get("type", "COMPONENT")
            responsibilities = comp_info.get("responsibilities", "No description available")
            description.append(f"### {comp_name} ({comp_type})\n")
            description.append(f"{responsibilities}\n")
    
    # Describe relationships
    if relationships:
        description.append("## Component Relationships\n")
        for rel in relationships:
            description.append(f"- **{rel['from']}** {rel['type'].lower().replace('_', ' ')} **{rel['to']}**: {rel.get('description', 'No description')}")
    
    return "\n".join(description)

def save_basic_diagram_files(state: DocumentationState, mermaid_code: str, description: str):
    """Save basic diagram files before beautification."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create diagrams directory
    diagrams_dir = os.path.join(FINAL_DOC_DIR, "diagrams")
    os.makedirs(diagrams_dir, exist_ok=True)
    
    # Save mermaid diagram
    mermaid_file = os.path.join(diagrams_dir, f"architecture_diagram_{timestamp}.mmd")
    with open(mermaid_file, 'w', encoding='utf-8') as f:
        f.write(mermaid_code)
    
    # Save architectural description
    desc_file = os.path.join(diagrams_dir, f"architecture_description_{timestamp}.md")
    with open(desc_file, 'w', encoding='utf-8') as f:
        f.write(description)
    
    # Save architectural data as JSON
    arch_data_file = os.path.join(diagrams_dir, f"architecture_data_{timestamp}.json")
    arch_data = {
        "timestamp": timestamp,
        "components": state.get("architectural_components", {}),
        "relationships": state.get("architectural_relationships", []),
        "mermaid_code": mermaid_code,
        "description": description
    }
    
    with open(arch_data_file, 'w', encoding='utf-8') as f:
        json.dump(arch_data, f, indent=2, ensure_ascii=False)
    
    logger.info(f" Basic diagram files saved in: {diagrams_dir}")

def check_and_recover_state():
    """Check for hanging state and provide recovery options."""
    latest_save = None
    if os.path.exists(INCREMENTAL_SAVE_DIR):
        save_files = [f for f in os.listdir(INCREMENTAL_SAVE_DIR) if f.endswith('.json')]
        if save_files:
            latest_save = max(save_files, key=lambda x: os.path.getctime(os.path.join(INCREMENTAL_SAVE_DIR, x)))
            save_time = datetime.fromtimestamp(os.path.getctime(os.path.join(INCREMENTAL_SAVE_DIR, latest_save)))
            if datetime.now() - save_time > timedelta(minutes=10):
                logger.warning(f" Last save was {datetime.now() - save_time} ago. Possible hang detected.")
                return os.path.join(INCREMENTAL_SAVE_DIR, latest_save)
    return None
'''
def generate_final_diagrams_diagram(state: DocumentationState) -> str:
    from diagrams import Diagram
    from diagrams.programming.language import Python
    from diagrams.generic.compute import Rack
    from diagrams.generic.database import SQL
    
    components = state.get("architectural_components", {})
    
    with Diagram("System Architecture", filename="final_docs/diagrams/architecture", show=False):
        nodes = {}
        for comp_name, comp_info in components.items():
            comp_type = comp_info.get("type", "COMPONENT")
            if comp_type in ["API_ENDPOINT", "CONTROLLER"]:
                nodes[comp_name] = Rack(comp_name)
            elif comp_type in ["DATABASE"]:
                nodes[comp_name] = SQL(comp_name)
            else:
                nodes[comp_name] = Python(comp_name)
        
        # Add relationships
        for rel in state.get("architectural_relationships", []):
            if rel["from"] in nodes and rel["to"] in nodes:
                nodes[rel["from"]] >> nodes[rel["to"]]
    
    return "Diagrams-based architecture diagram generated"
'''
def generate_final_diagrams_diagram(state: DocumentationState) -> str:
    """
    Generates a professional architecture diagram using Azure icons.
    """
    from diagrams.azure.compute import AppServices, FunctionApps, VM
    from diagrams.azure.database import SQLDatabases
    from diagrams.azure.integration import APIManagement
    from diagrams.azure.storage import BlobStorage
    from diagrams import Diagram, Cluster, Edge

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    diagrams_dir = os.path.join(FINAL_DOC_DIR, "diagrams")
    os.makedirs(diagrams_dir, exist_ok=True)
    output_filename = os.path.join(diagrams_dir, f"azure_architecture_{timestamp}")

    components = state.get("architectural_components", [])
    relationships = state.get("architectural_relationships", [])

    if not components:
        return "No architectural components found to generate a diagram."

    # --- UPDATED AZURE ICON MAPPING ---
    icon_map = {
        "API": APIManagement,
        "Service": AppServices,
        "Worker": FunctionApps,
        "Database": SQLDatabases,
        "DEFAULT": Python # Fallback icon
    }

    with Diagram("System Architecture (Azure)", filename=output_filename, show=False):
        nodes = {}
        grouped_nodes = {}

        for comp_info in components:
            group = comp_info.get("group", "Default Group")
            if group not in grouped_nodes:
                grouped_nodes[group] = []
            grouped_nodes[group].append(comp_info)
        
        for group_name, component_list in grouped_nodes.items():
            with Cluster(group_name):
                for comp_info in component_list:
                    node_id = comp_info.get("id")
                    node_label = comp_info.get("label")
                    node_type = comp_info.get("type", "DEFAULT")
                    
                    Icon = icon_map.get(node_type, icon_map["DEFAULT"])
                    nodes[node_id] = Icon(node_label)

        for rel in relationships:
            from_node = rel.get("from")
            to_node = rel.get("to")
            rel_label = rel.get("label", "")
            
            if from_node in nodes and to_node in nodes:
                nodes[from_node] >> Edge(label=rel_label) >> nodes[to_node]
    
    return f"Azure diagram generated at {output_filename}.png"


def run_architecture_generation_node(state: DocumentationState) -> DocumentationState:
    """Runs the standalone architecture generation process as the final step."""
    logger.info(" Starting standalone architecture diagram generation...")
    
    if len(sys.argv) < 2:
        logger.error(" Architecture generation requires a repository path argument.")
        print("Usage: python main2.py <path_to_repository>")
        return state
        
    repo_path = sys.argv[1]
    if not os.path.isdir(repo_path):
        logger.error(f" Repository path '{repo_path}' not found for architecture generation.")
        return state

    # Execute the sequence from the first script
    strategic_files = find_strategic_files(repo_path)
    if not strategic_files:
        print("Could not find any strategic files to generate architecture diagram.")
        return state

    analyzed_data = analyze_files_to_data(strategic_files, repo_path)
    architecture_model = synthesize_architecture_model(analyzed_data)
    
    if not architecture_model.get("components"):
        print("Failed to create an architectural model. Exiting diagram generation.")
        return state

    repo_name = os.path.basename(os.path.normpath(repo_path))
    output_dir = os.path.join("final_docs", "diagrams")
    os.makedirs(output_dir, exist_ok=True)
    
    # Save the intermediate JSON model for debugging in the new directory
    model_path = os.path.join(output_dir, "architecture_model.json")
    with open(model_path, 'w', encoding='utf-8') as f:
        json.dump(architecture_model, f, indent=2)
    logger.info(f" Intermediate architecture model saved to: {model_path}")
    
    # Define the new base filename for the diagram
    diagram_filename_base = os.path.join(output_dir, "final_architecture")
    generate_diagram(architecture_model, diagram_filename_base)
        
    # Update the success message to reflect the new path
    print(f"\n Success! Advanced system architecture diagram saved in: {output_dir}")
    logger.info(" Standalone architecture diagram generation complete.")
    
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
# workflow.add_node("parallel_processing", parallel_processing_node_sync)
workflow.add_node("parallel_processing", parallel_writer_node_sync)
workflow.add_node("compiler", compiler_node)
workflow.add_node("architecture_generator", run_architecture_generation_node)
#workflow.add_node("system_synthesis", system_synthesis_node) # Add the new node
#workflow.add_node("diagram_finalizer", diagram_finalizer_node)

workflow.set_entry_point("loader")
workflow.add_conditional_edges("loader", should_continue_processing, {"continue": "scrapper", "end": "compiler"})

# --- FIX: Update the conditional edge to read the decision from the state ---
workflow.add_conditional_edges(
    "scrapper",
    lambda state: state["scrapper_decision"], # Read the decision from the state key
    {"scrap": "loader", "proceed": "selector"}
)

workflow.add_edge("selector", "parallel_processing")
workflow.add_edge("parallel_processing", "loader")
#workflow.add_edge("compiler", "diagram_finalizer")
# --- FIX: Define the final sequence of nodes ---
# This ensures a path exists to your new synthesis node.
workflow.add_edge("compiler", "architecture_generator") # Generate architecture diagram
#workflow.add_edge("system_synthesis", "diagram_finalizer") # Run finalizer with the new model
workflow.add_edge("architecture_generator", END)

app = workflow.compile()

# --- Main execution block ---
if __name__ == "__main__":
    start_time = datetime.now()
    progress_bar = None

    JSON_FILE = "output/CalculatorCode/documentation_and_graph_data.json"
    GRAPH_FILE = "output/CalculatorCode/conceptual_graph.pkl"
    FINAL_DOC_DIR = "final_docs"
    os.makedirs(FINAL_DOC_DIR, exist_ok=True)
    OUTPUT_FILE_BASE = "Complete_Technical_Documentation.md"
    OUTPUT_FILE = os.path.join(FINAL_DOC_DIR, OUTPUT_FILE_BASE)

    logger.info(" DOCUMENTATION GENERATION STARTED")
    logger.info(f" Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print(" AI DOCUMENTATION GENERATOR")
    print("=" * 80)
    print(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

    logger.info(" File validation:")
    logger.info(f" JSON file: {JSON_FILE}")
    logger.info(f" Graph file: {GRAPH_FILE}")
    logger.info(f" Output file: {OUTPUT_FILE}")
    print(f"Input files:")
    print(f"  - JSON: {JSON_FILE}")
    print(f"  - Graph: {GRAPH_FILE}")
    print(f"  - Output: {OUTPUT_FILE}")

    try:
        logger.info(" Loading initial data...")
        print("\n Loading initial data...")
        
        initial_data = load_all_data(JSON_FILE, GRAPH_FILE)
        if initial_data:
            total_components = len(initial_data["all_data"])
            logger.info(f" Data loaded successfully")
            logger.info(f" Total components to process: {total_components}")
            print(f" Data loaded: {total_components} components found")

            # Use tqdm to show progress of component processing
            component_names = sorted(initial_data["all_data"].keys())
            progress_bar = tqdm(total=total_components, desc="Initializing...", unit="component", 
                               bar_format='{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]')

            logger.info(" Initializing documentation state...")
            print(" Initializing documentation state...")
            
            initial_state = DocumentationState(
                unprocessed_components=component_names.copy(),
                all_data=initial_data["all_data"],
                nx_graph=initial_data["nx_graph"],
                document_content={section: "" for section in ALL_SECTIONS},
                current_component_name=None,
                current_component_doc=None,
                current_component_context=None,
                target_sections=[],
                final_document=None,
                scrapper_decision="",
                connected_nodes=[],
                # Initialize architectural diagram fields
                architectural_components={},
                architectural_relationships=[],
                diagram_mermaid_code="graph TD\n",
                diagram_description="## System Architecture Overview\n\nThis diagram represents the architectural components and their relationships:\n\n"
            )

            config = {"recursion_limit": total_components * 4 + 15}
            logger.info(f" Graph configuration:")
            logger.info(f" Graph recursion limit set to: {config['recursion_limit']}")
            logger.info(f" Available documentation sections: {len(ALL_SECTIONS)}")
            print(f" Graph recursion limit: {config['recursion_limit']}")
            print(f" Documentation sections: {len(ALL_SECTIONS)}")
            print(f"--- Running graph with recursion limit: {config['recursion_limit']} ---")

            logger.info(" Starting documentation generation pipeline...")
            print("\n STARTING DOCUMENTATION GENERATION PIPELINE")
            print("=" * 60)
            
            final_state = app.invoke(initial_state, config=config)
            
            logger.info(" Pipeline execution completed")
            print("\n PIPELINE EXECUTION COMPLETED")
            print("=" * 60)
            
            if final_state and final_state.get("final_document"):
                # --- Save final document in versioned manner ---
                logger.info(" Saving final documentation...")
                print(" Saving final documentation...")
                
                def get_versioned_filename(base_path):
                    base_dir, base_name = os.path.split(base_path)
                    name, ext = os.path.splitext(base_name)
                    version = 1
                    candidate = os.path.join(base_dir, base_name)
                    while os.path.exists(candidate):
                        candidate = os.path.join(base_dir, f"{name}_v{version}{ext}")
                        version += 1
                    return candidate

                save_path = get_versioned_filename(OUTPUT_FILE)
                with open(save_path, "w", encoding="utf-8") as f:
                    f.write(final_state["final_document"])

                # Save final state as JSON
                final_state_file = os.path.join(INCREMENTAL_SAVE_DIR, f"final_state_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
                save_incremental_progress(final_state, "final_completion")

                end_time = datetime.now()
                duration = end_time - start_time

                # Log comprehensive statistics
                doc_length = len(final_state['final_document'])
                char_count = doc_length
                word_count = len(final_state['final_document'].split())
                line_count = final_state['final_document'].count('\n') + 1
                
                logger.info(" DOCUMENTATION GENERATION COMPLETED SUCCESSFULLY")
                logger.info(f" End time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
                logger.info(f" Total duration: {duration}")
                logger.info(f" Final document saved to: {save_path}")
                logger.info(f" Document statistics:")
                logger.info(f"   - Length: {char_count} characters")
                logger.info(f"   - Words: {word_count}")
                logger.info(f"   - Lines: {line_count}")
                logger.info(f" Incremental saves stored in: {INCREMENTAL_SAVE_DIR}")
                
                # Log comprehensive processing summary
                log_processing_summary()

                print("\n" + "=" * 80)
                print(" SUCCESS! DOCUMENTATION GENERATION COMPLETED")
                print("=" * 80)
                print(f" Document saved to: {save_path}")
                print(f" Total processing time: {duration}")
                print(f"� Document statistics:")
                print(f"   - Characters: {char_count:,}")
                print(f"   - Words: {word_count:,}")
                print(f"   - Lines: {line_count:,}")
                print(f"� Incremental saves: {INCREMENTAL_SAVE_DIR}")
                
                # Run diagram beautification
                # print("\n Running diagram beautification...")
                # logger.info(" Starting diagram beautification...")
                # try:
                #     import subprocess
                #     beautify_script = os.path.join(FINAL_DOC_DIR, "beautify_diagram.py")
                #     if os.path.exists(beautify_script):
                #         logger.info(f" Executing beautification script: {beautify_script}")
                #         result = subprocess.run([sys.executable, beautify_script], 
                #                               capture_output=True, text=True, cwd=os.getcwd())
                #         if result.returncode == 0:
                #             logger.info(" Diagram beautification completed successfully")
                #             print(" Diagram beautification completed successfully!")
                #             print(result.stdout)
                #         else:
                #             logger.warning(f" Diagram beautification had issues: {result.stderr}")
                #             print(f" Diagram beautification had issues: {result.stderr}")
                #     else:
                #         logger.warning(f" Beautification script not found: {beautify_script}")
                #         print(" Beautification script not found")
                # except Exception as e:
                #     logger.error(f" Could not run beautification automatically: {e}")
                #     print(f" Could not run beautification automatically: {e}")
                #     print(f" You can run it manually: python {os.path.join(FINAL_DOC_DIR, 'beautify_diagram.py')}")

            else:
                logger.error(" FAILURE: The final document could not be generated")
                print("\n" + "=" * 80)
                print(" FAILURE: THE FINAL DOCUMENT COULD NOT BE GENERATED")
                print("=" * 80)
        
        else:
            logger.error(" Failed to load initial data")
            print(" Failed to load initial data")
            
    except Exception as e:
        logger.error(f" CRITICAL ERROR during documentation generation: {e}")
        print(f"\n CRITICAL ERROR: {e}")
        print("=" * 80)
    
    finally:
        # Ensure progress bar is always closed
        if progress_bar:
            progress_bar.close()
        
        end_time = datetime.now()
        total_duration = end_time - start_time
        logger.info(f" Process ended at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f" Total execution time: {total_duration}")
        print(f"\n Process ended at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f" Total execution time: {total_duration}")
        print("=" * 80)