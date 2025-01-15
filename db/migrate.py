import os
import sqlite3
import psycopg2
from psycopg2 import sql

# PostgreSQL connection parameters
PG_USER = "postgres"
PG_HOST = "localhost"
PG_PORT = 5432
PG_PASSWORD = ""  # Add password if required

# Directory containing SQLite files
SQLITE_DIR = os.path.expanduser("~/Downloads/dev_1")

# Connect to PostgreSQL
pg_conn = psycopg2.connect(
    dbname="postgres", user=PG_USER, password=PG_PASSWORD, host=PG_HOST, port=PG_PORT
)
pg_conn.autocommit = True
pg_cursor = pg_conn.cursor()

def drop_and_create_database(db_name):
    """Drop and recreate a PostgreSQL database."""
    try:
        print(f"Dropping database {db_name} if it exists...")
        
        # Terminate active connections to the database
        pg_cursor.execute(
            sql.SQL("""
                SELECT pg_terminate_backend(pg_stat_activity.pid)
                FROM pg_stat_activity
                WHERE pg_stat_activity.datname = {db_name}
                AND pid <> pg_backend_pid();
            """).format(db_name=sql.Literal(db_name))
        )

        # Drop the database
        pg_cursor.execute(sql.SQL("DROP DATABASE IF EXISTS {db_name};").format(db_name=sql.Identifier(db_name)))

        print(f"Creating database {db_name}...")
        pg_cursor.execute(sql.SQL("CREATE DATABASE {db_name};").format(db_name=sql.Identifier(db_name)))
    except Exception as e:
        print(f"Error creating database {db_name}: {e}")

def migrate_sqlite_to_postgres(sqlite_file, db_name):
    """Migrate data from SQLite to PostgreSQL."""
    try:
        # Connect to the SQLite database
        sqlite_conn = sqlite3.connect(sqlite_file)
        sqlite_cursor = sqlite_conn.cursor()

        # Connect to the newly created PostgreSQL database
        target_pg_conn = psycopg2.connect(
            dbname=db_name, user=PG_USER, password=PG_PASSWORD, host=PG_HOST, port=PG_PORT
        )
        target_pg_cursor = target_pg_conn.cursor()

        # Get the list of tables in SQLite
        sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = sqlite_cursor.fetchall()

        if not tables:
            print(f"No tables found in SQLite database {sqlite_file}. Skipping.")
            return

        for table in tables:
            try:
                table_name = table[0]
                print(f"Migrating table {table_name}...")

                # Fetch table schema from SQLite
                sqlite_cursor.execute(f"PRAGMA table_info({table_name});")
                columns = sqlite_cursor.fetchall()

                # Debugging: Print the raw columns
                print(f"Schema for table {table_name}: {columns}")

                # Skip tables with no columns
                if not columns:
                    print(f"Skipping table {table_name}: No columns found.")
                    continue

                # Validate and extract column definitions
                column_definitions = [
                    f"\"{col[1].replace('\\', '\\\\').replace('"', '""')}\" TEXT"
                    for col in columns if col[1]
                ]
                column_names = [
                    f"\"{col[1].replace('\\', '\\\\').replace('"', '""')}\""
                    for col in columns if col[1]
                ]

                if not column_definitions:
                    print(f"Skipping table {table_name}: No valid column definitions.")
                    continue

                # Create table schema in PostgreSQL
                create_table_query = f"CREATE TABLE \"{table_name}\" ({', '.join(column_definitions)});"
                print(f"Creating table with query: {create_table_query}")
                target_pg_cursor.execute(create_table_query)

                # Fetch data from SQLite table
                sqlite_cursor.execute(f"SELECT * FROM {table_name};")
                rows = sqlite_cursor.fetchall()

                # Skip empty tables
                if not rows:
                    print(f"Skipping table {table_name}: No data found.")
                    continue

                # Insert data into PostgreSQL
                placeholders = ", ".join(["%s"] * len(column_names))
                insert_query = f"INSERT INTO \"{table_name}\" ({', '.join(column_names)}) VALUES ({placeholders});"

                for row in rows:
                    try:
                        # Check row length
                        if len(row) != len(column_names):
                            print(f"Skipping row due to mismatched length: {row}")
                            continue

                        # print(f"Inserting row: {row}")
                        target_pg_cursor.execute(insert_query, row)
                    except Exception as row_error:
                        print(f"Error inserting row {row} into table {table_name}: {row_error}")
                        continue

            except Exception as table_error:
                print(f"Error migrating table {table_name}: {table_error}")
                continue

        target_pg_conn.commit()
        print(f"Migration of {sqlite_file} to {db_name} completed.")

    except Exception as e:
        print(f"Error migrating {sqlite_file} to {db_name}: {e}")
    finally:
        sqlite_conn.close()
        target_pg_conn.close()

# Walk through all .sqlite files in the directory
for root, _, files in os.walk(SQLITE_DIR):
    for file in files:
        if file.endswith(".sqlite"):
            sqlite_file = os.path.join(root, file)
            db_name = os.path.splitext(file)[0]
            print(f"Processing {sqlite_file}...")

            # Drop and recreate the PostgreSQL database
            drop_and_create_database(db_name)

            # Migrate SQLite database to PostgreSQL
            migrate_sqlite_to_postgres(sqlite_file, db_name)

# Close PostgreSQL connection
pg_cursor.close()
pg_conn.close()

print("All migrations completed.")
