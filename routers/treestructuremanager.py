import re
from urllib.parse import urlparse

class TreeStructureManager:
    def __init__(self):
     self.tree_structure = {}

    def initialize(self):
        """
        Initializes an empty tree structure.
        @requires(Crawler.has_executed_successfully() and DirectoryBruteForcer.has_executed_successfully())
        @ensures(self.tree_structure is not None)
        """
        self.tree_structure = {}

    def add_url(self, url: str):
        """
        Parses the URL and inserts its domain and path segments into the nested dictionary.
        @requires(url is not None and isinstance(url, str))
        @ensures(url in self.tree_structure)  # conceptually, the domain/path is represented in the structure
        """
        if not url or not isinstance(url, str):
            raise ValueError("URL must be a non-empty string.")

        parsed = urlparse(url)
        domain = parsed.netloc
        path = parsed.path.strip("/")

        # If there's no domain, fallback to using the entire URL as the key.
        if not domain:
            domain = parsed.path
            path = ""

        segments = [seg for seg in path.split("/") if seg]

        # Insert into the tree
        current_node = self.tree_structure
        if domain not in current_node:
            current_node[domain] = {}
        current_node = current_node[domain]

        for seg in segments:
            if seg not in current_node:
                current_node[seg] = {}
            current_node = current_node[seg]

    def add_directory(self, path: str):
        """
        Adds a directory into the tree structure based on a given path.
        @requires(path is not None and isinstance(path, str))
        @ensures(path in self.tree_structure)
        """
        if not path or not isinstance(path, str):
            raise ValueError("Path must be a non-empty string.")
        parts = path.strip("/").split("/")
        current = self.tree_structure
        for part in parts:
            if part not in current:
                current[part] = {}
            current = current[part]

    def add_file(self, path: str, filename: str):
        """
        Adds a file under the specified directory node.
        @requires(path is not None and filename is not None)
        @ensures(filename in self.tree_structure[path])
        """
        if not path or not filename:
            raise ValueError("Both path and filename must be non-empty strings.")
        parts = path.strip("/").split("/")
        current = self.tree_structure
        for part in parts:
            if part not in current:
                current[part] = {}
            current = current[part]
        # Represent the file as a key with a value of None.
        current[filename] = None

    def remove_node(self, path: str):
        """
        Removes a node (directory or file) from the tree.
        @requires(path in self.tree_structure)
        @ensures(path not in self.tree_structure)
        """
        if not path or not isinstance(path, str):
            raise ValueError("Path must be a non-empty string.")
        parts = path.strip("/").split("/")

        def _remove(current: dict, parts_list: list) -> bool:
            if len(parts_list) == 1:
                key = parts_list[0]
                if key in current:
                    del current[key]
                    return True
                return False
            key = parts_list[0]
            if key not in current or not isinstance(current[key], dict):
                return False
            removed = _remove(current[key], parts_list[1:])
            if removed and not current[key]:
                del current[key]
            return removed

        success = _remove(self.tree_structure, parts)
        if not success:
            raise KeyError(f"Path '{path}' not found in the tree structure.")

    def get_structure(self) -> dict:
        """
        Returns the current hierarchical structure as a nested dictionary.
        @requires(self.tree_structure is not None)
        @ensures(return instanceof Dictionary)
        """
        return self.tree_structure

    @staticmethod
    def dict_to_tree_nodes(name: str, node: dict) -> dict:
        """
        Recursively converts a dictionary node into a { "name": ..., "children": [...] } structure,
        which is a common format for tree viewer components.
        """
        children = []
        for key, val in node.items():
            if isinstance(val, dict):
                children.append(TreeStructureManager.dict_to_tree_nodes(key, val))
            else:
                children.append({"name": key, "children": []})
        return {"name": name, "children": children}

    def get_tree_nodes(self) -> list:
        """
        Converts the entire tree structure into a list of tree nodes (one per domain).
        """
        roots = []
        for domain, subdict in self.tree_structure.items():
            roots.append(TreeStructureManager.dict_to_tree_nodes(domain, subdict))
        return roots


# Demo usage if run as a script:
if __name__ == '__main__':
    manager = TreeStructureManager()
    
    import pprint
    print("Initial tree structure (nested dictionary):")
    pprint.pprint(manager.get_structure(), width=120)
    
    print("\nTree structure in node-based format:")
    tree_nodes = manager.get_tree_nodes()
    pprint.pprint(tree_nodes, width=120)
    
    # Example removal:
    manager.remove_node("192.168.1.25:8080/quests/shareform")
    print("\nAfter removing 'quests/shareform':")
    pprint.pprint(manager.get_structure(), width=120)
    
    # Adding a file under a directory:
    manager.add_file("192.168.1.25:8080/quests", "new_file.txt")
    print("\nAfter adding 'new_file.txt' under 'quests':")
    pprint.pprint(manager.get_structure(), width=120)
