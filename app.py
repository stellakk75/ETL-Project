# Import Libraries
import datetime as dt
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import psycopg2
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Flask Setup
#################################################
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
#################################################

# Database Setup
connection = psycopg2.connect(user = "postgres",
                                  password = "postgres",
                                  host = "127.0.0.1",
                                  port = "5432",
                                  database = "quotes_db")
db_string = "postgres://postgres:postgres@localhost:5432/quotes_db"
engine = connection.cursor()
db = create_engine(db_string)


@app.route("/quotes")
def quotes():
    engine.execute("SELECT COUNT(*) FROM quotes;")
    total_tags = engine.fetchone()  
    quotes_all_df = pd.read_sql_query(
        '''SELECT quotes.quote_id,quotes.author_name,quotes.quote,tags.tag \
                    FROM quotes \
                    JOIN \
                    tags ON quotes.quote_id = tags.quote_id \
                    ORDER BY quotes.quote_id''',db
                                    )
    

    return jsonify(quotes_all_df.values.tolist())
@app.route("/top10tags")
def top10tags():
    top10tags_df = pd.read_sql_query(
                   ''' SELECT tag,count(*) FROM TAGS \
                       GROUP BY tag \
                       ORDER BY count(*) DESC LIMIT 10
                   ''' , db
                                    )  
    i = 0
    cnt = 0
    tags_dict = {}
    top10 = []
    for i in range(len(top10tags_df.to_dict('split')['data'])):
        top_dict = {}
        tags = top10tags_df.to_dict('split')['data'][i][0]
        cnt =  top10tags_df.to_dict('split')['data'][i][1]

        data = {
            
            'tags' : tags,
            'quote_count' : cnt
        }
        top10.append(data)
    return jsonify(top10)


if __name__ == "__main__":
    app.run(debug=True)
