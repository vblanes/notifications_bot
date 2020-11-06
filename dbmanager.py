import sqlite3
import logging
from typing import Optional


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DBManager:

    def __init__(self):
        self.connection = sqlite3.connect('database.sqlite3')
        self.cursor = self.connection.cursor()

    def __del__(self):
        self.cursor.close()
        self.connection.close()

    ###########
    # Users
    ###########

    def add_user(self, telegram_id, user, role='user', password=None):
        query = 'INSERT INTO users (telegram_id, username, password, userrole)' \
                'VALUES (?, ?, ?, ?)'
        self.cursor.execute(query, (telegram_id, user, password, role))
        self.connection.commit()

    def exist_user(self, user: str) -> int:
        query = "SELECT COUNT(1) FROM users WHERE username= ?"
        self.cursor.execute(query, (user,))
        try:
            rs = self.cursor.fetchall()
        except sqlite3.Error:
            return False
        # rs should be a list of tuples
        return rs[0][0]

    def exist_user_by_telegram_id(self, telegram_id: int) -> int:
        query = "SELECT COUNT(1) FROM users WHERE telegram_id= ?"
        self.cursor.execute(query, (telegram_id,))
        rs = self.cursor.fetchall()
        # rs should be a list of tuples
        return rs[0][0]

    def get_user(self, telegram_id: int) -> tuple:
        logger.info(f'Checking possible user {telegram_id}')
        query = "SELECT telegram_id, username, password, userrole from users where telegram_id = ?"
        self.cursor.execute(query, (telegram_id,))
        rs = self.cursor.fetchall()
        return rs[0] if rs else []

    ##########
    # Codes
    ##########
    def add_code(self, code) -> bool:
        query = "INSERT INTO codes (code) VALUES (?)"
        self.cursor.execute(query, (code,))
        self.connection.commit()

    def delete_code(self, code):
        query = "DELETE FROM codes WHERE code = ?"
        self.cursor.execute(query, (code,))
        self.connection.commit()


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
        self.cursor.execute(query)
        rs = self.cursor.fetchall()
        logger.info(f"List fo codes rs: {rs}")
        # remove 1-element tuples
        return [el[0] for el in rs]
