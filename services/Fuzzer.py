import random
from typing import Dict, Any
import json
import string

from services.utils import send_get_request, send_post_request, send_put_request

class Fuzzer:
    config = dict()
    default_config =  {
            "TargetURL": "www.example.com",
            "HTTPMethod": "GET",
            "Cookies": [],
            "HideStatusCode": [],
            "ShowOnlyStatusCode": [],
            "FilterContentLength": 1000,
            "PageLimit": 1000,
            "WordList": ["username", "password", "search", "admin"]
        }
    def __init__(self, config=None):
        if config is None:
            self.reset()
            return
        elif len(config) == 0:
            self.reset()
            return
        for key in self.default_config.keys():
            if key not in config:
                print(key)
                raise KeyError("Invalid config dictionary")
        try:
            self.config = {
                "TargetURL": config["TargetURL"],
                "HTTPMethod": config["HTTPMethod"],
                "Cookies": config["Cookies"],
                "HideStatusCode": config["HideStatusCode"],
                "ShowOnlyStatusCode": config["ShowOnlyStatusCode"],
                "FilterContentLength": int(config["FilterContentLength"]),
                "PageLimit": int(config["PageLimit"]),
                "WordList": config["WordList"]
            }
        except ValueError as e:
            raise ValueError(f"Invalid config values: {e}")
         #Store raw responses as {path:response}
        self.op_results: Dict[str, Any] = {}
        #Track visited URLs to prevent duplicate crawling
        self.visited_urls = set()
        #Track how many pages have been crawled
        self.page_count = int(0)

    def start(self):
        if self.config['HTTPMethod'] == "GET":
            self.start_fuzzer_get()
        elif self.config['HTTPMethod'] == "POST":
            self.start_fuzzer_post()
        elif self.config['HTTPMethod'] == "PUT":
            self.start_fuzzer_put()
       

    def generate_fuzzing_params(self, max_length: int = 100) ->str:
        characters = string.ascii_letters + string.digits
        string_length = random.randint(0, max_length)
        return ''.join(random.choice(characters) for _ in range(string_length))



    def fuzz(self, word, mode, fuzzed_string=None, json_string=None):
        
        curr_dir = self.config['TargetURL']+"/"+word+"/"+fuzzed_string
        # www.google.com/akjlsdhf www.google.com/search/alkdsjfh
        if mode == "GET":
            response, status_code = send_get_request(curr_dir, 0, self.page_count, self.config['PageLimit'], "", self.config['Cookies'])
        elif mode =="POST":
            response, status_code = send_post_request(curr_dir, 0, json_string, self.page_count, self.config['PageLimit'], "", self.config['Cookies'])
        elif mode == "PUT":
            response, status_code = send_put_request(curr_dir, 0, json_string, self.page_count, self.config['PageLimit'], "", self.config['Cookies'])
        else:
            raise TypeError("Invalid mode")
        self.op_results[curr_dir] = response, status_code
        self.visited_urls.add(curr_dir)
        self.update_fuzzer_data(links=self.visited_urls, fuzzer_data=self.op_results)
        self.page_count+=1

    def start_fuzzer_get(self):
        fuzzed_string = self.generate_fuzzing_params()
        self.fuzz("", "GET", fuzzed_string)
        while self.page_count < self.config['PageLimit']:
            for word in self.config['WordList']:
                if self.page_count >= self.config['PageLimit']:
                    return
                fuzzed_string = self.generate_fuzzing_params()
                self.fuzz(word, "GET" , fuzzed_string)

    def start_fuzzer_put(self):
        while self.page_count < self.config['PageLimit']:
            for word in self.config['WordList']:
                if self.page_count >= self.config['PageLimit']:
                    return

                fuzzed_string = self.generate_fuzzing_params()
                json_string = json.dumps({word: fuzzed_string})
                self.fuzz(word, "PUT", fuzzed_string, json_string)

    import json

    def start_fuzzer_post(self):
        while self.page_count < self.config['PageLimit']:
            for word in self.config['WordList']:
                if self.page_count >= self.config['PageLimit']:  # Double check to prevent overflow
                    return

                fuzzed_string = self.generate_fuzzing_params()
                json_string = json.dumps({word: fuzzed_string})
                self.fuzz(word, "POST", fuzzed_string, json_string)

    def get_data(self):
        return self.op_results
    
    def get_links(self):
        return self.visited_urls
            
    def reset(self):
        self.config = None
        self.config = self.default_config
        self.op_results = {} #reset operation results
        self.visited_urls = set() #reset curr list of visited urls
        self.page_count = 0 #reset pages count


    def update_fuzzer_data(self, links, fuzzer_data):
        from routers.api_endpoints import set_fuzzer_data, set_fuzzer_links
        # Update fuzzer data and links in real-time
        set_fuzzer_links(links)
        set_fuzzer_data(fuzzer_data)
        print(f"Updated fuzzer data for:")
    