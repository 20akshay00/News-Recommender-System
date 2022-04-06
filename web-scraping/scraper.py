from bs4 import BeautifulSoup
from time import sleep
from database_utils import insert_data
import requests, os, sqlite3
from datetime import datetime

# sets proxy
os.environ["https_proxy"] = "http://172.16.2.250:3128"

def scrape_from_page(url, category, website):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")

    if(website == "IBTimes"):
        title = soup.find("header", {"class" : "article-title"}).find("h1").get_text()
        content = " ".join([elt.get_text() for elt in soup.find("div", {"id" : "article_content"}).find_all("p")])
        summary = soup.find("h2", {"class" : "subline"}).get_text()
        date = soup.time.attrs['datetime'][:10] if not(soup.time is None) else None
    
    elif(website == "ElPais"):
        if(soup.find("h1", class_ = "a_t") is None): return []

        title = soup.find("h1", class_ = "a_t").get_text()
        date = soup.find("a", id = "article_date_p").attrs['data-date'][:10] if not (soup.find("a", id = "article_date_p") is None) else None
        summary = soup.find("h2", class_ = "a_st").get_text()
        content = " ".join([elt.text for elt in soup.find_all("p")])[:-62]

    elif(website == "IndiaToday"):
        if(soup.find("h1", itemprop = "headline") is None): return []

        title = soup.find("h1", itemprop = "headline").get_text()
        date = datetime.strftime(datetime.strptime(soup.find("dt", class_ = "pubdata").get_text(), '%B %d, %Y'), "%Y-%m-%d")
        summary = soup.find("h2").get_text()
        content = " ".join([elt.get_text() for elt in soup.find("div", {"class" : "story-section"}).find_all("p")])

    return [title, date, url, category, summary, content]

def get_topic_pages(page, website):
    soup = BeautifulSoup(page.content, 'html.parser')

    if(website == "IBTimes"):
        urls = list(set([elt["href"] for elt in soup.find("section", {"id" : "repo-list"}).find_all("a")]))

    elif(website == "ElPais"):
        urls_1 = list(set([elt.find("a")["href"] for elt in soup.find_all("article", class_='c c-d c--m')]))
        urls_2 = list(set([elt.find("a")["href"] for elt in soup.find_all("article", class_='c c-o c-d c--m')]))
        urls_incomplete = urls_1 + urls_2
        urls = [('https://english.elpais.com' + urls_incomplete[i]) for i in range(len(urls_incomplete))]

    elif(website == "IndiaToday"):
        urls = ["https://www.indiatoday.in" + elt.find("a")["href"] for elt in soup.find_all("div", {"class" : "catagory-listing"})]

    return urls

def scrape(page_no, topic, website):
    data = []
    
    if(website == "IBTimes"): URL = f"https://www.ibtimes.co.in/{topic}/page/{page_no}"
    elif(website == "ElPais"): URL = f"https://english.elpais.com/{topic}/{page_no}"
    elif(website == "IndiaToday"): URL = f"https://www.indiatoday.in/{topic}?page={page_no}"
    else: quit()

    url_list = get_topic_pages(requests.get(URL), website)
    sleep(1)

    for url in url_list:
        dt = scrape_from_page(url, topic, website)
        if (dt):
            data.append(dt)
            sleep(1)

    return data

def scrape_loop(website, start_pg, end_pg, topic, alert = False):
    data = []
    for pg in range(start_pg, end_pg):
        if(alert): print(f"Scraping page {pg}...\n")
        data += scrape(pg, topic, website)
    
    return data

dt = scrape_loop("IndiaToday", 1, 16, "world", True)

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