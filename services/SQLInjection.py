from typing import List, Dict, Optional, Any
import os
import re

class SQLInjection:
    def __init__(self):
        self.predefined_queries = ["SELECT * FROM users", "DROP TABLE students"]
        self.stored_requests = {}
        self.stored_responses = {}
        self.request_counter = 1
    
    def get_predefined_queries(self) -> List[str]:
        return self.predefined_queries
    
    def store_request(self, request: str) -> bool:
        if request:
            self.stored_requests[self.request_counter] = request
            self.request_counter += 1
            return True
        return False
    
    def get_request_by_id(self, request_id: int) -> Optional[str]:
        return self.stored_requests.get(request_id)
    
    def modify_request(self, request_id: int, new_request: str) -> bool:
        if request_id in self.stored_requests:
            self.stored_requests[request_id] = new_request
            return True
        return False
    
    def store_response(self, request_id: int, response: str) -> bool:
        if request_id in self.stored_requests:
            self.stored_responses[request_id] = response
            return True
        return False    
    
    def get_response_by_id(self, request_id: int) -> Optional[str]:
        return self.stored_responses.get(request_id)
    
    def get_all_requests(self) -> Dict[int, str]:
        return self.stored_requests
    
    def get_all_responses(self) -> Dict[int, str]:
        return self.stored_responses
    
    def save_results_to_file(self, filename: str = "sql_results.txt") -> None:
        with open(filename, "w") as file:
            for request_id in self.stored_requests:
                request = self.stored_requests[request_id]
                response = self.stored_responses.get(request_id, "No Response")
                file.write(f"Request {request_id}: {request}\nResponse: {response}\n\n")
        print(f"Results saved to {filename}")
                
                
    def reset_service(self) -> None:
        self.stored_requests = {}
        self.stored_responses = {}
        self.request_counter = 1
        
    def get_available_features(self) -> List[str]:
        return ["SQL Injection Scan",
                "Modify SQL Request",
                "Show Stored SQL Requests",
                "Show Stored SQL Responses",
                "Save Results to File",
                "Reset Service"]
        
    