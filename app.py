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


@app.route("/scrape")
def scraper():
    listings = mongo.db.listings
    listings.drop()
    listings_data = scrape_craigslist.scrape()
    listings.insert_many(listings_data)
    return redirect("/", code=302)


if __name__ == "__main__":
    app.run(debug=True)
