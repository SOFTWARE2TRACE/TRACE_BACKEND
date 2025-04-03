import json
import sys
from backend.Crawler import Crawler

if __name__ == "__main__":
    config_json = sys.argv[1]
    # config_json = {"TargetURL": "www.google.com/",
    #  "CrawlDepth": 100,
    #  "PageNumberLimit": 200,
    #  "UserAgent": "Mozilla/5.0",
    #  "RequestDelay": 20000}
    config = json.loads(config_json)
    crawler = Crawler(config_json)
    crawler.processResponse()
    crawler.tree_creator.display_data()
    # print(json.dumps(result))