from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
from flask import Flask, render_template, flash, request, send_from_directory
from flask import Flask, Response, request, render_template, redirect, url_for
#from cache import *

import flask_login
import sys
from flask import Flask, redirect, url_for, session, request
from get_wards_to_visit import registered_voters_didnt_turn_out
#from cache import closest_name
import random
from get_map import get_map

# App config.
DEBUG = True

app = Flask(__name__)
app.config.from_object(__name__)






#login page
@app.route("/", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        #default page
        wards = []
        html = get_map(wards)
        return render_template('index.html', map= html)
    if request.method == 'POST':
        #they entered params 
        #render new html page
    #The request method is POST (page is recieving data)
        flip_percent = float(request.form['flip_percent'])
        hispanic_threshhold = float(request.form['hispanic_threshold'])
        #dictionary of wards to visit
        wards_to_visit_dict = registered_voters_didnt_turn_out.execute(flip_percent,hispanic_threshhold)


        
        print("flip_percent: ", flip_percent)
        print("hispanic_threshhold: ", hispanic_threshhold)
        wards = list(wards_to_visit_dict.keys())
        print("wards to visit: ", wards)
        html = get_map(wards)
        print (html)


        return render_template('index.html', map= html)





if __name__ == "__main__":
    app.run(host='0.0.0.0')