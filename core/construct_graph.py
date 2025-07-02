# File: core/construct_graph.py
#
# This script is the heart of the repository analysis engine.
# This version is enhanced to robustly capture and create nodes for all
# module-level code (i.e., script code outside of any function or class).

import os
import sys
import warnings
import ast
import pickle
import json
from collections import namedtuple
import networkx as nx
from tqdm import tqdm

warnings.simplefilter("ignore", category=FutureWarning)
from tree_sitter_languages import get_language, get_parser

Tag = namedtuple("Tag", "rel_fname fname line name kind category info docstring".split())

class CodeGraph:
    """
    Analyzes a code repository and constructs a detailed dependency graph,
    including nodes for functions, classes, and module-level code.
    """

    def __init__(self, root=None):
        if not root:
            root = os.getcwd()
        self.root = root
        self.structure_cache = self._pre_parse_all_files()

    def _extract_function_calls(self, node):
        """
        Recursively extract all function calls from an AST node.
        """
        calls = []
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    calls.append(child.func.id)
                elif isinstance(child.func, ast.Attribute):
                    # Handle method calls like obj.method()
                    if isinstance(child.func.value, ast.Name):
                        calls.append(f"{child.func.value.id}.{child.func.attr}")
                    else:
                        calls.append(child.func.attr)
        return calls

    def _extract_class_inheritance_and_imports(self, node):
        """
        Extract base classes and imported classes from a class definition.
        """
        inherited_classes = []
        imported_classes = []
        
        # Extract base classes from class definition
        if hasattr(node, 'bases'):
            for base in node.bases:
                if isinstance(base, ast.Name):
                    inherited_classes.append(base.id)
                elif isinstance(base, ast.Attribute):
                    inherited_classes.append(f"{base.value.id}.{base.attr}" if isinstance(base.value, ast.Name) else base.attr)
        
        # Extract any class references in the class body (like type hints, etc.)
        for child in ast.walk(node):
            if isinstance(child, ast.Name) and child.id not in inherited_classes:
                # This could be a reference to another class
                imported_classes.append(child.id)
                
        return inherited_classes, imported_classes

    def _parse_python_file(self, file_path):
        """
        Parses a single Python file using the `ast` module to extract
        functions, classes, methods, their docstrings, and any module-level code.
        """
        try:
            with open(file_path, "r", encoding='utf-8', errors='ignore') as file:
                file_content = file.read()
                parsed_data = ast.parse(file_content)
        except Exception:
            return None

        class_info = []
        function_names = []
        class_methods = set()
        module_level_nodes = []
        module_level_calls = []

        # --- A more robust way to capture all module-level code ---
        # We iterate through the top-level nodes of the file's AST.
        for i, node in enumerate(parsed_data.body):
            if isinstance(node, ast.ClassDef):
                # Extract inheritance and class dependencies
                inherited_classes, imported_classes = self._extract_class_inheritance_and_imports(node)
                
                methods = []
                for n in node.body:
                    if isinstance(n, ast.FunctionDef):
                        # Extract function calls within the method
                        method_calls = self._extract_function_calls(n)
                        
                        # This is a method within the class
                        methods.append({
                            "name": n.name,
                            "start_line": n.lineno,
                            "end_line": getattr(n, 'end_lineno', n.lineno),
                            "text": ast.unparse(n),
                            "docstring": ast.get_docstring(n) or "",
                            "calls": method_calls
                        })
                        class_methods.add(n.name)
                
                class_info.append({
                    "name": node.name,
                    "start_line": node.lineno,
                    "end_line": getattr(node, 'end_lineno', node.lineno),
                    "text": ast.unparse(node),
                    "methods": methods,
                    "docstring": ast.get_docstring(node) or "",
                    "inherited_classes": inherited_classes,
                    "imported_classes": list(set(imported_classes))  # Remove duplicates
                })

            elif isinstance(node, ast.FunctionDef):
                # Extract function calls within the function
                function_calls = self._extract_function_calls(node)
                
                # This is a top-level function
                function_names.append({
                    "name": node.name,
                    "start_line": node.lineno,
                    "end_line": getattr(node, 'end_lineno', node.lineno),
                    "text": ast.unparse(node),
                    "docstring": ast.get_docstring(node) or "",
                    "calls": function_calls
                })

            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                # Ignore imports, as they are not executable code in this context
                continue

            elif i == 0 and isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
                # This is likely the module-level docstring, so we skip it.
                # We only check the very first node for this.
                continue
            
            else:
                # If it's not a class, function, or import, it's module-level code.
                # This correctly captures assignments, function calls, etc.
                module_level_nodes.append(node)
                # Extract function calls from module-level code
                module_level_calls.extend(self._extract_function_calls(node))

        module_level_code_str = ""
        if module_level_nodes:
            # Reconstruct the module-level code from the collected nodes
            module_level_code_str = "\n".join([ast.unparse(n) for n in module_level_nodes])

        return {
            "classes": class_info,
            "functions": function_names,
            "module_level_code": module_level_code_str,
            "module_level_calls": list(set(module_level_calls))  # Remove duplicates
        }

    def _pre_parse_all_files(self):
        """
        Walks the repository and runs the AST parser on all Python files,
        caching the results for fast lookups later.
        """
        print("Pre-parsing repository structure with AST...")
        structure = {}
        py_files = self.find_files(self.root)
        for file_path in tqdm(py_files, desc="Parsing Files (AST)"):
            rel_path = os.path.relpath(file_path, self.root)
            parsed_info = self._parse_python_file(file_path)
            if parsed_info:
                structure[rel_path] = parsed_info
        return structure

    def get_all_tags(self, files_to_process):
        """
        Uses tree-sitter to find all definitions and references in the code,
        creating a list of `Tag` objects.
        """
        all_tags = []
        language = get_language('python')
        parser = get_parser('python')
        query_scm = """
            (class_definition name: (identifier) @name.definition.class) @definition.class
            (function_definition name: (identifier) @name.definition.function) @definition.function
            (call function: [(identifier) @name.reference.call (attribute attribute: (identifier) @name.reference.call)]) @reference.call
        """
        ts_query = language.query(query_scm)

        for fname in tqdm(files_to_process, desc="Scanning Files (tree-sitter)"):
            rel_fname = os.path.relpath(fname, self.root)
            if rel_fname not in self.structure_cache:
                continue

            with open(fname, "r", encoding='utf-8', errors='ignore') as f:
                code = f.read()
            
            tree = parser.parse(bytes(code, "utf-8"))
            captures = ts_query.captures(tree.root_node)

            for node, tag_type in captures:
                kind = "def" if "definition" in tag_type else "ref"
                tag_name = node.text.decode("utf-8")
                
                all_tags.append({
                    "name": tag_name,
                    "kind": kind,
                    "rel_fname": rel_fname,
                    "line": node.start_point[0] + 1,
                })
        return all_tags

    def _add_function_call_nodes(self, G, calls, caller_name):
        """
        Add nodes for function calls and create edges from caller to called functions.
        """
        for call in calls:
            # Check if the called function already exists as a node
            if call not in G:
                # Create a new node for the called function with minimal info
                G.add_node(
                    call,
                    category='external_function',
                    info='',  # No source code available for external functions
                    docstring='',
                    fname='external',
                    line=(0, 0),
                    kind='def'
                )
            
            # Create edge from caller to called function
            if caller_name in G:
                G.add_edge(caller_name, call, label='calls')

    def tags_to_graph(self, tags):
        """
        Constructs the final NetworkX graph from the list of tags, including
        nodes for module-level code with enhanced connectivity.
        """
        G = nx.MultiDiGraph()
        
        definitions = {}
        
        # First pass: Create all definition nodes
        for file_path, structure in self.structure_cache.items():
            # Add class nodes
            for class_def in structure.get('classes', []):
                class_name = class_def['name']
                definitions[class_name] = {'type': 'class', 'file': file_path, **class_def}
                
                # Add method nodes
                for method_def in class_def.get('methods', []):
                    method_full_name = f"{class_name}.{method_def['name']}"
                    definitions[method_full_name] = {'type': 'method', 'file': file_path, 'parent_class': class_name, **method_def}
            
            # Add function nodes
            for func_def in structure.get('functions', []):
                definitions[func_def['name']] = {'type': 'function', 'file': file_path, **func_def}

        # Create nodes for all definitions
        for name, attrs in definitions.items():
            G.add_node(
                name,
                category=attrs['type'],
                info=attrs.get('text', ''),
                docstring=attrs.get('docstring', ''),
                fname=attrs['file'],
                line=(attrs.get('start_line', 0), attrs.get('end_line', 0)),
                kind='def'
            )

        # Second pass: Create module-level code nodes and establish relationships
        for file_path, structure in self.structure_cache.items():
            module_code = structure.get('module_level_code')
            if module_code:
                # Create a unique name for this node
                module_node_name = f"{file_path}::module_code"
                G.add_node(
                    module_node_name,
                    category='module_code',
                    info=module_code,
                    docstring='',
                    fname=file_path,
                    line=(0, 0),
                    kind='def'
                )
                
                # Connect module-level code to all functions and classes defined in the same file
                for class_def in structure.get('classes', []):
                    class_name = class_def['name']
                    if class_name in G:
                        G.add_edge(module_node_name, class_name, label='defines')
                
                for func_def in structure.get('functions', []):
                    func_name = func_def['name']
                    if func_name in G:
                        G.add_edge(module_node_name, func_name, label='defines')
                
                # Add function call nodes and edges from module-level code
                module_calls = structure.get('module_level_calls', [])
                self._add_function_call_nodes(G, module_calls, module_node_name)

        # Third pass: Establish class-function relationships and inheritance
        for file_path, structure in self.structure_cache.items():
            for class_def in structure.get('classes', []):
                class_name = class_def['name']
                
                # Connect class to its methods (bidirectional)
                for method_def in class_def.get('methods', []):
                    method_full_name = f"{class_name}.{method_def['name']}"
                    if G.has_node(class_name) and G.has_node(method_full_name):
                        G.add_edge(class_name, method_full_name, label='contains')
                        G.add_edge(method_full_name, class_name, label='belongs_to')
                    
                    # Add function call nodes and edges from methods
                    method_calls = method_def.get('calls', [])
                    self._add_function_call_nodes(G, method_calls, method_full_name)
                
                # Connect class to inherited classes
                for inherited_class in class_def.get('inherited_classes', []):
                    if inherited_class not in G:
                        # Create node for inherited class if it doesn't exist
                        G.add_node(
                            inherited_class,
                            category='external_class',
                            info='',
                            docstring='',
                            fname='external',
                            line=(0, 0),
                            kind='def'
                        )
                    G.add_edge(class_name, inherited_class, label='inherits_from')
                
                # Connect class to imported/referenced classes
                for imported_class in class_def.get('imported_classes', []):
                    # Only create edges for classes that seem to be actual class references
                    # (filtering out common variable names)
                    if imported_class and imported_class[0].isupper():  # Basic heuristic for class names
                        if imported_class not in G:
                            G.add_node(
                                imported_class,
                                category='external_class',
                                info='',
                                docstring='',
                                fname='external',
                                line=(0, 0),
                                kind='def'
                            )
                        G.add_edge(class_name, imported_class, label='references')
            
            # Add function call nodes and edges from standalone functions
            for func_def in structure.get('functions', []):
                func_name = func_def['name']
                func_calls = func_def.get('calls', [])
                self._add_function_call_nodes(G, func_calls, func_name)

        # Fourth pass: Handle tree-sitter based references (legacy support)
        for tag in tqdm(tags, desc="Building Graph Edges"):
            if tag['kind'] == 'ref':
                caller_scope = self.find_scope(tag['rel_fname'], tag['line'])
                callee_name = tag['name']
                if caller_scope and callee_name in G and G.has_node(caller_scope):
                    # Only add if this edge doesn't already exist
                    if not G.has_edge(caller_scope, callee_name):
                        G.add_edge(caller_scope, callee_name, label='invokes')

        return G
    
    def find_scope(self, file_path, line_number):
        """
        Finds the function, class, or module-level scope that contains a given line number.
        """
        if file_path not in self.structure_cache:
            return None
            
        structure = self.structure_cache[file_path]
        
        # Check functions first
        for func in structure.get('functions', []):
            if func['start_line'] <= line_number <= func['end_line']:
                return func['name']
        
        # Check classes and their methods
        for cls in structure.get('classes', []):
            if cls['start_line'] <= line_number <= cls['end_line']:
                for meth in cls.get('methods', []):
                    if meth['start_line'] <= line_number <= meth['end_line']:
                        return f"{cls['name']}.{meth['name']}"
                return cls['name']
        
        # If not in a function or class, it's in the module-level scope
        if structure.get('module_level_code'):
            return f"{file_path}::module_code"
            
        return None

    def find_files(self, start_dir):
        """
        Finds all Python files in the given directory.
        """
        py_files = []
        for root, _, files in os.walk(start_dir):
            for file in files:
                if file.endswith('.py'):
                    py_files.append(os.path.join(root, file))
        return py_files

    def build_graph(self):
        """
        The main public method to build the full graph.
        """
        print("Finding all Python files in the repository...")
        py_files = self.find_files(self.root)
        
        print("Extracting tags from files using tree-sitter...")
        tags = self.get_all_tags(py_files)
        
        print("Constructing NetworkX graph from tags...")
        graph = self.tags_to_graph(tags)
        
        return graph

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python core/construct_graph.py <directory>")
        sys.exit(1)

    dir_name = sys.argv[1]
    graph_builder = CodeGraph(root=dir_name)
    repo_graph = graph_builder.build_graph()

    print("\n" + "="*50)
    print(f"🏅 Successfully constructed the code graph for '{dir_name}'")
    print(f"   - Nodes: {len(repo_graph.nodes())}")
    print(f"   - Edges: {len(repo_graph.edges())}")
    print("="*50)

    # Print some statistics about the graph
    node_types = {}
    edge_types = {}
    
    for node, attrs in repo_graph.nodes(data=True):
        category = attrs.get('category', 'unknown')
        node_types[category] = node_types.get(category, 0) + 1
    
    for u, v, attrs in repo_graph.edges(data=True):
        label = attrs.get('label', 'unknown')
        edge_types[label] = edge_types.get(label, 0) + 1
    
    print("\nNode Types:")
    for node_type, count in sorted(node_types.items()):
        print(f"   - {node_type}: {count}")
    
    print("\nEdge Types:")
    for edge_type, count in sorted(edge_types.items()):
        print(f"   - {edge_type}: {count}")

    # Save the graph as a pickle file
    graph_output_file = 'graph.pkl'
    with open(graph_output_file, 'wb') as f:
        pickle.dump(repo_graph, f)
    print(f"\n🏅 Saved graph to '{graph_output_file}'")

    # Save the detailed structure as a JSON file
    structure_output_file = 'structure.json'
    with open(structure_output_file, 'w', encoding='utf-8') as f:
        json.dump(graph_builder.structure_cache, f, indent=2)
    print(f"🏅 Saved repository structure to '{structure_output_file}'")