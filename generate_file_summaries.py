import os
import json
from pathlib import Path
from typing import Dict, Any
from langchain_core.runnables import Runnable
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import AzureChatOpenAI

# Assumes file-level documentation will be generated from this base folder
docs_base_dir = "output/{repo_name}/documentation"

# Template prompt for summarizing file-level content
file_summary_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a senior technical writer. Generate a documentation summary for a code file."),
    ("human", """
You are provided with documentation of the components (functions/classes/module-level code) in a file:

{component_docs}

Generate a comprehensive FILE-LEVEL documentation that includes:

### 📌 Basic Information
- **Title & Overview**
- **Purpose**
- **Scope**

### ⚙️ Technical or Functional Details
- **Architecture / Design** (if relevant)
- **Features & Functions**
- **Requirements** (dependencies or data inputs)

### 🚀 Setup and Usage
- **Installation Instructions** (if applicable)
- **Configuration Settings** (if applicable)
- **Usage Guidelines** (how to use the features in this file)

Only use content present in the documentation snippets. Do not hallucinate missing logic.
""")
])

# Use Azure OpenAI (adjust deployment name and model)
lm = AzureChatOpenAI(
    deployment_name="gpt-4o-mini",
    model="gpt-4o-mini",
    temperature=0.3
)

summarizer: Runnable = file_summary_prompt | lm

def generate_file_level_doc(repo_name: str):
    repo_doc_dir = Path(f"output/{repo_name}/documentation")

    for py_file_dir in repo_doc_dir.rglob("*.py"):
        # Exclude markdown files
        continue

    for root, dirs, files in os.walk(repo_doc_dir):
        component_md_files = [f for f in files if f.endswith(".md") and "__file_summary.md" not in f]
        if not component_md_files:
            continue

        # Collect all component docs in this file
        component_docs = []
        for fname in component_md_files:
            fpath = os.path.join(root, fname)
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()
                component_docs.append(content)

        # Run the LLM agent to generate summary
        doc_input = {"component_docs": "\n\n---\n\n".join(component_docs)}
        summary = summarizer.invoke(doc_input).content

        # Save as __file_summary.md inside the same folder
        file_summary_path = os.path.join(root, "__file_summary.md")
        with open(file_summary_path, "w", encoding="utf-8") as f:
            f.write("# File Summary\n\n")
            f.write(summary)

        print(f"Generated file-level summary in: {file_summary_path}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python generate_file_level_docs.py <repo_name>")
        exit(1)

    repo_name = sys.argv[1]
    generate_file_level_doc(repo_name)
