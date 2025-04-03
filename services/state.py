# state.py
from routers.treestructuremanager import TreeStructureManager

tree_data = []

def init_tree_manager():
    manager = TreeStructureManager()
    manager.initialize()
    return manager