import sqlite3
class conn_sqlite3():
    def __init__(self,db_path):
        self.db_path=db_path
    def open(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.cur = self.conn.cursor()
    def do_sql_execute(self,sql):
        try:
            self.cur.execute(sql)
            self.conn.commit()
            count = self.cur.rowcount
            return count
        except Exception as e:
            self.conn.rollback()
            raise Exception(e,e.__traceback__.tb_lineno)
    def do_sql_select(self,sql):
        try:
            self.cur.execute(sql)
            res=self.cur.fetchall()
            return res
        except Exception as e:
            self.conn.rollback()
            raise Exception(e,e.__traceback__.tb_lineno)
    def close(self):
        if self.conn:
            self.conn.close()
