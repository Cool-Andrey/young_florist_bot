import sqlite3
from typing import Optional


class Repository:
    def __init__(self, db_path: str):
        self.conn: Optional[sqlite3.Connection] = None
        self.cursor: Optional[sqlite3.Cursor] = None
        try:
            self.conn = sqlite3.connect(db_path, check_same_thread=False)
            self.cursor = self.conn.cursor()
            with open('src/db/migrations/init.sql', 'r', encoding='utf-8') as script:
                migration = script.read()
            self.cursor.executescript(migration)
            self.conn.commit()
            print("Миграцию накатили")
        except sqlite3.Error as e:
            error_msg = f"Ошибка при инициализации базы данных: {e}"
            print(error_msg)
            self.close()
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Неожиданная ошибка при инициализации СУБД: {e}"
            print(error_msg)
            self.close()
            raise Exception(error_msg) from e

    async def set_user_and_language(self, user_id: int, language: str = 'ru'):
        try:
            self.cursor.execute("""
                INSERT INTO users (id, lang)
                VALUES (?, ?)
                ON CONFLICT(id) DO UPDATE SET lang = excluded.lang
            """, (user_id, language))
            self.conn.commit()
        except sqlite3.Error as e:
            error_msg = f"Ошибка при запросе к СУБД: не удалось установить язык для пользователя {user_id}: {e}"
            print(error_msg)
            self.conn.rollback()
            raise Exception(error_msg) from e

    async def get_token(self, user_id: int) -> Optional[str]:
        try:
            self.cursor.execute("SELECT access_token FROM users WHERE id = ?", (user_id,))
            res = self.cursor.fetchone()
            return str(res[0]) if res and res[0] is not None else None
        except sqlite3.Error as e:
            error_msg = f"Ошибка при запросе к СУБД: не удалось получить токен для пользователя {user_id}: {e}"
            print(error_msg)
            raise Exception(error_msg) from e

    async def get_language(self, user_id: int) -> Optional[str]:
        try:
            self.cursor.execute("SELECT lang FROM users WHERE id = ?", (user_id,))
            res = self.cursor.fetchone()
            return res[0] if res and res[0] is not None else None
        except sqlite3.Error as e:
            error_msg = f"Ошибка при запросе к СУБД: не удалось получить язык для пользователя {user_id}: {e}"
            print(error_msg)
            raise Exception(error_msg) from e

    async def set_token(self, access_token: str, user_id: int):
        try:
            self.cursor.execute("""
                UPDATE users
                SET access_token = ?
                WHERE id = ?
            """, (access_token, user_id))
            self.conn.commit()
        except sqlite3.Error as e:
            error_msg = f"Ошибка при запросе к СУБД: не удалось установить токен для пользователя {user_id}: {e}"
            print(error_msg)
            self.conn.rollback()
            raise Exception(error_msg) from e

    async def set_image_base64(self, user_id: int, image_base64: str):
        try:
            self.cursor.execute("""
                INSERT INTO users (id, lang, access_token, image_base_64)
                VALUES (?, 'ru', NULL, ?)
                ON CONFLICT(id) DO UPDATE SET
                    image_base_64 = excluded.image_base_64
            """, (user_id, image_base64))
            self.conn.commit()
        except sqlite3.Error as e:
            error_msg = f"Ошибка при запросе к СУБД: не удалось сохранить изображение для пользователя {user_id}: {e}"
            print(error_msg)
            self.conn.rollback()
            raise Exception(error_msg) from e

    async def get_image_base_64(self, user_id: int) -> Optional[str]:
        try:
            self.cursor.execute("SELECT image_base_64 FROM users WHERE id = ?", (user_id,))
            res = self.cursor.fetchone()
            return res[0] if res and res[0] is not None else None
        except sqlite3.Error as e:
            error_msg = f"Ошибка при запросе к СУБД: не удалось получить изображение для пользователя {user_id}: {e}"
            print(error_msg)
            raise Exception(error_msg) from e

    async def set_last_flower(self, user_id: int, flower_name: str):
        try:
            self.cursor.execute("""
                INSERT INTO users (id, last_flower)
                VALUES (?, ?)
                ON CONFLICT(id) DO UPDATE SET last_flower = excluded.last_flower
            """, (user_id, flower_name))
            self.conn.commit()
        except sqlite3.Error as e:
            error_msg = f"Ошибка при запросе к СУБД: не удалось установить последний цветок для пользователя {user_id}: {e}"
            print(error_msg)
            self.conn.rollback()
            raise Exception(error_msg) from e

    async def get_last_flower(self, user_id: int) -> Optional[str]:
        try:
            self.cursor.execute("SELECT last_flower FROM users WHERE id = ?", (user_id,))
            res = self.cursor.fetchone()
            return res[0] if res and res[0] is not None else None
        except sqlite3.Error as e:
            error_msg = f"Ошибка при запросе к СУБД: не удалось получить последний цветок для пользователя {user_id}: {e}"
            print(error_msg)
            raise Exception(error_msg) from e

    def close(self):
        if self.conn:
            try:
                self.conn.close()
                print("Соединение с БД закрыто.")
            except sqlite3.Error as e:
                print(f"Ошибка при закрытии соединения с СУБД: {e}")
            finally:
                self.conn = None
                self.cursor = None
