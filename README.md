# ETL-Project

**This group project scrapes the website http://quotes.toscrape.com/ for quotes, tags, authors with their date of birth and description. Then, the data is stored into MongoDB and later extracted and loaded into Postgres. Three tables with created with its associated keys within Postgres. A FLASK API with multiple endpoints are created to portray the data. See below for the available API routes.**

  * quotes:    http://127.0.0.1:5000/quotes
  * authors:   http://127.0.0.1:5000/authors
  * tags:      http://127.0.0.1:5000/tags
  * top10tags :http://127.0.0.1:5000/top10tags
