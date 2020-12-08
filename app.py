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

#Home API for available routes 
@app.route("/")
def welcomeHome():
    """List of all available api routes."""
    return (
        f"Welcome! Below is a list of all available routes:<br/>"       
        f"/api/v1.0/quotes<br/>"   
        f"/api/v1.0/authors<br/>"  
        f"/api/v1.0/tags<br/>"     
        f"/api/v1.0//top10tags<br/>"
    )

#Displays total # of quotes with each quote and associated author and tags
@app.route("/quotes")
def quotes():
    engine.execute("SELECT COUNT(*) FROM quotes;")
    total_cnt = engine.fetchone()  
    quotes_all_df = pd.read_sql_query(
        '''SELECT quotes.quote_id,quotes.author_name,quotes.quote,tags.tag \
                    FROM quotes \
                    JOIN \
                    tags ON quotes.quote_id = tags.quote_id \
                    ORDER BY quotes.quote_id''',db
                                    )
    
    xx = quotes_all_df.groupby(['quote_id','author_name','quote']).tag.apply(list).reset_index()
    quotes_list = []
    i = 0
    for i in range(len(xx.to_dict('split')['data'])):
        author_name = xx.to_dict('split')['data'][i][1]
        quote =  xx.to_dict('split')['data'][i][2]
        tags = xx.to_dict('split')['data'][i][3]
        data = {
            'text' : quote,
            'author name' : author_name,
            'tags' : tags
        }
        quotes_list.append(data)
    quotes_dict =[]
    data = {
    'total' :total_cnt,
    'quotes':quotes_list
     }
    quotes_dict.append(data)    
    return jsonify(quotes_dict)

#Displays total number of authors with details of each other and all the author's quotes with associated tags
@app.route("/authors")
def authors():
    quotes_author_df = pd.read_sql_query('''
                            SELECT author.author_name,author.description,author.dob,
                                  (SELECT COUNT(*) FROM quotes
                                   WHERE quotes.author_name = author.author_name),
                                  quotes.quote,tags.tag,quotes.quote_id
                            FROM author
                            JOIN quotes
                            ON author.author_name=quotes.author_name
                            JOIN tags
                            ON tags.quote_id = quotes.quote_id
                            ORDER BY author.author_name
                                    ''',db
                                     )
    total_author_df = pd.read_sql_query(
                            '''SELECT COUNT(*) FROM  author''',db)
    total = total_author_df.values.tolist()                        
    xx = quotes_author_df.groupby(['quote_id','author_name','description',
                               'dob','count','quote']).tag.apply(list).reset_index()
    xx.sort_values(by=['author_name'], inplace=True)
    quotes_authos_temp = xx.to_dict('split')['data']
    quotes_author_list = []
    full_author_list = []
    previous_author_name =''
    previous_flag = False
    first_iteration = True
    quotes_list = []
    quotes_tags = []

    for i in range(len(xx.to_dict('split')['data'])):
        new_quote_id = quotes_authos_temp[i][0]
        new_author_name = quotes_authos_temp[i][1]
        new_born = quotes_authos_temp[i][3]
        new_description =  quotes_authos_temp[i][2]
        new_count = quotes_authos_temp[i][4]
        new_quotes = quotes_authos_temp[i][5]
        new_tags = quotes_authos_temp[i][6]
        author_name = new_author_name
        if first_iteration:
                author_name = quotes_authos_temp[i][1]
                born = quotes_authos_temp[i][3]
                description =  quotes_authos_temp[i][2]
                count = quotes_authos_temp[i][4]
                quotes = quotes_authos_temp[i][5]
                tags = quotes_authos_temp[i][6]
                quote_text = {
                    'text':new_quotes,
                    'tags':new_tags
                            }
                quotes_list.append(quote_text)
                data = {
                    'name' : previous_author_name,
                    'description' : description,
                    'born' : born,
                    'count' : count,
                    'quotes':quote_text
                    }
                previous_author_name = author_name
                first_iteration = False

        else:
            if author_name == previous_author_name:
                        quote_text = {
                            'text':new_quotes,
                            'tags':new_tags
                            }
                        quotes_list.append(quote_text)
                        
            else:
                data = {
                    'name' : previous_author_name,
                    'description' : description,
                    'born' : born,
                    'count' : count,
                    'quotes':quotes_list
                }
                quotes_author_list.append(data)
                quotes_list = []
                quotes_tags = []
                previous_author_name = author_name

    data = {
        'total number of authors': total,
        'details': quotes_author_list
            }
    full_author_list.append(data)
    return jsonify(full_author_list)

#Displays total # of tags with details of each tag including # of quotes it appears in 
# and the all the quotes with the tag and the other associated tags 
@app.route("/tags")
def tags():
    #Define DataFrame from db query
    quotes_tags_df = pd.read_sql_query(
                    '''
                   SELECT quotes.quote_id, quotes.quote,tags.tag
                   FROM  quotes
                   JOIN tags
                   ON tags.quote_id = quotes.quote_id
                    ''', db           )
    #Define unique tags from db
    unique_tags_df = pd.read_sql_query('''SELECT DISTINCT tag FROM tags''',db)
    unique_tags_df_list = unique_tags_df.values.tolist()
    #Define in iterable format
    xx = quotes_tags_df.groupby(['quote_id','quote']).tag.apply(list).reset_index()
    tags_quote_temp = xx.to_dict('split')['data']
    #Loop through to extract the requested data and initialize list
    quote_list = []
    tag_list = []
    quote_tags = []
    quote_tags_details = []
    full_tags_details = []
    total_tags_count = 0
    quote_count = 0
    first_iteration = True
    quote_cnt = 0
    previous_quote_id = 0
    for j in unique_tags_df_list:
        # Pick tag and loop through to check all tags and collect quote data
        quote_list = []
        tag_list = []
        quote_count = 0
        quote_cnt = 0
        quote_tags= []
        total_tags_count = total_tags_count + 1
        for i in range(len(xx.to_dict('split')['data'])):
            quote_id = tags_quote_temp[i][0]
            quote = tags_quote_temp[i][1]
            tag = tags_quote_temp[i][2]
            if j[0] in tag:
                quote_cnt = quote_cnt + 1
                #print(f'{j[0]} matched in {tag}')
                data = {
                'text': quote,
                'tags':tag}
                quote_tags.append(data)
        data = {'name':j,
        'number_of_quotes':quote_cnt,
        'quotes':quote_tags}
        quote_tags_details.append(data)
    data = {'count' : total_tags_count,
       'details':quote_tags_details}

    full_tags_details.append(data)   

    return jsonify(results = full_tags_details)  

#Displays top 10 tags with the number of quotes the tag appeared in
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
