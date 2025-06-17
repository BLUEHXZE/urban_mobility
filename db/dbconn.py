import sqlite3
import os
from typing import List, Tuple, Any

class DatabaseConnection:
    def __init__(self, db_path="data/urban_mobility.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    def get_connection(self):
        """Get a database connection"""
        return sqlite3.connect(self.db_path)
    
    def execute_query(self, query: str, params: Tuple = ()) -> List[Tuple]:
        """Execute a SELECT query and return results"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def execute_non_query(self, query: str, params: Tuple = ()) -> int:
        """Execute INSERT, UPDATE, DELETE and return affected rows"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount
    
    def execute_scalar(self, query: str, params: Tuple = ()) -> Any:
        """Execute query and return single value"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            result = cursor.fetchone()
            return result[0] if result else None

# Global database instance
db = DatabaseConnection()