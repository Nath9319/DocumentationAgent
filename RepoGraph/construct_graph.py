# This file is adapted from the following sources:
# RepoMap: https://github.com/paul-gauthier/aider/blob/main/aider/repomap.py
# Agentless: https://github.com/OpenAutoCoder/Agentless/blob/main/get_repo_structure/get_repo_structure.py
# grep-ast: https://github.com/paul-gauthier/grep-ast

import os
import sys
import re
import warnings
from collections import namedtuple
import networkx as nx
from tqdm import tqdm
import ast
import pickle
import json
from copy import deepcopy
from utils import create_structure

# tree_sitter is throwing a FutureWarning
warnings.simplefilter("ignore", category=FutureWarning)
from tree_sitter_languages import get_language, get_parser

# --- MODIFIED SEGMENT: Added 'docstring' to the Tag structure ---
Tag = namedtuple("Tag", "rel_fname fname line name kind category info docstring".split())


class CodeGraph:

    warned_files = set()

    def __init__(
        self,
        root=None,
        io=None,
    ):
        self.io = io

        if not root:
            root = os.getcwd()
        self.root = root

        # Pre-parse the structure once
        self.structure = create_structure(self.root)

    def get_code_graph(self, files_to_process):
        if not files_to_process:
            return [], nx.MultiDiGraph()
        
        tags = self.get_all_tags(files_to_process)
        code_graph = self.tags_to_graph(tags)

        return tags, code_graph

    def get_all_tags(self, files_to_process):
        all_tags = []
        for fname in tqdm(files_to_process, desc="Parsing files for graph"):
            rel_fname = os.path.relpath(fname, self.root)
            tags = self.get_tags_for_file(fname, rel_fname)
            all_tags.extend(tags)
        return all_tags

    def tags_to_graph(self, tags):
        G = nx.MultiDiGraph()
        
        # Add definition nodes first
        for tag in tags:
            if tag.kind == 'def':
                # --- MODIFIED SEGMENT: Added 'docstring' to node attributes ---
                G.add_node(
                    tag.name,
                    category=tag.category,
                    info=tag.info,
                    docstring=tag.docstring, # <-- NEW
                    fname=tag.fname,
                    line=tag.line,
                    kind=tag.kind,
                )
        
        # Add edges for references and containment
        for tag in tags:
            if tag.category == 'class' and tag.kind == 'def':
                # The 'info' field for a class tag stores its method names.
                class_methods = tag.info.split('\n')
                for f in class_methods:
                    if G.has_node(tag.name) and G.has_node(f.strip()):
                        G.add_edge(tag.name, f.strip(), label='contains')

            elif tag.kind == 'ref':
                # For references, find the containing scope (function/class)
                # and link it to the definition of what it's calling.
                # Note: This is a simplified logic. A robust implementation
                # would need more precise scope resolution.
                if G.has_node(tag.name):
                    # This logic assumes a simple call graph. For a more accurate graph,
                    # one would need to determine the 'caller' of this 'ref' tag.
                    # For now, we'll skip creating caller->callee edges for simplicity
                    # as the main request is about capturing node data.
                    pass

        return G
    
    def get_tags_for_file(self, fname, rel_fname):
        rel_fname_norm = rel_fname.replace("\\", "/")
        ref_fname_lst = rel_fname_norm.split('/')
        
        s = self.structure
        try:
            for fname_part in ref_fname_lst:
                s = s[fname_part]
        except KeyError:
            print(f"Warning: Path '{rel_fname_norm}' not found in pre-parsed structure, skipping.")
            return []

        structure_classes = {item['name']: item for item in s.get('classes', [])}
        structure_functions = {item['name']: item for item in s.get('functions', [])}
        structure_class_methods = {
            item['name']: item 
            for cls in s.get('classes', []) 
            for item in cls.get('methods', [])
        }
        structure_all_defs = {**structure_functions, **structure_class_methods, **structure_classes}

        lang = 'python' # Hardcoded for this context
        language = get_language(lang)
        parser = get_parser(lang)

        query_scm = """
            (class_definition name: (identifier) @name.definition.class) @definition.class
            (function_definition name: (identifier) @name.definition.function) @definition.function
            (call function: [(identifier) @name.reference.call (attribute attribute: (identifier) @name.reference.call)]) @reference.call
        """

        try:
            with open(str(fname), "r", encoding='utf-8', errors='ignore') as f:
                code = f.read()
        except Exception as e:
            print(f"Warning: Could not read file {fname}: {e}")
            return []

        if not code:
            return []

        tree = parser.parse(bytes(code, "utf-8"))
        query = language.query(query_scm)
        captures = list(query.captures(tree.root_node))

        results = []
        for node, tag_type in captures:
            kind = "def" if tag_type.startswith("name.definition.") else "ref"
            tag_name = node.text.decode("utf-8")

            # We only create tags for definitions we found in the AST pass
            if tag_name in structure_all_defs and kind == 'def':
                def_info = structure_all_defs[tag_name]
                category = 'class' if 'methods' in def_info else 'function'
                info_text = ''
                if category == 'class':
                    info_text = '\n'.join([m['name'] for m in def_info.get('methods', [])])
                else: # It's a function or method
                    info_text = '\n'.join(def_info.get('text', ''))

                # --- MODIFIED SEGMENT: Extract docstring and create the Tag ---
                result = Tag(
                    rel_fname=rel_fname,
                    fname=fname,
                    name=tag_name,
                    kind=kind,
                    category=category,
                    info=info_text,
                    docstring=def_info.get('docstring', ''), # <-- NEW
                    line=tuple([def_info['start_line'], def_info['end_line']]),
                )
                results.append(result)
            elif kind == 'ref':
                # For references, we don't need docstrings, but the Tag needs the field
                result = Tag(
                    rel_fname=rel_fname,
                    fname=fname,
                    name=tag_name,
                    kind=kind,
                    category='unknown', # We don't know if it's a class or function ref without more context
                    info='',
                    docstring='', # <-- NEW (empty for refs)
                    line=tuple([node.start_point[0] + 1, node.end_point[0] + 1]),
                )
                results.append(result)

        return list(set(results)) # Deduplicate tags

    def find_files(self, start_dir):
        py_files = []
        for root, _, files in os.walk(start_dir):
            for file in files:
                if file.endswith('.py'):
                    py_files.append(os.path.join(root, file))
        return py_files


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python construct_graph.py <directory>")
        sys.exit(1)

    dir_name = sys.argv[1]
    code_graph = CodeGraph(root=dir_name)
    py_files = code_graph.find_files(dir_name)

    tags, G = code_graph.get_code_graph(py_files)

    print("---------------------------------")
    print(f"🏅 Successfully constructed the code graph for repo directory {dir_name}")
    print(f"   Number of nodes: {len(G.nodes)}")
    print(f"   Number of edges: {len(G.edges)}")
    print("---------------------------------")

    with open(f'{os.getcwd()}/graph.pkl', 'wb') as f:
        pickle.dump(G, f)
    
    # Save tags with the new docstring field
    tags_with_docstrings = []
    for tag in tags:
        tags_with_docstrings.append(tag._asdict())

    with open(f'{os.getcwd()}/tags.json', 'w') as f:
        json.dump(tags_with_docstrings, f, indent=2)

    print(f"🏅 Successfully cached code graph and node tags (with docstrings) in '{os.getcwd()}'")

