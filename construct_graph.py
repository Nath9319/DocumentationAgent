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
    
        Args:
            node (ast.AST): The root AST node to search for function calls.
    
        Returns:
            list: A list of function or method call names found within the AST node.
    
        Detailed Explanation:
        - Initializes an empty list `calls` to store the names of function/method calls.
        - Iterates over all descendant nodes of the input `node` using `ast.walk(node)`, which traverses the AST tree.
        - For each `child` node:
            - Checks if the node is an instance of `ast.Call`, which represents a function or method call in the AST.
            - If the call is a simple function call (e.g., `foo()`), `child.func` will be an `ast.Name`:
                - Appends the function name (`child.func.id`) to the `calls` list.
            - If the call is a method or attribute call (e.g., `obj.method()`), `child.func` will be an `ast.Attribute`:
                - If the object being called on is a simple name (e.g., `obj.method()`), `child.func.value` is an `ast.Name`:
                    - Appends the fully qualified method name (`obj.method`) to the `calls` list.
                - Otherwise (e.g., chained calls or more complex expressions), appends just the attribute name (`method`) to the `calls` list.
        - Returns the complete list of function and method call names found in thersively extract all function calls from an AST node.
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
        Extracts base classes (inheritance) and imported class references from a class definition AST node.
    
        Args:
            node (ast.ClassDef): The AST node representing a class definition.
    
        Returns:
            tuple: (inherited_classes, imported_classes)
                - inherited_classes (list): Names of base classes the class inherits from.
                - imported_classes (list): Names of other classes referenced in the class body.
    
        Detailed Explanation:
        - Initializes two empty lists: `inherited_classes` to store names of base classes, and `imported_classes` to store names of other referenced classes.
        - Checks if the node has a `bases` attribute (which contains the base classes for the class definition).
            - Iterates over each base in `node.bases`:
                - If the base is a simple name (e.g., `BaseClass`), appends its name (`base.id`) to `inherited_classes`.
                - If the base is an attribute (e.g., `module.BaseClass`), constructs the qualified name and appends it to `inherited_classes`.
        - Walks through all descendant nodes of the class definition using `ast.walk(node)`:
            - For each node, if it is an `ast.Name` and its `id` is not already in `inherited_classes`, appends its name to `imported_classes`.
                - This captures references to other classes in the class body, such as type hints or attribute assignments.
        - Returns a tuple containing the list of inherited class names and the list ofact base classes and imported classes from a class definition.
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
        Parses a single Python file using the `ast` module to extract functions, classes, methods, their docstrings, and any module-level code.
    
        Args:
            file_path (str): The path to the Python file to be parsed.
    
        Returns:
            dict: A dictionary containing extracted information with the following keys:
                - "classes": List of dictionaries with class metadata, methods, docstrings, inheritance, and dependencies.
                - "functions": List of dictionaries with function metadata, docstrings, and called functions.
                - "module_level_code": String of reconstructed module-level code (excluding imports and docstring).
                - "module_level_calls": List of unique function/method calls found at the module level.
    
        Detailed Explanation:
        - Tries to open the file at `file_path` in read mode with UTF-8 encoding, ignoring errors.
        - Reads the file content and parses it into an AST using `ast.parse`.
        - If any exception occurs during file reading or parsing, returns None.
        - Initializes empty containers for class info, function names, class methods, module-level nodes, and module-level calls.
        - Iterates through each top-level node in the parsed AST:
            - If the node is a class definition (`ast.ClassDef`):
                - Extracts base classes and imported class references using `_extract_class_inheritance_and_imports`.
                - Iterates through the class body to find methods (`ast.FunctionDef`):
                    - Extracts function calls within the method using `_extract_function_calls`.
                    - Collects method metadata: name, line numbers, source text, docstring, and calls.
                    - Adds the method name to the set of class methods.
                - Collects class metadata: name, line numbers, source text, methods, docstring, inherited classes, and imported classes.
            - If the node is a top-level function definition (`ast.FunctionDef`):
                - Extracts function calls within the function using `_extract_function_calls`.
                - Collects function metadata: name, line numbers, source text, docstring, and calls.
            - If the node is an import statement (`ast.Import` or `ast.ImportFrom`):
                - Skips it, as imports are not considered executable code for this context.
            - If the node is the first node and is a module-level docstring (`ast.Expr` with `ast.Constant` value):
                - Skips it, as it is not executable code.
            - Otherwise:
                - Treats the node as module-level code (e.g., assignments, function calls).
                - Adds the node to the list of module-level nodes.
                - Extracts function calls from the node and adds them to the module-level calls list.
        - If any module-level nodes were found, reconstructs their source code using `ast.unparse` and joins them into a string.
        - Returns a dictionary with all collected class, function, and module-level information.
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

    Steps and Line-by-Line Explanation:
    - Prints a message indicating that the repository structure is being pre-parsed using AST.
    - Initializes an empty dictionary `structure` to store parsed information for each file.
    - Calls `self.find_files(self.root)` to get a list of all Python file paths in the repository starting from the root directory.
    - Iterates over each Python file path using `tqdm` to show a progress bar labeled "Parsing Files (AST)":
        - Computes the relative path of the file with respect to the repository root using `os.path.relpath`.
        - Calls `self._parse_python_file(file_path)` to parse the file and extract its structure (functions, classes, etc.).
        - If parsing is successful (i.e., `parsed_info` is not None), adds the parsed information to the `structure` dictionary with the relative path as the key.
    - After all files are processed, returns the `structure` dictionary containing parsed data for each Python file in the repository.
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
    
        Args:
            files_to_process (list): List of file paths to process.
    
        Returns:
            list: A list of dictionaries, each representing a tag with its name, kind (def/ref), file, and line number.
    
        Detailed Explanation:
        - Initializes an empty list `all_tags` to store tag information for all files.
        - Retrieves the tree-sitter language and parser for Python using `get_language('python')` and `get_parser('python')`.
        - Defines a tree-sitter query string `query_scm` to match class definitions, function definitions, and function/method calls.
        - Compiles the query using `language.query(query_scm)` to create a `ts_query` object.
        - Iterates over each file in `files_to_process` using `tqdm` to display a progress bar labeled "Scanning Files (tree-sitter)":
            - Computes the relative file path with respect to the repository root using `os.path.relpath`.
            - Skips the file if it is not present in `self.structure_cache`.
            - Opens the file in read mode with UTF-8 encoding, ignoring errors, and reads its content into `code`.
            - Parses the code into a tree-sitter syntax tree using `parser.parse(bytes(code, "utf-8"))`.
            - Runs the compiled query on the root node of the syntax tree to get all captures (matches).
            - Iterates over each `(node, tag_type)` pair in the captures:
                - Determines the kind of tag: "def" if "definition" is in `tag_type`, otherwise "ref".
                - Extracts the tag name from the node's text.
                - Appends a dictionary to `all_tags` with:
                    - "name": the tag name,
                    - "kind": the tag kind ("def" or "ref"),
                    - "rel_fname": the relative file name,
                    - "line": the line number (1-based) where the tag occurs.
        - Returns the complete list of tag dictionaries for all processed files.
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
        Adds nodes for function calls and creates edges from the caller to the called functions in the graph.
    
        Args:
            G (networkx.Graph): The graph object representing the code structure.
            calls (list): A list of function or method names that are called by the caller.
            caller_name (str): The name of the function or method making the calls.
    
        Detailed Explanation:
        - Iterates over each function or method name in the `calls` list.
            - For each call:
                - Checks if the called function already exists as a node in the graph `G`.
                    - If not, adds a new node for the called function with:
                        - category set to 'external_function' (indicating it's not defined in the current codebase),
                        - empty string for source code (`info`),
                        - empty string for docstring,
                        - 'external' as the file name (`fname`),
                        - (0, 0) as the line numbers,
                        - 'def' as the kind.
                - Checks if the caller function (`caller_name`) exists in the graph.
                    - If so, adds an edge from the caller to the called function with the label 'calls'.
        - This ensures that all called functions are represented as nodes (even if external) and that call relationships are captured as edges in the graph.
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

        Args:
            tags (list): List of tag dictionaries, each representing a code definition or reference.

        Returns:
            networkx.MultiDiGraph: The constructed graph representing code structure and relationships.

        Detailed Explanation:
        - Initializes an empty directed multigraph `G` using NetworkX.
        - Initializes an empty dictionary `definitions` to store all code definitions (classes, methods, functions).
        - First pass over all files in `self.structure_cache`:
            - For each class in the file:
                - Adds the class to `definitions` with its metadata.
                - For each method in the class:
                    - Adds the method (with fully qualified name) to `definitions` with its metadata.
            - For each standalone function in the file:
                - Adds the function to `definitions` with its metadata.
        - Adds all definition nodes to the graph `G` with attributes such as category, source code, docstring, file name, line numbers, and kind.
        - Second pass over all files:
            - For each file, if module-level code exists:
                - Adds a node for the module-level code.
                - Connects the module-level node to all classes and functions defined in the same file with 'defines' edges.
                - Adds function call nodes and edges from the module-level code using `_add_function_call_nodes`.
        - Third pass over all files:
            - For each class:
                - Connects the class to its methods with 'contains' and 'belongs_to' edges (bidirectional).
                - Adds function call nodes and edges from each method using `_add_function_call_nodes`.
                - For each inherited class:
                    - Adds a node for the inherited class if it doesn't exist, and connects with an 'inherits_from' edge.
                - For each imported/referenced class (heuristically, names starting with uppercase):
                    - Adds a node if it doesn't exist, and connects with a 'references' edge.
            - For each standalone function:
                - Adds function call nodes and edges from the function using `_add_function_call_nodes`.
        - Fourth pass (legacy support for tree-sitter tags):
            - For each tag of kind 'ref':
                - Finds the caller scope using `find_scope`.
                - If both caller and callee exist in the graph and the edge doesn't already exist, adds an 'invokes' edge.
        - Returns the constructed graph `G`.
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
    
        Args:
            file_path (str): The path to the file being analyzed.
            line_number (int): The line number for which to determine the containing scope.
    
        Returns:
            str or None: The name of the function, method, class, or module-level scope containing the line,
                        or None if no scope is found.
    
        Detailed Explanation:
        - Checks if the file's structure is present in `self.structure_cache`.
            - If not, returns None (scope cannot be determined).
        - Retrieves the parsed structure for the file from the cache.
        - Checks all top-level functions in the file:
            - For each function, if the line number falls within its start and end lines, returns the function's name.
        - Checks all classes in the file:
            - For each class, if the line number falls within its start and end lines:
                - Checks all methods in the class:
                    - If the line number falls within a method's start and end lines, returns the fully qualified method name (ClassName.MethodName).
                - If not in a method but within the class, returns the class name.
        - If the line is not within any function or class, but the file has module-level code, returns a special module-level scope name.
        - If no scope is found, returns None.
        if file_path not in self.structure_cache:
            return None
        """
            
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