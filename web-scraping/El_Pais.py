from bs4 import BeautifulSoup
from time import sleep
from database_utils import insert_data
import requests, os, sqlite3

os.environ["https_proxy"] = "http://172.16.2.250:3128"

def scrape_from_page(url, category):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")

    if(soup.find("h1", class_ = "a_t") is None): return []

    title = soup.find("h1", class_ = "a_t").get_text()
    date = soup.find("a", id = "article_date_p").attrs['data-date'][:10] if not (soup.find("a", id = "article_date_p") is None) else None
    summary = soup.find("h2", class_ = "a_st").get_text()
    content = " ".join([elt.text for elt in soup.find_all("p")])[:-62]

    return [title, date, url, category, summary, content]

def get_topic_pages(page):
    soup = BeautifulSoup(page.content, "html.parser")
    urls_1 = list(set([elt.find("a")["href"] for elt in soup.find_all("article", class_='c c-d c--m')]))
    urls_2 = list(set([elt.find("a")["href"] for elt in soup.find_all("article", class_='c c-o c-d c--m')]))
    urls_incomplete = urls_1 + urls_2
    urls = [('https://english.elpais.com' + urls_incomplete[i]) for i in range(len(urls_incomplete))]
    return urls

def scrape(page_no, topic):
    URL = f"https://english.elpais.com/{topic}/{str(page_no)}"
    url_list = get_topic_pages(requests.get(URL))
    sleep(1)

    data = []

    for url in url_list:
        dt = scrape_from_page(url, topic)
        if (dt):
            data.append(dt)
            sleep(1)

    return data

def scrape_loop(start_pg, end_pg, topic, alert = False):
    data = []
    for pg in range(start_pg, end_pg):
        if(alert): print(f"Scraping page {pg}...\n")
        data += scrape(pg, topic)
        
    return data

dt = scrape_loop(6, 7, "science-tech", True)


#-----------------------------------------
db_name = "news-db.sqlite"
tb_name = "articles1"

insert = f"""
    INSERT INTO {tb_name}
    (headline, date, url, category, summary, content)
    VALUES (?, ?, ?, ?, ?, ?)
    """

conn = sqlite3.connect(db_name)
insert_data(conn, insert, dt)
conn.close()
