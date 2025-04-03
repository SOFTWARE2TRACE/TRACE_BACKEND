from typing import Dict, Any
from DirectoryTreeCreator import DirectoryTreeCreator

class Crawler:
    # Class-level default config to match Crawler.py
    default_config = {
        "TargetURL": "",
        "CrawlDepth": 10,
        "PageNumberLimit": 20,
        "UserAgent": "",
        "RequestDelay": 2000
    }

    def __init__(self):
        """
        Initialize the Crawler with storage for Task 4’s results and tree.
        """
        # Task 4: Storage for crawl results
        self.op_results: Dict[str, Any] = {}
        # Task 4: Storage for the directory tree
        self.tree = DirectoryTreeCreator()
        # Config initialization to match Crawler.py’s default behavior
        self.config: Dict[str, Any] = self.default_config

    def getCrawlResults(self) -> Dict[str, Any]:
        """
        Returns the stored crawl results.
        Fulfills Contract 2: "Get results" - Knows the responses received from machines.
        
        Returns:
            Dict[str, Any]: A dictionary mapping paths to their responses.
        Pre-condition: op_results must not be None (ensured by initialization).
        Post-condition: Returns a non-null dictionary (empty if no results).
        """
        if self.op_results is None:
            return {}
        return self.op_results

    def getTree(self) -> 'Tree':
        """
        Returns the Tree object managed by DirectoryTreeCreator.
        Fulfills Contract 2: "Get results" - Knows the current tree structure.
        
        Returns:
            Tree: The graph structure representing the crawled directory tree.
        Pre-condition: tree must not be None (ensured by initialization).
        Post-condition: Returns a non-null Tree instance.
        """
        return self.tree.get_tree()