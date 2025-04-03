class Tree:
    def __init__(self) -> None:
        self.root = None
        self.dir_tree = {}
    
    def add_vertex(self, vertex) -> None:
        if not self.dir_tree:  # if current tree is empty, the vertex is the root:
            self.root = vertex
        if vertex not in self.dir_tree:
            self.dir_tree[vertex] = []

    def add_edge(self, src, dest) -> None:
        if src not in self.dir_tree:
            self.add_vertex(src)
        if dest not in self.dir_tree:
            self.add_vertex(dest)
        self.dir_tree[src].append(dest)
    
    def remove_edge(self, src, dest) -> None:
        if src in self.dir_tree and dest in self.dir_tree[src]:
            self.dir_tree[src].remove(dest)
    
    def remove_vertex(self, vertex) -> None:
        if vertex in self.dir_tree:
            del self.dir_tree[vertex]
        for v in self.dir_tree:
            if vertex in self.dir_tree[v]:
                self.dir_tree[v].remove(vertex)
    
    def has_edge(self, src, dest) -> None:
        return src in self.dir_tree and dest in self.dir_tree[src]
    
    def has_vertex(self, vertex) -> None:
        return vertex in self.dir_tree