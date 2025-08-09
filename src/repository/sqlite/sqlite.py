import sqlite3
from typing import Optional

class Repository():
    def __init__(self, db_path : str):
        self.conn: Optional[sqlite3.Connection] = None
        self.cursor: Optional[sqlite3.Cursor] = None
        try:
            self.conn = sqlite3.connect(db_path)
            self.cursor = self.conn.cursor()
            with open('src/db/migrations/init.sql', 'r', encoding='utf-8') as script:
                migration = script.read()
            self.cursor.executescript(migration)
            self.conn.commit()
            print("Миграцию накатили")
        except sqlite3.Error as e:
            print(f"Ошибка с работой СУБД: {e}")
            self.close()
            raise
        except Exception as e:
            print(f"Неожиданная ошибка: {e}")
            self.close()
            raise
    def add_or_update_user(self, user_id : int, language : str):
        self.cursor.execute("""INSERT OR REPLACE INTO users (id, language) VALUES (?, ?)""",
                            (user_id, language))
        self.conn.commit()
    def get_token(self, user_id : int) -> str:
        self.cursor.execute("""SELECT access_token FROM users WHERE id = ?""", user_id)
        res = self.cursor.fetch
    def get_language(self, user_id : int):
        self.cursor.execute("""SELECT * """)
    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None