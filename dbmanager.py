import sqlite3
from typing import Optional


class DBManager:

    def __init__(self):
        self.connection = sqlite3.connect('')
        self.cursor = self.connection.cursor()

    def __del__(self):
        self.cursor.close()
        self.connection.close()

    ###########
    # Users
    ###########
    def add_user(self, telegram_id: int, user: str, role: str = 'user', password: Optional[str] = None) -> bool:
        query = 'INSERT INTO users (telegramid, username, password, userrole)' \
                'VALUES (?, ?, ?, ?)'
        try:
            self.cursor.execute(query, (telegram_id, user, password, role))
        except sqlite3.Error:
            return False
        return True

    def exist_user(self, user: str) -> bool:
        query = "SELECT COUNT(1) FROM users WHERE username = ?"
        self.cursor.execute(query, (user,))
        try:
            rs = self.cursor.fetchall()
        except sqlite3.Error:
            return False
        # rs should be a list of tuples
        return rs[0][0]

    def get_user(self, telegram_id: int) -> Optional[list]:
        query = "SELECT telegram_id, username, password, userrole from user where telegram_id= ? "
        try:
            self.cursor.execute(query, (telegram_id,))
            rs = self.cursor.fetchall()
        except sqlite3.Error:
            return None
        return rs

    ##########
    # Codes
    ##########
    def add_code(self, code) -> bool:
        query = "INSERT INTO codes (code) VALUES (?)"
        try:
            self.cursor.execute(query, (code,))
        except sqlite3.Error:
            return False
        return True

    def delete_code(self, code) -> bool:
        try:
            query = "DELETE FROM codes WHERE code = ?"
            self.cursor.execute(query, (code,))
        except sqlite3.Error:
            return False
        return True

    def exist_code(self, code) -> bool:
        query = "SELECT COUNT(1) FROM codes WHERE code = ?"
        try:
            self.cursor.execute(query, (code,))
            rs = self.cursor.fetchall()
        # rs should be a list of tuples
        except sqlite3.Error:
            return False
        return rs[0][0]

    def list_codes(self) -> Optional[list]:
        query = "SELECT * FROM codes"
        try:
            self.cursor.execute(query)
            rs = self.cursor.fetchall()
        except sqlite3.Error:
            return None
        # remove 1-element tuples
        return [el[0] for el in rs]
