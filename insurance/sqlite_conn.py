"""
This is a simple class for providing a sqlite connection.

"""
import os
import sqlite3


class SQLiteConnection:
    """Simple class for providing a single connection to sqlite"""
    conn = None
    dir_name = os.path.dirname(__file__)
    fn = os.path.join(dir_name, '../data/auto_insurance.db')

    def __init__(self):
        print(F"Connecting to db in {self.fn}")
        self.conn = sqlite3.connect(self.fn)
