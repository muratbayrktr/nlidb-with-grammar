import psycopg2

class DBEngine:
    def connect_postgresql(self):
        # Open database connection
        # Connect to the database
        db = psycopg2.connect(
            "dbname=bird user=nlidb host=localhost password='' port=5432"
        )
        return db


    def execute_postgresql_query(self, cursor, query):
        """Execute a MySQL query."""
        cursor.execute(query)
        result = cursor.fetchall()
        return result


    def perform_query_on_postgresql_databases(self, query):
        db = self.connect_postgresql()
        cursor = db.cursor()
        result = self.execute_postgresql_query(cursor, query)
        db.close()
        return result