from bs4 import BeautifulSoup
from time import sleep
from database_utils import insert_data
import requests, os, sqlite3

os.environ["https_proxy"] = "http://172.16.2.250:3128"

def scrape_from_page(url, category):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    title = soup.find("header", {"class" : "article-title"}).find("h1").get_text()
    content = " ".join([elt.get_text() for elt in soup.find("div", {"id" : "article_content"}).find_all("p")])
    summary = soup.find("h2", {"class" : "subline"}).get_text()
    date = soup.time.attrs['datetime'][:10] if not(soup.time is None) else None

    return [title, date, url, category, summary, content]

def get_topic_pages(page):
    soup = BeautifulSoup(page.content, 'html.parser')
    urls = list(set([elt["href"] for elt in soup.find("section", {"id" : "repo-list"}).find_all("a")]))
    return urls

def scrape(page_no, topic):
    URL = "https://www.ibtimes.co.in/" + topic + "/page/" + str(page_no)
    url_list = get_topic_pages(requests.get(URL))
    sleep(1)

    data = []

    for url in url_list:
        data.append(scrape_from_page(url, topic))
        sleep(1)

    return data

def scrape_loop(start_pg, end_pg, topic, alert = False):
    data = []
    for pg in range(start_pg, end_pg):
        if(alert): print(f"Scraping page {pg}...\n")
        data += scrape(pg, topic)
    
    return data

dt = scrape_loop(2, 52, "business", True)

#-----------------------------------------
db_name = "news-db.sqlite"
tb_name = "articles"

insert = f"""
    INSERT INTO {tb_name}
    (headline, date, url, category, summary, content)
    VALUES (?, ?, ?, ?, ?, ?)
    """

conn = sqlite3.connect(db_name)
insert_data(conn, insert, dt)
conn.close()