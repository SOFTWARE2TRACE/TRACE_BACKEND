from typing import List, Dict, Optional
import os

class Table:
    def __init__(self, name: str, columns: List[str], data: List[Dict[str, Any]]):
        self.name = name
        self.columns = columns
        self.data = data
    
    def get_table_name(self) -> str:
        return self.name
    
    def get_columns(self) -> List[str]:
        return self.columns
    
    def get_data(self) -> List[Dict[str, Any]]:
        return self.data
    
    def query_data(self, column: str, value: Any) -> List[Dict[str, Any]]:
        return [row for row in self.data if row.get(column) == value]
    
    def delete_row(self, column: str, value: Any) -> bool:
        original_length = len(self.data)
        self.data = [row for row in self.data if row.get(column) != value]
        return len(self.data) < original_length
    
    def insert_row(self, new_row: Dict[str, Any]) -> bool:
        if all(col in self.columns for col in new_row.keys()):
            self.data.append(new_row)
            return True
        return False