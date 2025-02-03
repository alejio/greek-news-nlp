# roadmap.md

## Stage 1
- Data collection: I created data_collection/scraper_gazzetta_async.py to scrape the gazzetta.gr website. This output csv files.
- Data storage: I set up a relevant PostgreSQL database and bulk inserted the csv files into the database.
- Data analysis: In notebooks/prototyping.ipynb and notebooks/sentiment_eda.ipynb I explored the data. I have seen some interesting things but I need to do more analysis. However, I will like to proceed to the next stage now so I have something end-to-end to show.

## Stage 2
- Web application: I now need to create an MVP web application that does basic data visualization. I want the web app to look and feel good so I am not restricted by the Python ecosystem. This app will need to be supported by a Python backend. The app will give me ideas for the next stage.
- I've made a simple FastAPI backend and added a router for articles.
- Now I want to dockerize the app and run it in a container.

## Stage 3
- Some ideas include:
  - Data collection: I will add football match details such as results, major refereeing decisions such as red cards and penalties, etc. I can also add more websites to scrape.
  - Data storage: I should adapt scrapers to write directly to the database.
