from bs4 import BeautifulSoup
from time import sleep
from database_utils import insert_data
import requests, os, sqlite3
from datetime import datetime

os.environ["https_proxy"] = "http://172.16.2.250:3128"

def scrape_from_page(url, category):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    if(soup.find("h1", itemprop = "headline") is None): return []

    title = soup.find("h1", itemprop = "headline").get_text()
    date = datetime.strftime(datetime.strptime(soup.find("dt", class_ = "pubdata").get_text(), '%B %d, %Y'), "%Y-%m-%d")
    summary = soup.find("h2").get_text()
    content = " ".join([elt.get_text() for elt in soup.find("div", {"class" : "story-section"}).find_all("p")])

    return [title, date, url, category, summary, content]

def get_topic_pages(page):
    soup = BeautifulSoup(page.content, "html.parser")
    return ["https://www.indiatoday.in" + elt.find("a")["href"] for elt in soup.find_all("div", {"class" : "catagory-listing"})]

def scrape(page_no, topic):
    URL = f"https://www.indiatoday.in/{topic}?page={page_no}"
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

dt = scrape_loop(2, 3, "science", True)

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