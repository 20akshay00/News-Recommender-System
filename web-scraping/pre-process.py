import sqlite3
import pandas as pd
import re, string
from nltk.corpus import stopwords

stop_words = set(stopwords.words("english"))

def clean_up(txt):
    txt_without_stop_words = " ".join([word for word in txt.lower().split() if word not in stop_words])
    txt_without_punct = "".join([ch for ch in txt_without_stop_words if ch not in set(string.punctuation)])
    return re.sub(" +", " ", re.sub("\d", "", re.sub("[^\w\s]", "", txt_without_punct)))

# ----------------   
db_name = "news-db.sqlite"
tb_in_name = "articles"
tb_out_name = "articles_processed"
# ----------------   

conn = sqlite3.connect(db_name)
df = pd.read_sql_query(f"SELECT * FROM {tb_in_name}", conn)
conn.close()


for i in range(df.shape[0]):
    df["content"][i] = clean_up(df["content"][i])

conn = sqlite3.connect(db_name)
df.to_sql(tb_out_name, conn, if_exists="replace")
conn.close()