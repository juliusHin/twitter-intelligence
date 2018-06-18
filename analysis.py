# -*- encoding: utf-8 -*-

import matplotlib.pyplot as pl
from collections import Counter
import sqlite3
import os.path
import numpy as np
from geopy.geocoders import Nominatim
from flask import Flask, render_template
import json

ROOT_DIR = os.path.dirname(os.pardir)
db_path = os.path.join(ROOT_DIR, "TweetAnalysis.db")

def analysis_graph():

    with sqlite3.connect(db_path) as db:

        conn = db
        c = conn.cursor()
        c.execute("SELECT  username, count(*) as tekrar FROM Tweet  group by username order by tekrar desc LIMIT 10")
        data = c.fetchall()
        ilk=[]
        y=[]
        i=0
        for row in data:
            ilk.append(row[0])
            y.append(row[1])
            i=i+1
            pl.figure(1)
            x = range(i)

        pl.bar(x, y, align='center')
        pl.xticks(x, ilk)
        #pl.plot(x, y, "-")
        pl.title('User - Tweet Count')
        pl.xlabel('Username')
        pl.ylabel('Tweet Count')
        pl.show()

        c.execute("SELECT hashtag from Tweet")
        hashtag_list = []
        for row in c.fetchall():
            if " " in ''.join(row):
                for m in ''.join(row).split(' '):
                    hashtag_list.append(m)
            else:
                signle_item  = ''.join(row)
                hashtag_list.append(signle_item)

        counter = Counter(hashtag_list)

        pl.rcdefaults()
        keys = counter.keys()
        y_pos = np.arange(len(keys))
        performance = [counter[k] for k in keys]
        error = np.random.rand(len(keys))

        pl.barh(y_pos, performance, xerr=error, align='center', alpha=0.4, )
        pl.yticks(y_pos, keys)
        pl.xlabel('quantity')
        pl.title('hashtags')
        pl.show()

analysis_graph()

def location_analysis():
    with sqlite3.connect(db_path) as db:
        conn = db
        c = conn.cursor()

        locxy = []
        c.execute("Select place from location")
        loc_array = c.fetchall()

        # mapping
        geo_data = {

            "features": []
        }
        for x in range(len(loc_array)):
            if (loc_array[x] != ''):
                geolocator = Nominatim()
                location = geolocator.geocode(loc_array[x])
                locxy.append(location.latitude)
                locxy.append(location.longitude)

                geo_json_feature = {
                    "lat": location.latitude,
                    "lng": location.longitude
                }

                geo_data['features'].append(geo_json_feature)
                locxy.clear()
        json_location = json.dumps(geo_data)
        return json_location

app = Flask(__name__)

@app.route('/locations')
def map():
   location = location_analysis()

   return render_template('locations.html', location = location)

if __name__ == '__main__':
    app.run()