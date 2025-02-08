# roadmap.md

## Stage 1
- Data collection: I created data_collection/scraper_gazzetta_async.py to scrape the gazzetta.gr website. This output csv files.
- Data storage: I set up a relevant PostgreSQL database and bulk inserted the csv files into the database.
- Data analysis: In notebooks/prototyping.ipynb and notebooks/sentiment_eda.ipynb I explored the data. I have seen some interesting things but I need to do more analysis. However, I will like to proceed to the next stage now so I have something end-to-end to show.

## Stage 2
- I've made a simple FastAPI backend and added a router for articles.
- I have setup CI/CD pipeline with Github Actions.
- I've created a Dockerfile and docker-compose.yml file to run the app in a container. It doesn't quite work as intended because the database is empty. I will deal with this at a later point. Also considering whether I should use a managed database service like AWS RDS.
- Web application: I created a simple frontend in Next.js. It allows visualising some data by hitting the backend endpoints which in turn hit the database.

## Stage 3
- [INSERT IDEAS]


## Ideation
- Some ideas include:
  - Data collection: I will add football match details such as results, major refereeing decisions such as red cards and penalties, etc. I can also add more websites to scrape.
  - Data storage: I should adapt scrapers to write directly to the database.
  - I am thinking of adding a chatbot that will answer questions about the data. It would be great if it could do visualisations on the fly based on natural language queries. For example: "How often does journalist Κώστας Νικολακόπουλος complain about referee decisions after defeats of Olympiakos?"
