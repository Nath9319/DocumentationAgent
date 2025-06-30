# File: core/construct_graph.py
#
# This script is the heart of the repository analysis engine. It combines AST
# parsing and tree-sitter queries to build a comprehensive, directed graph
# of the entire codebase. This version is customized to:
#   - Be self-contained by integrating the parsing logic.
#   - Capture docstrings for every class and function, which is critical
#     for the documentation agent.
#   - Create a detailed graph representing calls and containment.

import os
import sys
import warnings
import ast
import pickle
import json
from collections import namedtuple
import networkx as nx
from tqdm import tqdm

# tree_sitter is a powerful parser for creating concrete syntax trees.
warnings.simplefilter("ignore", category=FutureWarning)
from tree_sitter_languages import get_language, get_parser

# The Tag is the structured representation of a single code element (def or ref).
# The 'docstring' field is essential for our agent.
Tag = namedtuple("Tag", "rel_fname fname line name kind category info docstring".split())

class CodeGraph:
    """
    Analyzes a code repository and constructs a detailed dependency graph.
    """

    def __init__(self, root=None):
        if not root:
            root = os.getcwd()
        self.root = root
        # The structure cache will hold the AST-parsed info for all files.
        self.structure_cache = self._pre_parse_all_files()

    def _parse_python_file(self, file_path):
        """
        Parses a single Python file using the `ast` module to extract
        functions, classes, methods, and their docstrings. This is the
        foundation for our node attributes.

        This logic is integrated from your `utils.py`.
        """
        try:
            with open(file_path, "r", encoding='utf-8', errors='ignore') as file:
                file_content = file.read()
                parsed_data = ast.parse(file_content)
        except Exception as e:
            # print(f"Warning: AST parsing failed for {file_path}: {e}")
            return None

        class_info = []
        function_names = []
        class_methods = set()

        for node in ast.walk(parsed_data):
            if isinstance(node, ast.ClassDef):
                methods = []
                for n in node.body:
                    if isinstance(n, ast.FunctionDef):
                        methods.append({
                            "name": n.name,
                            "start_line": n.lineno,
                            "end_line": n.end_lineno,
                            "text": ast.unparse(n),
                            "docstring": ast.get_docstring(n) or ""
                        })
                        class_methods.add(n.name)
                class_info.append({
                    "name": node.name,
                    "start_line": node.lineno,
                    "end_line": node.end_lineno,
                    "text": ast.unparse(node),
                    "methods": methods,
                    "docstring": ast.get_docstring(node) or ""
                })
            elif isinstance(node, ast.FunctionDef) and node.name not in class_methods:
                function_names.append({
                    "name": node.name,
                    "start_line": node.lineno,
                    "end_line": node.end_lineno,
                    "text": ast.unparse(node),
                    "docstring": ast.get_docstring(node) or ""
                })
        
        return {
            "classes": class_info,
            "functions": function_names,
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
        # This query finds class/function definitions and function calls.
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
        Constructs the final NetworkX graph from the list of tags.
        """
        G = nx.MultiDiGraph()
        
        # Create a mapping from names to their definition tags
        definitions = {}
        for file_path, structure in self.structure_cache.items():
            for class_def in structure.get('classes', []):
                definitions[class_def['name']] = {'type': 'class', 'file': file_path, **class_def}
                for method_def in class_def.get('methods', []):
                    # Store method as ClassName.method_name for uniqueness
                    definitions[f"{class_def['name']}.{method_def['name']}"] = {'type': 'method', 'file': file_path, **method_def}
            for func_def in structure.get('functions', []):
                definitions[func_def['name']] = {'type': 'function', 'file': file_path, **func_def}

        # Add all definitions as nodes to the graph
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

        # Add edges based on references and containment
        for tag in tqdm(tags, desc="Building Graph Edges"):
            if tag['kind'] == 'ref':
                caller_scope = self.find_scope(tag['rel_fname'], tag['line'])
                callee_name = tag['name']
                if caller_scope and callee_name in G and G.has_node(caller_scope):
                    G.add_edge(caller_scope, callee_name, label='invokes')
        
        # Add 'contains' edges for class methods
        for class_name, attrs in definitions.items():
            if attrs['type'] == 'class':
                for method in attrs.get('methods', []):
                    method_full_name = f"{class_name}.{method['name']}"
                    if G.has_node(class_name) and G.has_node(method_full_name):
                        G.add_edge(class_name, method_full_name, label='contains')

        return G
    
    def find_scope(self, file_path, line_number):
        """
        Finds the function or class that contains a given line number in a file.
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
                # It's inside a class, check methods
                for meth in cls.get('methods', []):
                    if meth['start_line'] <= line_number <= meth['end_line']:
                        return f"{cls['name']}.{meth['name']}"
                return cls['name'] # It's in the class body but not in a method
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

    output_file = 'graph.pkl'
    with open(output_file, 'wb') as f:
        pickle.dump(repo_graph, f)
    
    print(f"🏅 Saved graph to '{output_file}'")
