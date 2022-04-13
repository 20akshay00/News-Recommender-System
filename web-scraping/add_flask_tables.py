import sqlite3
conn = sqlite3.connect("news-db.sqlite")
create_user = f'CREATE TABLE users (id INTEGER PRIMARY KEY, username VARCHAR, email_address VARCHAR, password_hash VARCHAR)'
insert_user = f"""
    INSERT INTO users
    (id, username, email_address, password_hash)
    VALUES (?, ?, ?, ?)
    """
create_log = f'CREATE TABLE session_log (log_id INTEGER PRIMARY KEY, session_id INTEGER, user_id INTEGER, article_id INTEGER)'
insert_log = f"""
    INSERT INTO session_log
    (log_id, session_id, user_id, article_id)
    VALUES (?, ?, ?, ?)
    """

conn.cursor().execute(create_user)
conn.cursor().execute(create_log)
conn.cursor().execute(insert_user, [0, "admin", "admin@admin.com", "pwd"])
conn.cursor().execute(insert_log, [0, 0, 0, None])
conn.commit()
conn.close()