import os
import sqlite3
from typing import Union


class SQLiteConnector:
    def __init__(self, db_name):
        self.db_name = db_name
        self.con = sqlite3.connect(db_name, autocommit=True)
        self.cur = self.con.cursor()
        self.is_closed = False

    def execute(self, raw_sql, sql_params: Union[tuple, None] = None):
        sql_params = tuple() if not sql_params else sql_params
        return self.cur.execute(raw_sql, sql_params)

    def close(self):
        self.cur.close()
        self.con.close()
        self.is_closed = True

    def __del__(self):
        if not self.is_closed:
            self.close()

    def drop_db(self):
        self.close()
        os.remove(self.db_name)


if __name__ == "__main__":
    sql_con = SQLiteConnector("parser.db")
    sql_con.drop_db()
