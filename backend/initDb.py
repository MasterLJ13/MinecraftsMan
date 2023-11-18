import sqlite3
from sqlite3 import Error


def createDB(db_file, f1, f2, f3):
    try:
        conn = sqlite3.connect(db_file)
        print("connected to database")
        with open(f1) as f:
            print("r")
            conn.executescript(f.read())
        with open(f2) as f:
            print("r")
            conn.executescript(f.read())
        with open(f3) as f:
            print("r")
            conn.executescript(f.read())
        conn.close()
        print("read sql file finished")
        return True
    except Error as e:
        print(e)
        return False
