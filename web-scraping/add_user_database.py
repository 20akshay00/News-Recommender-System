import sqlite3
conn = sqlite3.connect("news-db.sqlite")
create = f'CREATE TABLE users (id INTEGER PRIMARY KEY, username VARCHAR, email_address VARCHAR, password_hash VARCHAR)'
insert = f"""
    INSERT INTO users
    (id, username, email_address, password_hash)
    VALUES (?, ?, ?, ?)
    """

conn.cursor().execute(create)
conn.cursor().execute(insert, [0, "admin", "admin@admin.com", "pwd"])
conn.commit()
conn.close()