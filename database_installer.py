import sqlite3 as sql
import os, sys, time
from database import DataBase
from datetime import datetime
from getpass import getpass
from numpy import pi

def install_db(isNew = False):
    name = 'main.db'

    # Initial settings for the system (cannot be empty)
    # Last setting have to point to output image

                
    settings = { 
                0: ['gaussianblur', 'copy', [3], [1, 50], 'wstepne rozmycie', 'left'],
                1: ['cropbrightrect', '0gaussianblur', [167, 7, 10], [0, 255], [-100, 100], [-100, 100], 'Wyciecie ekranu', 'left'],
                2: ['verticalturncate', '1cropbrightrect', [20], [-1000, 1000], 'wyciecie gory', 'left'],
                3: ['verticalturncate', '1cropbrightrect', [-20], [-1000, 1000], 'wyciecie dolu', 'left'],
                4: ['horizontalturncate', '1cropbrightrect', [20], [-1000, 1000], 'wyciecie z lewej', 'left'],
                5: ['horizontalturncate', '1cropbrightrect', [-20], [-1000, 1000], 'wyciecie z prawej', 'left'],
                6: ['truncate', '1cropbrightrect', [54, 712, 47, 1409], [0, 2000], [0, 2000], [0, 2000], [0, 2000], 'wyciecie srodka', 'left'],
                7: ['gaussianblur', '2verticalturncate', [16], [1, 50], 'rozmycie gory', 'left'],
                8: ['gaussianblur', '3verticalturncate', [16], [1, 50], 'rozmycie golu', 'left'],
                9: ['gaussianblur', '4horizontalturncate', [4], [1, 50], 'rozmycie z lewej', 'left'],
                10: ['gaussianblur', '5horizontalturncate', [16], [1, 50], 'rozmycie z prawej', 'left'],
                11: ['gaussianblur', '6truncate', [18], [1, 50], 'rozmycie srodka', 'left'],
                12: ['sobel', '7gaussianblur', [2, 0, 1, 1, 2], [0, 200], [0, 200], [0, 10], [0, 10], [0, 3], 'różniczka gory', 'left'],
                13: ['sobel', '8gaussianblur', [2, 0, 1, 1, 2], [0, 200], [0, 200], [0, 10], [0, 10], [0, 3], 'różniczka dolu', 'left'],
                14: ['sobel', '9gaussianblur', [2, 0, 1, 1, 2], [0, 200], [0, 200], [0, 10], [0, 10], [0, 3], 'różniczka z lewej', 'left'],
                15: ['sobel', '10gaussianblur', [2, 0, 1, 1, 2], [0, 200], [0, 200], [0, 10], [0, 10], [0, 3], 'różniczka z prawej', 'left'],
                16: ['sobel', '11gaussianblur', [3.7, 0, 1, 1, 2], [0, 200], [0, 200], [0, 10], [0, 10], [0, 3], 'rózniczka srodka', 'left'],
                17: ['binarythreshold', '12sobel', [135], [0, 255], 'threshold gory', 'left'],
                18: ['binarythreshold', '13sobel', [135], [0, 255], 'threshold dolu', 'left'],
                19: ['binarythreshold', '14sobel', [135], [0, 255], 'threshold z lewej', 'left'],
                20: ['binarythreshold', '15sobel', [135], [0, 255], 'threshold z prawej', 'left'],
                21: ['binarythreshold', '16sobel', [135], [0, 255], 'threshold srodka', 'left'],
                22: ['countwhitepixels', '17binarythreshold', [0.005], [0, 100], 'limit gory', 'left'],
                23: ['countwhitepixels', '18binarythreshold', [0.005], [0, 100], 'limit dolu', 'left'],
                24: ['countwhitepixels', '19binarythreshold', [0.005], [0, 100], 'limit z lewej', 'left'],
                25: ['countwhitepixels', '20binarythreshold', [0.005], [0, 100], 'limit z prawej', 'left'],
                26: ['countwhitepixels', '21binarythreshold', [0.005], [0, 100], 'limit srodka', 'left'],
                27: ['output', [
                    ['gora', '17binarythreshold'],
                    ['dol', '18binarythreshold'],
                    ['lewo', '19binarythreshold'],
                    ['prawo', '20binarythreshold'],
                    ['srodek', '21binarythreshold']
                ], 'out'],
    }

    settings = str(settings).encode('utf-8').hex()

    if not isNew:
        print('If you continue, the existing database will be lost.')
        print('continue - install/reset data base\notherwise - abort')
        temp = input('SQL> ')
        if temp != 'continue':
            sys.exit()
        
    password = ''
    while not password:
        password = getpass('Create admin password:\nSQL>')
    if name in os.listdir():
        os.remove(name)

    conn = sql.connect(name)
    cursor = conn.cursor()

    print('Make your custom stuff.')
    print('0 - continue')
    while(True):
        temp = input('SQL> ')
        if temp == '0':
            break
        cursor.execute(temp)
        conn.commit()
        print(cursor.fetchall())


    cursor.execute('CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, user VARCHAR UNIQUE, password TEXT, level INTEGER, firstname TEXT, lastname TEXT)'); conn.commit()
    cursor.execute('CREATE TABLE logs (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, timestamp DATETIME, text TEXT)'); conn.commit()
    cursor.execute('CREATE TABLE settings (id INTEGER PRIMARY KEY, user VARCHAR, timestamp DATETIME, settings TEXT, name TEXT)'); conn.commit()
    cursor.execute('CREATE TABLE results (id INTEGER PRIMARY KEY, timestamp DATETIME, serialnumber VARCHAR, passfail BOOLEAN, teststep VARCHAR, measurement FLOAT, maxlimit FLOAT, minlimit FLOAT)'); conn.commit()
    cursor.execute(f"INSERT INTO settings (user, timestamp, settings) VALUES ('system', '{datetime.now()}', '{settings}')"); conn.commit()
    cursor.execute(f"INSERT INTO logs (timestamp, text) VALUES ('{datetime.now()}', 'Database created!')"); conn.commit()
    conn.close()
    shared = {}

    db = DataBase()
    db.connect()
    db.sign_up('admin', password, 3, 'Admin', 'Admin')
    db.disconnect()
    print('Data Base installed.')
    print('Have a nice day!')
    input('')

if __name__ == "__main__":
    install_db()