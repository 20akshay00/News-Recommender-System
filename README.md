# Alligator's Den

A News Recommender System, made as part of IDC410 (Machine Learning) course at IISERM.

## Setting up the environment

- Using `pip`:
```
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

- Using `conda`:
```
conda env create --file=environments.yml
```

## Running the application
To run the web server for the application, go to the root directory and execute `./flask_api/run.py`. 

## Scraping articles
Shift into the `./web-scraping` directory.
- Run `database_interface.py` to create the news-db and articles table
- Change the parameters in `scraper.py` to scrape articles from one of these four websites: El Pais, IBTimes, India Today, Republic World. 
- Run `clean_articles.py` to fix some issues in the scraped content
- Run `pre-process.py` to perform cleaning, lemmatization and stemming of the content (which are stored in two new tables; `articles_cleaned`, `articles_processed`). 
- Finally, use `add_flask_tables.py` to add the table templates for user authentication and session logging in the same database, for utilization by the Flask API.

**Note:** You must manually change the input and output databases for some of the scripts above, based on your choice of the initial database file.

## Misc.
Any jupyter notebooks found in this repository is no longer necessary, and was simply used as a sandbox to experiment our ideas before we implemented them into `.py` scripts that are finally used in the API. For example, the `./recommender-bots` directory simply contains informal jupyter notebooks, but the only relevant file to the application is `./flask_api/news_server/recommender.py`.