from neo4j import GraphDatabase

# Replace with your actual credentials and connection string
uri = "bolt://localhost:7687"  # or neo4j+s://<your-aura-url>
user = "neo4j"
password = "12345678"

driver = GraphDatabase.driver(uri, auth=(user, password))

def test_connection():
    with driver.session() as session:
        result = session.run("RETURN 'Connection successful!' AS message")
        for record in result:
            print(record["message"])

test_connection()
driver.close()



def get_driver():
    return driver
