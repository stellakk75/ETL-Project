from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo
import scrape_craigslist

app = Flask(__name__)

# Use flask_pymongo to set up mongo connection
mongo = PyMongo(app, uri="mongodb://localhost:27017/weather_app")

@app.route("/")
def index():
    listings = mongo.db.listings.find()
    return render_template("index.html", listings=listings)


@app.route("/quotes")

@app.route("/authors")

@app.route("/authors/<author name>")

@app.route("/tags")

@app.route("/tags/<tag>")

@app.route("/top10tags")

if __name__ == "__main__":
    app.run(debug=True)
