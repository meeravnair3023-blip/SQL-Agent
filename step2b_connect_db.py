import mysql.connector

class Database:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root123",   # ← your password
            database="chinook"
        )

    def run(self, query):
        cursor = self.conn.cursor()

        try:
            cursor.execute(query)

            if query.strip().upper().startswith("SELECT"):
                return cursor.fetchall()
            else:
                self.conn.commit()
                return "OK"

        except Exception as e:
            return f"DB Error: {str(e)}"

db = Database()