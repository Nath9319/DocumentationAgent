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

        # --- A more robust way to capture all module-level code ---
        # We iterate through the top-level nodes of the file's AST.
        for i, node in enumerate(parsed_data.body):
            if isinstance(node, ast.ClassDef):
                methods = []
                for n in node.body:
                    if isinstance(n, ast.FunctionDef):
                        # This is a method within the class
                        methods.append({
                            "name": n.name,
                            "start_line": n.lineno,
                            "end_line": getattr(n, 'end_lineno', n.lineno),
                            "text": ast.unparse(n),
                            "docstring": ast.get_docstring(n) or ""
                        })
                        class_methods.add(n.name)
                class_info.append({
                    "name": node.name,
                    "start_line": node.lineno,
                    "end_line": getattr(node, 'end_lineno', node.lineno),
                    "text": ast.unparse(node),
                    "methods": methods,
                    "docstring": ast.get_docstring(node) or ""
                })

            elif isinstance(node, ast.FunctionDef):
                # This is a top-level function
                function_names.append({
                    "name": node.name,
                    "start_line": node.lineno,
                    "end_line": getattr(node, 'end_lineno', node.lineno),
                    "text": ast.unparse(node),
                    "docstring": ast.get_docstring(node) or ""
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

        module_level_code_str = ""
        if module_level_nodes:
            # Reconstruct the module-level code from the collected nodes
            module_level_code_str = "\n".join([ast.unparse(n) for n in module_level_nodes])

        return {
            "classes": class_info,
            "functions": function_names,
            "module_level_code": module_level_code_str
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

    def tags_to_graph(self, tags):
        """
        Constructs the final NetworkX graph from the list of tags, including
        nodes for module-level code.
        """
        G = nx.MultiDiGraph()
        
        definitions = {}
        for file_path, structure in self.structure_cache.items():
            for class_def in structure.get('classes', []):
                definitions[class_def['name']] = {'type': 'class', 'file': file_path, **class_def}
                for method_def in class_def.get('methods', []):
                    definitions[f"{class_def['name']}.{method_def['name']}"] = {'type': 'method', 'file': file_path, **method_def}
            for func_def in structure.get('functions', []):
                definitions[func_def['name']] = {'type': 'function', 'file': file_path, **func_def}

        for name, attrs in definitions.items():
            G.add_node(
                name,
                category=attrs['type'],
                info=attrs['text'],
                docstring=attrs.get('docstring', ''),
                fname=attrs['file'],
                line=(attrs['start_line'], attrs['end_line']),
                kind='def'
            )

        # --- Add nodes for module-level code ---
        for file_path, structure in self.structure_cache.items():
            module_code = structure.get('module_level_code')
            if module_code:
                # Create a unique name for this node
                node_name = f"{file_path}::module_code"
                G.add_node(
                    node_name,
                    category='module_code',
                    info=module_code,
                    docstring='', # No formal docstring for module code
                    fname=file_path,
                    line=(0, 0), # Line numbers are for the whole block
                    kind='def'
                )

        for tag in tqdm(tags, desc="Building Graph Edges"):
            if tag['kind'] == 'ref':
                caller_scope = self.find_scope(tag['rel_fname'], tag['line'])
                callee_name = tag['name']
                if caller_scope and callee_name in G and G.has_node(caller_scope):
                    G.add_edge(caller_scope, callee_name, label='invokes')
        
        for class_name, attrs in definitions.items():
            if attrs['type'] == 'class':
                for method in attrs.get('methods', []):
                    method_full_name = f"{class_name}.{method['name']}"
                    if G.has_node(class_name) and G.has_node(method_full_name):
                        G.add_edge(class_name, method_full_name, label='contains')

        return G
    
    def find_scope(self, file_path, line_number):
        """
        Finds the function, class, or module-level scope that contains a given line number.
        """
        if file_path not in self.structure_cache:
            return None
            
        structure = self.structure_cache[file_path]
        
        for func in structure.get('functions', []):
            if func['start_line'] <= line_number <= func['end_line']:
                return func['name']
        
        for cls in structure.get('classes', []):
            if cls['start_line'] <= line_number <= cls['end_line']:
                for meth in cls.get('methods', []):
                    if meth['start_line'] <= line_number <= meth['end_line']:
                        return f"{cls['name']}.{meth['name']}"
                return cls['name']
        
        # --- If not in a function or class, it's in the module-level scope ---
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
    

def generate_structure_json(repo_path: str, output_path: str = "structure.json"):
    """
    Public utility to generate structure.json from a given repo path.
    """
    graph_builder = CodeGraph(root=repo_path)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(graph_builder.structure_cache, f, indent=2)
    print(f" structure.json saved at: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python core/construct_graph.py <directory>")
        sys.exit(1)

    dir_name = sys.argv[1]
    graph_builder = CodeGraph(root=dir_name)
    repo_graph = graph_builder.build_graph()

    print("\n" + "="*50)
    print(f"Successfully constructed the code graph for '{dir_name}'")
    print(f"   - Nodes: {len(repo_graph.nodes())}")
    print(f"   - Edges: {len(repo_graph.edges())}")
    print("="*50)

    # --- THIS IS THE FIX: Save the graph and the structure cache ---
    # Save the graph as a pickle file
    graph_output_file = 'pickle_graph.pkl'
    with open(graph_output_file, 'wb') as f:
        pickle.dump(repo_graph, f)
    print(f" Saved graph to '{graph_output_file}'")

    # Save the detailed structure as a JSON file
    structure_output_file = 'structure.json'
    with open(structure_output_file, 'w', encoding='utf-8') as f:
        json.dump(graph_builder.structure_cache, f, indent=2)
    print(f" Saved repository structure to '{structure_output_file}'")