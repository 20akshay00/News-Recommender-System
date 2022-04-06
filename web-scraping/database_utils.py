import sqlite3, os

def run_query(conn, query):
    conn.cursor().execute(query)
    conn.commit()
    
def table_exists(conn, table_name):
    return conn.cursor().execute(
  f"""SELECT name FROM sqlite_master WHERE type='table'
  AND name='{table_name}'; """).fetchall() != []

def show_table(conn, table_name):
    return conn.execute(f"SELECT * FROM {table_name}").fetchall()
    
def insert_data(conn, insert_query, data):
    conn.cursor().executemany(insert_query, data)
    conn.commit()

def db_exists(db_name):
    return os.path.isfile(db_name)