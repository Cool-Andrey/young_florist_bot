import sqlite3
from typing import Optional


class Repository():
    def __init__(self, db_path: str):
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

    async def set_user_and_language(self, user_id: int, language: str = 'ru'):
        self.cursor.execute("""
            INSERT INTO users (id, lang)
            VALUES (?, ?)
            ON CONFLICT(id) DO UPDATE SET lang = excluded.lang
        """, (user_id, language))
        self.conn.commit()


    async def get_token(self, user_id: int) -> (str | None):
        self.cursor.execute("""SELECT access_token FROM users WHERE id = ?""", (user_id,))
        res = self.cursor.fetchone()
        return str(res[0]) if res else None


    async def get_language(self, user_id: int) -> (str | None):
        self.cursor.execute("""SELECT lang FROM users WHERE id = ?""", (user_id,))
        res = self.cursor.fetchone()
        return res[0] if res else None


    async def set_token(self, access_token: str, user_id: int):
        self.cursor.execute("""
            UPDATE users
            SET access_token = ?
            WHERE id = ?
        """, (access_token, user_id))
        self.conn.commit()


    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None
