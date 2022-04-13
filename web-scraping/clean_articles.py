import sqlite3, re
import pandas as pd
from database_utils import run_query

#-----------
db_in_name = "news-db.sqlite"
db_out_name = "news-db_.sqlite"
tb_name = "articles"
#-----------

conn = sqlite3.connect(db_in_name)
df = pd.read_sql("SELECT * FROM articles", conn)
conn.close()

df.drop_duplicates(subset = ["headline"], keep = 'first')

for i in range(df.shape[0]):
    df["content"][i] = re.sub("English version.*", " ", df["content"][i])
    df["content"][i] = "\n".join([elt for elt in df["content"][i].split("\n") if not any([(word in elt) for word in ["READ", "Also Read", "twitter", "Disclaimer", "Image", "IMAGE"]])])

conn = sqlite3.connect(db_out_name)
df.to_sql(tb_name, conn, if_exists="replace", index = False)
conn.close()