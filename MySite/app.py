#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    simple flask app
"""

__author__ = 'Oreki47'


import os, sys
from flask import Flask, render_template
import json, sqlalchemy
import tweepy

sys.path.insert(0, os.path.abspath('/home/ethan/Dropbox/Github/side_projects/MySite'))
from src.utilities import ConfigData, mysql_enginer_init, ReviewModel
from src.game_engine import run_game_engine
from src.sentiment_engine import run_sentiment_engine
from src.contact import run_contact
from src.projects import run_projects
from src.about import run_about

def main():
	app = Flask(__name__)
	app.config.from_pyfile('config.py')

	CONFIG_PATH = '/home/ethan/Dropbox/Github/side_projects/MySite/src/config.ini'

	config = ConfigData(CONFIG_PATH)
	engine = mysql_enginer_init(config.mysql_game_database, config)
	clf = ReviewModel()

	auth = tweepy.OAuthHandler(config.consumer_key, config.consumer_secret)
	auth.set_access_token(config.access_token, config.access_token_secret)
	api = tweepy.API(auth) 

	@app.route('/')
	@app.route('/index')
	def index():
		welcome_message = "Hello World!"
		return render_template('welcome.html', welcome_message=welcome_message)

	run_about(app, engine, config)
	run_projects(app, engine, config)
	run_contact(app, engine, config)
	run_game_engine(app, engine, config)
	run_sentiment_engine(app, engine, config, clf, api)
	
	app.run(debug=True, port=5001, threaded=True)
	
if __name__ == '__main__':
	main()
	



