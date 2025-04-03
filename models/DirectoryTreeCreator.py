from models.Tree import Tree
from services.utils import getURL, getIP  # helper functions that did not really belong in this class

"""
# Crawler data will have this format:
let networkMap = [
    {
        url: "www.google.com",
        path: "/",
        children: [
            {
                url: "www.google.com/search",
                path: "/search",
                children: [
                    {
                        url: "www.google.com/search/search",
                        path: "/search/search",
                        children: []
                    }
                ]
            }
        ]
    }
];
"""

class DirectoryTreeCreator:
    def __init__(self, tree = Tree()) -> None:
        self.tree = tree

    def get_tree(self) -> Tree:  # function from srs
        return self.tree

    def reset(self) -> None:  # function from srs
        self.tree = Tree()

    def populate(self, crawl_data: dict, display=False) -> None:  # recursively populates the tree (which has a graph structure)
        # TODO display the tree as it is being built (we might require the indent parameter like the display_pretty function)
        for node in crawl_data:
            url = node.get('url')
            path = node.get('path')
            children = node.get('children')
            vertex = (
                url,
                path
            )
            for child_node in children:
                child_url = child_node.get('url')
                child_path = child_node.get('path')
                child_vertex = (
                    child_url,
                    child_path
                )
                self.tree.add_edge(vertex, child_vertex)
            self.populate(children)

    def add_edge(self, src: tuple[str, str], dst: tuple[str, str], display=False) -> None:  # wrapper for add_edge on the tree structure
        if not isinstance(src, tuple) or len(src) != 2:
            raise ValueError(f"Vertex {src} is not properly formatted! Format should be a tuple of the form: (url, path)")
        if not isinstance(dst, tuple) or len(dst) != 2:
            raise ValueError(f"Vertex {dst} is not properly formatted! Format should be a tuple of the form: (url, path)")
        self.tree.add_edge(src, dst)

        if display:  # TODO display the tree as it is being built (we might require the indent parameter like the display_pretty function)
            pass

    def display_data(self) -> None:  # displays all the data currently stored
        for vertex in self.tree.dir_tree:
            print(f"{getURL(vertex)}  {self.tree.dir_tree[vertex]}")

    def display_pretty(self, root, indent="") -> None:  # displays the data starting from a specified root
        children = self.tree.dir_tree[root]
        if children:
            print(f"{indent}{getURL(root)} --> ")
        else:
            print(f"{indent}{getURL(root)}")

        for child in children:
            if child in self.tree.dir_tree:
                self.display_pretty(child, f"{indent}\t")
            else:
                raise ValueError(f"Vertex {child} was found as a children of {root}, but it was not found on the graph!")

    def get_tree_map(self, root) -> list:
        children = self.tree.dir_tree.get(root, [])
        children_list = []
        for child in children:
             children_list.append(self.get_tree_map_children(child))
        node_map = [{
            "ip": getIP(root),
            "path": getURL(root),
            "children": children_list
        }]
        return node_map

    def get_tree_map_children(self, child):
        children = self.tree.dir_tree.get(child)
        children_list = []
        for grandchild in children:
            children_list.append(self.get_tree_map_children(grandchild))
        node_map = {
            "ip": getIP(child),
            "path": getURL(child),
            "children": children_list
        }
        return node_map
