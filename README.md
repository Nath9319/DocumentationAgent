# 🤖✨ DocumentationAgent

Welcome to **DocumentationAgent**!  
A smart AI-powered tool that automatically generates structured, insightful, and visually appealing documentation for any GitHub repository.  
Let your projects explain themselves — so you can focus more on building and less on writing docs! 🚀

---

## 📚 What is DocumentationAgent?

**DocumentationAgent** is an intelligent documentation assistant designed to:
- 🔍 Analyze any codebase (regardless of language or structure)
- 📝 Create easy-to-understand, organized documentation
- 🌈 Add a splash of color and icons for maximum readability
- 🤝 Help teams onboard and collaborate faster

---

## 🦾 Key Features

- 🚦 **Automatic Codebase Analysis**  
  Scans your repository and extracts key information.
- 🧭 **Structured Documentation Output**  
  Generates clear sections for usage, API, architecture, and more.
- 🎨 **Colorful & Iconic Markdown**  
  Uses emojis and icons to make docs engaging and accessible.
- 🛠️ **Customizable Templates**  
  Tweak the output format as you like!
- 🌐 **Language-Agnostic**  
  Works with Python, JavaScript, Java, Go, and many more.

---

## 🚀 Getting Started

1. **Clone the repo**
   ```bash
   git clone https://github.com/Nath9319/DocumentationAgent.git
   ```
2. **Install dependencies**
   ```bash
   # Example for Python
   pip install -r requirements.txt
   ```
3. **Run the Agent**
   ```bash
   # Example command
   python agent.py --repo /path/to/your/repo
   ```

---

## 🛡️ Example Output

```markdown
# Project Title
## 🚀 Overview
Short project summary...

## 🏗️ Architecture
- Module 1: ...
- Module 2: ...

## 📦 API Reference
| Endpoint | Description |
|----------|-------------|
| `/api/v1/...` | ...      |

## 📝 Usage
How to install and run...

## 🤝 Contributing
Guidelines here...
```

---

## 🤩 Why Use DocumentationAgent?

- 🕒 Save hours on manual documentation
- 💡 Get AI-powered insights about your code
- 🚀 Boost team productivity and onboarding
- ✨ Make your repo shine for the community

---

## 🙏 Contributing

We welcome PRs, ideas, and feedback!  
Check out [CONTRIBUTING.md](CONTRIBUTING.md) to get started.

---

## 📄 License

This project is licensed under the MIT License.

---

## 👤 Author

- **Nath9319**  
  [GitHub Profile](https://github.com/Nath9319)

---

> ⭐️ If you like this project, give it a star!

---

# 🤖 DocumentationAgent

## Overview
DocumentationAgent is an AI-powered tool that automatically generates structured, insightful, and visually appealing documentation for any code repository. It analyzes your codebase, builds a code graph, and uses a LangGraph-based agent to generate documentation for each function and class, saving the results in a structured output directory.

---

## Key Files and Their Logic

### 1. `main.py`
- **Purpose:** Entry point for the DocumentationAgent.
- **Logic:**
  - Loads environment variables (e.g., `OPENAI_API_KEY`).
  - Checks the repository path and loads or constructs a code graph (`graph.pkl`).
  - Sets up the output directory for documentation.
  - Creates and runs the LangGraph agent, which iterates through the code graph and generates documentation for each node.

### 2. `RepoGraph/construct_graph.py`
- **Purpose:** Builds a code graph from the repository source code.
- **Logic:**
  - Uses tree-sitter to parse Python files and extract classes, functions, and their docstrings.
  - Constructs a graph (using networkx) where nodes represent code entities and edges represent relationships (e.g., function calls).
  - Saves the graph as `graph.pkl` and node metadata as `tags.json`.

### 3. `RepoGraph/graph_searcher.py`
- **Purpose:** Provides graph traversal utilities.
- **Logic:**
  - Implements one-hop and two-hop neighbor search, depth-first search (DFS), and breadth-first search (BFS) for the code graph.

### 4. `agent/agent_graph.py`
- **Purpose:** Defines the LangGraph agent's workflow.
- **Logic:**
  - Sets up a state machine with nodes for initializing the documentation queue, selecting nodes, gathering context, generating documentation, and saving results.
  - Controls the flow of the documentation process.

### 5. `agent/agent_nodes.py`
- **Purpose:** Implements the logic for each step in the agent's workflow.
- **Logic:**
  - Functions for initializing the documentation queue, selecting the next node, gathering context, generating documentation using LLMs, and saving documentation.

### 6. `agent/agent_state.py`
- **Purpose:** Defines the structure of the agent's state.
- **Logic:**
  - Uses a TypedDict to specify what information is passed between agent nodes (e.g., the code graph, queue of nodes to document, current node info, output directory).

### 7. `find_node_connections.py` & `get_node_info.py`
- **Purpose:** Utility scripts for exploring the code graph.
- **Logic:**
  - `find_node_connections.py`: Finds and prints direct incoming and outgoing connections for a given node.
  - `get_node_info.py`: Retrieves all stored information for a single node from the code graph.

### 8. `traverse_graph.py`
- **Purpose:** Demonstrates how to traverse the code graph.
- **Logic:**
  - Loads the graph and provides examples of iterating through nodes and performing DFS.

### 9. `visualize_graph.py` & `graph_visualization.html`
- **Purpose:** Visualizes the code graph.
- **Logic:**
  - Uses pyvis to create an interactive HTML visualization of the code graph.

### 10. `prompts/templates.py`
- **Purpose:** Stores prompt templates for the LLM.
- **Logic:**
  - Centralizes the prompt used to instruct the LLM on how to generate documentation for each code node.

### 11. `requirements.txt`
- **Purpose:** Lists Python dependencies for the project.

### 12. `.gitignore`
- **Purpose:** Specifies files and folders to be ignored by git (e.g., caches, virtual environments, data, agenticSeek, etc.).

---

## How It Works
1. **Graph Construction:**
   - Run the agent, which will parse your codebase and build a code graph if one does not exist.
2. **Documentation Generation:**
   - The agent traverses the graph, gathers context for each node, and uses an LLM to generate documentation.
3. **Output:**
   - Documentation is saved in a structured output directory, ready for use in your project.

---

## Getting Started
1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set your `OPENAI_API_KEY` in a `.env` file.
4. Run the agent:
   ```bash
   python main.py <path_to_your_repo>
   ```

---

## Contributing
Pull requests and feedback are welcome!
