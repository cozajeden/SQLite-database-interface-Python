import sqlite3 as sql
import os, sys
from datetime import datetime
from passlib.hash import pbkdf2_sha256 as secure
from tkinter.messagebox import showerror

BASEDIR = os.path.dirname(os.path.abspath(__file__))


class DataBase:
    def __init__(self):
        super().__init__()
        self.dbName = 'main.db'
        if self.dbName not in os.listdir(BASEDIR):
            showerror('Błąd krytyczny.', 'Brak bazy danych!')
            sys.exit('Database do not exist.')
        # currentLevel:
        # 0 - operator
        # 1 - SIP/DUM
        # 2 - engineer
        # 3 - admin
        self.currentLevel = 0
        self.currentUser = 'OPERATOR'

    def log(self, text):        self.execute(f"INSERT INTO logs (timestamp, text) VALUES ('{datetime.now()}', '{text}')"); self.commit()
    def connect(self):          self.conn = sql.connect(os.path.join(BASEDIR, self.dbName)); self.cursor = self.conn.cursor()
    def log_out(self):          self.currentLevel = 0; self.currentUser = 'OPERATOR'
    def execute(self, query):   self.cursor.execute(query); self.commit()
    def fetchall(self):         return self.cursor.fetchall()
    def fetchone(self):         return self.cursor.fetchone()
    def commit(self):           self.conn.commit()
    def disconnect(self):       self.conn.close()

    def log_results(self, results: list):
        """results - list of lists
        each list have to contain data in order:
        serialnumber, teststep, passfail, measurement, minlimit, maxlimit"""
        query = f"INSERT INTO results (timestamp, serialnumber, teststep, passfail, measurement, minlimit, maxlimit) VALUES "
        timestamp = datetime.now()
        for serialnumber, teststep, passfail, measurement, minlimit, maxlimit in results:
            query += f"('{timestamp}', '{serialnumber}', '{teststep}', {passfail}, {measurement}, {minlimit}, {maxlimit}),"
        self.execute(query[:-1])

    def sign_up(self, user, password, level, firstname, lastname):
        query = f"""SELECT user FROM users where user = '{user}'"""
        self.execute(query)
        temp = self.fetchone()
        if temp is None:
            password = secure.hash(password)
            query = f"""INSERT INTO users (user, password, level, firstname, lastname)
            VALUES ('{user}', '{password}', {level}, '{firstname}', '{lastname}')"""
            self.execute(query)
            self.log(f'User {user} signed up by {self.currentUser}.')
        else:
            return 'Użytkownik już istnieje.'

    def sign_in(self, user, password):
        query = f"""SELECT * FROM users WHERE user = '{user}'"""
        self.execute(query)
        temp = self.fetchone()
        if temp is not None:
            _, _user, _password, _level, _firstname, _lastname = temp
            verified = secure.verify(password, _password)
            if verified:
                self.currentLevel = _level
                self.currentUser = f'{_firstname} {_lastname}'
                self.log(f'User {user} logged in.')
            else:
                return 'Nieprawidłowe hasło.'
        else:
            return 'Użytkownik nie ustnieje.'

    def get_users(self):
        query = """SELECT id, user FROM users"""
        self.execute(query)
        temp = self.fetchall()
        return temp

    def change_password(self, user, oldpass1, oldpass2, newpass):
        if oldpass1 == oldpass2:
            query = f"""SELECT * FROM users WHERE user = '{user}'"""
            self.execute(query)
            temp = self.fetchone()
            if temp is not None:
                _id, _user, _password, *_ = temp
                verified = secure.verify(oldpass1, _password)
                if verified:
                    password = secure.hash(newpass)
                    query = f"""UPDATE users SET password = '{password}' WHERE user = '{user}'"""
                    self.execute(query)
                    self.commit()
                    self.log(f'User {self.currentUser} changed password.')
                else:
                    return 'Nieprawidłowe hasło.'
            else:
                return 'Użytkownik nie istnieje.'
        else:
            return 'Hasła do siebie nie pasują.'

    def save_settings(self, settings, name=None):
        settings = str(settings).encode('utf-8').hex()
        self.execute(f"INSERT INTO settings (user, timestamp, settings, name) VALUES ('{self.currentUser}', '{datetime.now()}', '{settings}', '{name}')")
        self.log(f'Settings changed by {self.currentUser}')

    def make_settings_current(self, id):
        'Save choosen settings as current settings. Return choosen settings'
        self.execute(f"SELECT settings FROM settings WHERE id = {id}")
        settings, name = self.fetchone()
        self.execute(f"""INSERT INTO settings (user, timestamp, settings, name) VALUES ('{self.currentUser}', '{datetime.now()}', '{settings}', '{name}')""")
        self.log(f'Settings {id} loaded by {self.currentUser}')
        return eval(bytes.fromhex(settings).decode('utf-8'))

    def get_settings(self):
        self.execute(f"SELECT id, name, settings FROM settings")
        idSettings = self.fetchall()
        settings = map(lambda x: (x[0], x[1], bytes.fromhex(x[2]).decode('utf-8')), idSettings)
        return list(settings)

    def get_current_settings(self):
        self.execute('SELECT settings from settings ORDER BY id DESC LIMIT 1')
        return eval(bytes.fromhex(self.fetchone()[0]).decode('utf-8'))


if __name__ == "__main__":
    db = DataBase()
    db.connect()
    # settings = 'record'
    # sets = db.get_settings()
    # print(sets)
    # db.save_settings(next(filter(lambda x: x != 1, sets))[1])
    # db.execute('SELECT * from settings')
    # print(db.fetchall())
    # db.execute('SELECT settings from settings ORDER BY id DESC LIMIT 1')
    # print(db.fetchall())
    db.disconnect()
