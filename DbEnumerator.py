from neo4j import GraphDatabase
from typing import List, Dict

class DBEnumerator:
    def __init__(self, driver):
        self.driver = driver
        self.tables = []
        self.columns = {}
        self.results = {}

    def enumerate_database(self):
        with self.driver.session() as session:
            # Fetch all the table names (labels in Neo4j)
            result = session.run("CALL db.labels()")
            self.tables = [record["label"] for record in result]
            print(f"Tables found: {self.tables}")  # Debugging output

            # Fetch columns (properties) for each table (node label)
            for table in self.tables:
                result = session.run(f"MATCH (n:{table}) RETURN keys(n) LIMIT 1")
                columns = []
                for record in result:
                    columns = record["keys(n)"]  # The properties (columns) for the table
                self.columns[table] = columns
                print(f"Columns for {table}: {self.columns[table]}")  # Debugging output

            # Fetch data for each table
            for table in self.tables:
                result = session.run(f"MATCH (n:{table}) RETURN n LIMIT 10")  # Fetch data for each table (node)
                table_data = []
                for record in result:
                    node = record["n"]
                    node_data = {
                        "identity": node.identity,
                        "labels": node.labels,
                        "properties": dict(node.items()),  # Convert properties to a dict
                        "elementId": str(node.identity)  # Convert identity to a string for elementId
                    }
                    print(f"Data for {table}: {node_data}")  # Debugging output
                    table_data.append(node_data)
                self.results[table] = table_data

    def get_summary(self):
        return {
            "tableNames": self.tables,
            "columnNames": self.columns,
            "table": self.results
        }
