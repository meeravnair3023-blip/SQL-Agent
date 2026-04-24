import sqlite3

class Database:
    def __init__(self):
        self.conn = sqlite3.connect("Chinook.db", check_same_thread=False)

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