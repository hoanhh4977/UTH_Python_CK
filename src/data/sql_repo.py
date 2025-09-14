import sqlite3
import pandas as pd

class SQLiteRepo:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None

    def connect(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

    def list_tables(self):
        cur = self.conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        return [r[0] for r in cur.fetchall()]

    def get_schema(self, table: str):
        cur = self.conn.execute(f"PRAGMA table_info({table})")
        return [(r[1], r[2]) for r in cur.fetchall()]

    def run_query(self, sql: str, limit: int = 100):
        if "limit" not in sql.lower():
            sql = sql.strip(";") + f" LIMIT {limit}"
        return pd.read_sql_query(sql, self.conn)

    def insert_dataframe(self, df: pd.DataFrame, table_name: str):
        df.to_sql(table_name, self.conn, if_exists="replace", index=False)
