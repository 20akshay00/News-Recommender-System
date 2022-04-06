# database = "news_db.sqlite"
# table_name = "articles"

import sqlite3, os
from database_utils import table_exists, show_table, run_query, db_exists

db_name = input("Enter database name: ") + ".sqlite"
if not db_exists(db_name): 
    if(input(f"Database does not exist. Create? (y/n): ") == "n"):
        exit()

conn = sqlite3.connect(db_name)

table_name = input("Enter table name: ")

if not (table_exists(conn, table_name)): 
    if(input(f"Table \"{table_name}\" does not exist. Create? (y/n): ") == "y"):
        create = f'CREATE TABLE {table_name} (article_id INTEGER PRIMARY KEY, headline VARCHAR, date DATE, url VARCHAR, category VARCHAR, summary VARCHAR, content VARCHAR)'
        run_query(conn, create)
    else:
        conn.close()
        quit()

while(True):
    ans = input("\n\nUSE DB Browser for more features--\n\nWhat do you want to do?\n 1) Delete table \n 2) Exit \n\n >")

    if(ans == "1"):
        if(input("Are you sure?? (y/n): ") == "y"):
            if(input("Super sure?? (y/n): ") == "y"):
                if(input("This process is NOT reversible. Last chance (y/n): ") == "y"):
                    delete = f'DROP TABLE {table_name}'
                    run_query(conn, delete)

        print(f"Deleted \"{table_name}\".")
        conn.close()
        exit()
        
    elif(ans == "2"):
        conn.close()
        quit()

# insert = f"""
#     INSERT INTO {table_name}
#     (title, date, url, category, summary, content)
#     VALUES (?, ?, ?, ?, ?, ?)
#     """