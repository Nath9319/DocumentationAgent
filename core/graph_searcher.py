# File: core/graph_searcher.py
#
# This class provides a suite of tools for querying and traversing the
# repository graph built by `construct_graph.py`. This version is customized
# with specific methods for finding code dependencies and references, which
# are essential for the documentation agent's logic.

import networkx as nx

class RepoSearcher:
    """A class to perform searches and traversals on a repository code graph."""

    def __init__(self, graph: nx.MultiDiGraph):
        """
        Initializes the RepoSearcher with a NetworkX graph.

        Args:
            graph (nx.MultiDiGraph): The repository code graph.
        """
        self.graph = graph

    def get_dependencies(self, node_name: str) -> list[str]:
        """
        Finds all nodes that the given node directly calls or contains.
        This is useful for understanding what a function/class relies on.

        Args:
            node_name (str): The name of the node to find dependencies for.

        Returns:
            list[str]: A list of node names that are successors of the given node.
        """
        if node_name not in self.graph:
            return []
        # Successors are nodes that the current node has an edge pointing TO.
        return list(self.graph.successors(node_name))

    def get_references(self, node_name: str) -> list[str]:
        """
        Finds all nodes that directly call the given node.
        This is useful for understanding how and where a function/class is used.

        Args:
            node_name (str): The name of the node to find references for.

        Returns:
            list[str]: A list of node names that are predecessors of the given node.
        """
        if node_name not in self.graph:
            return []
        # Predecessors are nodes that have an edge pointing FROM them TO the current node.
        return list(self.graph.predecessors(node_name))

    def dfs_traversal(self, start_node: str, depth_limit: int = 5) -> list[str]:
        """
        Performs a depth-first search (DFS) traversal from a starting node.
        Explores as far as possible along each branch before backtracking.

        Args:
            start_node (str): The node to begin the traversal from.
            depth_limit (int): The maximum depth to explore.

        Returns:
            list[str]: A list of visited nodes in the order they were discovered.
        """
        if start_node not in self.graph:
            return []
            
        visited = []
        stack = [(start_node, 0)]
        while stack:
            node, level = stack.pop()
            if node not in visited:
                visited.append(node)
                if level < depth_limit:
                    # We reverse the neighbors to maintain a more intuitive
                    # left-to-right exploration order from the original source code.
                    neighbors = reversed(list(self.graph.successors(node)))
                    for neighbor in neighbors:
                        if neighbor not in visited:
                            stack.append((neighbor, level + 1))
        return visited

    def bfs_traversal(self, start_node: str, depth_limit: int = 5) -> list[str]:
        """
        Performs a breadth-first search (BFS) traversal from a starting node.
        Explores all neighbors at the present depth prior to moving on to nodes
        at the next depth level.

        Args:
            start_node (str): The node to begin the traversal from.
            depth_limit (int): The maximum depth to explore.

        Returns:
            list[str]: A list of visited nodes in the order they were discovered.
        """
        if start_node not in self.graph:
            return []

        visited = []
        queue = [(start_node, 0)]
        
        while queue:
            node, level = queue.pop(0)
            if node not in visited:
                visited.append(node)
                if level < depth_limit:
                    for neighbor in self.graph.successors(node):
                        if neighbor not in visited:
                            queue.append((neighbor, level + 1))
        return visited
