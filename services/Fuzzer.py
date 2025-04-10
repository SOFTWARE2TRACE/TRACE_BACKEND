import random
from typing import Dict, Any
import json
import string

# Removed: from services.utils import send_get_request, send_post_request, send_put_request
# Reason: Replaced with Subsystem 1's HTTPClient for consistent HTTP handling across subsystems
#from services.utils import send_get_request, send_post_request, send_put_request

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
    
    def __init__(self, config=None, http_client=None):
        # Added http_client parameter to accept HTTPClient instance from Subsystem 1
        if config is None or len(config) == 0:
            self.reset()
            return
        else:
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
            self.op_results: Dict[str, Any] = {}
            self.visited_urls = set()
            self.page_count = 0
            self.client = http_client # Store HTTPClient instance for making requests
            if self.client is None:
                raise ValueError("HTTPClient instance required") # Ensure HTTPClient is provided by Subsystem 1

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
        
        curr_dir = self.config['TargetURL']+"/"+word+"/"+ (fuzzed_string or "")
        headers = {"User-Agent": ""}  # Default empty, configurable later if needed
        # Replaced utils.py send_*_request with HTTPClient to use Subsystem 1's centralized HTTP handling
        # www.google.com/akjlsdhf www.google.com/search/alkdsjfh
        if mode == "GET":
            self.client.send_request_with_cookies(curr_dir, None, "GET", headers, self.config['Cookies'])
        elif mode == "POST":
            payload = json.loads(json_string) if json_string else {}
            self.client.send_request_with_cookies(curr_dir, payload, "POST", headers, self.config['Cookies'])
        elif mode == "PUT":
            payload = json.loads(json_string) if json_string else {}
            self.client.send_request_with_cookies(curr_dir, payload, "PUT", headers, self.config['Cookies'])
        else:
            raise TypeError("Invalid mode")
        # Updated to use HTTPClient's response structure (body, status_code)
        response = self.client.receive_response()
        if response:
            self.op_results[curr_dir] = (response.body, response.status_code)
            self.visited_urls.add(curr_dir)
            self.page_count += 1
            self.update_fuzzer_data(links=self.visited_urls, fuzzer_data=self.op_results)

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

    #already a one at the top : import json

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
    
