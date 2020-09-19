import sqlite3


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
    def add_user(self, telegram_id, user, role='user', password=None):
        query = 'INSERT INTO users (telegramid, username, password, userrole)' \
                'VALUES (?, ?, ?, ?)'
        self.cursor.execute(query, (telegram_id, user, password, role))

    def exist_user(self, user):
        query = "SELECT COUNT(1) FROM users WHERE username = ?"
        self.cursor.execute(query, (user,))
        rs = self.cursor.fetchall()
        # rs should be a list of tuples
        return rs[0][0]

    def get_user(self, telegram_id):
        query = "SELECT telegram_id, username, password, userrole from user where telegram_id= ? "
        self.cursor.execute(query, (telegram_id,))
        return self.cursor.fetchall()

    ##########
    # Codes
    ##########
    def add_code(self, code):
        query = "INSERT INTO codes (code) VALUES (?)"
        self.cursor.execute(query, (code,))

    def delete_code(self, code):
        query = "DELETE FROM codes WHERE code = ?"
        self.cursor.execute(query, (code,))

    def exist_code(self, code):
        query = "SELECT COUNT(1) FROM codes WHERE code = ?"
        self.cursor.execute(query, (code,))
        rs = self.cursor.fetchall()
        # rs should be a list of tuples
        return rs[0][0]

    def list_codes(self):
        query = "SELECT * FROM codes"
        self.cursor.execute(query)
        rs = self.cursor.fetchall()
        # remove 1-element tuples
        return [el[0] for el in rs]
