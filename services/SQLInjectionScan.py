from typing import List, Dict, Optional, Any
import os
import re

class SQLInjectionScan:
    SQL_PATTERNS = [
        r"(?i)(union.*select)",
        r"(?i)(select.*from.*where)",
        r"(?i)(insert\s+into.*values)",
        r"(?i)(drop\s+table)",
        r"(?i)(--|#|/\*|\*/|xp_)"
    ]
    
    @staticmethod
    def scan_input_sql_injection(user_input: str) -> bool:
        for pattern in SQLInjectionScan.SQL_PATTERNS:
            if re.search(pattern, user_input):
                return True
        return False
    
    @staticmethod
    def analyze_query(query: str) -> bool:
        for pattern in SQLInjectionScan.SQL_PATTERNS:
            if re.search(pattern, query):
                return True
        return False
    
    
    @staticmethod
    def detect_sql_vulnerabilities(logs: List[str]) -> List[str]:
        suspicious_queries = [log for log in logs if SQLInjectionScan.analyze_query(log)]
        return suspicious_queries

    @staticmethod
    def process_response(response: str) -> str:
        if "error" in response.lower():
            return "Possible SQL Injection Error Detected"
        return "Response processed successfully"