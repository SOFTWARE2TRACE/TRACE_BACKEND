import socket
from typing import Dict, Any
import time
from urllib.parse import urljoin, urlparse
# Removed:import requests
from bs4 import BeautifulSoup

from models.DirectoryTreeCreator import DirectoryTreeCreator

class Crawler:
    config = dict()
    default_config =  {
            "TargetURL": "www.example.com",
            "CrawlDepth": 10,
            "PageNumberLimit": int(20),
            "UserAgent": "",
            "RequestDelay": 1000
        }
    def __init__(self, config = None, http_client=None):
        # Handle empty or None config by resetting to defaults
        if config is None or len(config) == 0:
            self.reset()
        else:
            # Validate that all required config keys are present
            for key in self.default_config.keys():
                if key not in config:
                    raise KeyError("Invalid config dictionary")
            try:
                # Set config with type conversion for numeric values
                self.config = {
                    "TargetURL": config["TargetURL"],
                    "CrawlDepth": int(config["CrawlDepth"]),
                    "PageNumberLimit": int(config["PageNumberLimit"]),
                    "UserAgent": config["UserAgent"],
                    "RequestDelay": float(config["RequestDelay"]),
                }
            except ValueError as e:
                raise ValueError(f"Invalid config values: {e}")

        # Dictionary to store raw HTML responses {path: response}
        self.op_results: Dict[str, Any] = {}
        # Set to track visited URLs and avoid duplicates
        self.visited_urls = set()
        # Counter for number of pages crawled
        self.page_count = 0
        # Instance of DirectoryTreeCreator to manage the tree structure
        self.tree_creator = DirectoryTreeCreator()
        # Current crawl depth (not used in this version but kept for consistency)
        self.curr_depth = 0
        # HTTPClient instance from Subsystem 1 for making requests
        self.client = http_client
        if self.client is None:
            raise ValueError("HTTPClient instance required")

    # def startCrawl(self):
    #
    #     self.tree_creator = DirectoryTreeCreator()
    #     curr_dir = self.config["TargetURL"]
    #
    #     try:
    #         req = requests.get(curr_dir, headers={'User-Agent': self.config['UserAgent']})
    #         if req.status_code == 200:
    #             print(f"Currently crawling: {curr_dir}")
    #
    #             root_node = {
    #                 "url": curr_dir,
    #                 "ip": socket.gethostbyname(urlparse(curr_dir).hostname),
    #                 "children": []
    #             }
    #             self.processResponse(curr_dir, req.text, root_node, depth=1)
    #         else:
    #             print(f"[ERROR] Failed to access target URL: {req.status_code}")
    #     except Exception as e:
    #         print(f"[ERROR] Connection error: {e}")
    #
    # def processResponse(self, curr_dir: str, response: str, parent_node=None, depth=1, page_count=0):
    #     if curr_dir in self.visited_urls:
    #         return
    #
    #     if depth > self.config['CrawlDepth']:
    #         return
    #
    #     if page_count > self.config['PageNumberLimit']:
    #         return
    #
    #     self.op_results[curr_dir] = response
    #     self.visited_urls.add(curr_dir)
    #
    #
    #     soup = BeautifulSoup(response, 'html.parser')
    #     links = [a.get('href') for a in soup.find_all('a', href=True)]
    #
    #     valid_links = []
    #     for link in links:
    #         parsed = urlparse(link)
    #         if parsed.scheme in ["http", "https"]:
    #             valid_links.append(link)
    #         elif parsed.scheme == "":
    #             valid_links.append(urljoin(curr_dir, link))
    #
    #     for next_url in valid_links:
    #         if next_url in self.visited_urls:
    #             continue
    #
    #         if page_count >= self.config['PageNumberLimit']:
    #             print(f"Depth limit reached")
    #             return
    #
    #         time.sleep(self.config['RequestDelay'] / 1000)
    #
    #         try:
    #             print(f"Currently crawling: {next_url}")
    #             req = requests.get(next_url, headers={'User-Agent': self.config['UserAgent']})
    #             if req.status_code == 200:
    #                 page_count += 1
    #                 node = {
    #                     "url": next_url,
    #                     "ip": socket.gethostbyname(urlparse(next_url).hostname),
    #                     "children": []
    #                 }
    #
    #                 if parent_node is not None:
    #                     if node not in parent_node["children"]:
    #                         parent_node["children"].append(node)
    #
    #                         parent = (parent_node["url"], parent_node["ip"])
    #                         child = (node["url"], node["ip"])
    #
    #                         if child not in self.tree_creator.tree.dir_tree.get(parent, []):
    #                             self.tree_creator.add_edge(parent, child)
    #
    #                 self.processResponse(next_url, req.text, node, depth + 1, page_count)
    #             else:
    #                 print(f"NOTE: Failed to crawl {next_url}: {req.status_code}")
    #         except Exception as e:
    #             print(f"Error: Failed to crawl {next_url}: {e}")

    def start_crawl(self):
        self.tree_creator.reset()
        curr_dir = self.config["TargetURL"]
        response = self.send_request(curr_dir)
        parent_node = {
            "url": curr_dir,
            "ip": socket.gethostbyname(urlparse(curr_dir).hostname),
            "children": []
        }
        self.process_response(response, parent_node, curr_dir, depth_count=0)

    def process_response(self, response, parent_node, curr_dir, depth_count=0):
        print(f"Depth: {depth_count}, URL: {curr_dir}")

        if depth_count >= self.config['CrawlDepth']:
            return
        if self.page_count >= self.config['PageNumberLimit']:
            return

        links = self.get_valid_links(response, curr_dir)

        for link in links:
            if self.page_count >= self.config['PageNumberLimit']:
                return
            if link in self.visited_urls:
                continue

            response = self.send_request(link)
            if not response:
                continue

            node = {
                "url": link,
                "ip": socket.gethostbyname(urlparse(link).hostname),
                "children": []
            }

            if parent_node is not None:
                if node not in parent_node["children"]:
                    parent_node["children"].append(node)

                    parent = (parent_node["url"], parent_node["ip"])
                    child = (node["url"], node["ip"])

                    if child not in self.tree_creator.tree.dir_tree.get(parent, []):
                        self.tree_creator.add_edge(parent, child)

            self.process_response(response, node, link, depth_count + 1)

    def send_request(self, curr_dir):
        if self.page_count >= self.config['PageNumberLimit']:
            return None
        time.sleep(self.config['RequestDelay']/1000)
        try:
            self.client.send_request(curr_dir, None, "GET", {'User-Agent': self.config['UserAgent']})
            response = self.client.receive_response()
            if response and response.status_code == 200:
                print(f"Currently crawling: {curr_dir}")
                self.op_results[curr_dir] = response.body
                self.visited_urls.add(curr_dir)
                self.page_count += 1
                if self.tree_creator.tree.root is not None:
                    self.update_crawler_data(self.visited_urls, self.tree_creator.get_tree_map(self.tree_creator.tree.root))
                return response.body
            else:
                print(f"[ERROR] Failed to access {curr_dir}: {response.status_code if response else 'No response'}")
        except Exception as e:
            print(f"[ERROR] Connection error: {e}")
        return None

    def get_valid_links(self, response: str, curr_dir):
        if not response:  # Handle None or empty response
            return []
        soup = BeautifulSoup(response, 'html.parser')
        links = [a.get('href') for a in soup.find_all('a', href=True)]
        links = [link for link in links if not link.startswith("#")]
        page_count = 0
        valid_links = []
        for link in links:
            if page_count >= self.config['PageNumberLimit']:
                return valid_links

            parsed = urlparse(link)
            if parsed.scheme in ["http", "https"]:
                valid_links.append(link)
            elif parsed.scheme == "":
                valid_links.append(urljoin(curr_dir, link))
            page_count += 1
        print("valid links", valid_links)
        return valid_links

    def update_crawler_data(self, links, crawler_data):
        from routers.api_endpoints import set_crawler_data, set_crawler_links
        # Update crawler data and links in real-time
        set_crawler_links(links)
        set_crawler_data(crawler_data)
        print(f"Updated crawler data:")

    def getConfig(self):
        if self.config is None:
            self.reset()
            raise ValueError("Config cannot be None, resetting to default")
        elif len(self.config) == 0:
            self.reset()
            raise ValueError("Config cannot be an empty list, resetting to default")
        elif self.config is not None:
            return self.config

    def setConfig(self, config):
        if config is None:
            self.reset()
            raise ValueError("Config cannot be None, resetting to default")
        elif len(config) == 0:
            self.reset()
            raise ValueError("Config cannot be an empty list, resetting to default")
        elif config is not None:
            self.config = config
    def reset(self):
        self.config = None
        self.config = self.default_config
        self.op_results = {} #reset operation results
        self.visited_urls = set() #reset curr list of visited urls
        self.page_count = 0 #reset pages count
        self.tree_creator = DirectoryTreeCreator() #reset tree
        
    def getCrawlResults(self) -> list[str]:
        #Return a list of URLs that have been crawled
        #Sample usage (urls = crawler.getCrawlResults())
        return list(self.op_results.keys())
    
    def getTree(self):
        #Ensures getTree matches the SRS and provides the full tree structure, not just visited URLs.
        return self.tree_creator.get_tree_map(self.tree_creator.tree.root)
    def getDefaultConfig(self):
        return self.default_config
