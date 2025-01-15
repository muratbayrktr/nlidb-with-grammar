import psycopg2
from psycopg2 import sql

# PostgreSQL connection details
PG_HOST = "localhost"
PG_PORT = 5432
PG_USER = "postgres"
PG_PASSWORD = ""  

# List of databases to test
databases = [
    "california_schools",
    "card_games",
    "codebase_community",
    "debit_card_specializing",
    "european_football_2",
    "financial",
    "formula_1",
    "student_club",
    "superhero",
    "thrombosis_prediction",
    "toxicology"
]

def test_database(db_name):
    try:
        # Connect to the database
        connection = psycopg2.connect(
            dbname=db_name,
            user=PG_USER,
            password=PG_PASSWORD,
            host=PG_HOST,
            port=PG_PORT
        )
        cursor = connection.cursor()
        
        # List tables in the database
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
        tables = cursor.fetchall()
        print(f"Database '{db_name}' connected successfully.")
        print(f"Tables in '{db_name}': {', '.join([table[0] for table in tables])}")

        # Optionally, test querying the first table
        if tables:
            table_name = tables[0][0]
            cursor.execute(sql.SQL("SELECT * FROM {} LIMIT 5").format(sql.Identifier(table_name)))
            rows = cursor.fetchall()
            print(f"Sample data from '{table_name}' in '{db_name}': {rows}")
        else:
            print(f"No tables found in database '{db_name}'.")
        
        cursor.close()
        connection.close()
        print(f"Closed connection to database '{db_name}'.\n")

    except Exception as e:
        print(f"Error connecting to database '{db_name}': {e}")

# Test each database
for db in databases:
    test_database(db)
