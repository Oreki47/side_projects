import os, sys, time, re
import requests, json, logging
import configparser
import numpy as np
import string
import html
import nltk
from nltk.corpus import stopwords
from nltk import word_tokenize
import pickle

from datetime import datetime
from multiprocessing import Pool
from sqlalchemy import create_engine
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField

class ConfigData(object):
    def __init__(self, filename):
        config = configparser.ConfigParser()
        config.optionxform = str
        config.read(filename)
        self.mysql_username = config.get('MySQL', 'username')
        self.mysql_password = config.get('MySQL', 'password')
        self.mysql_game_database = config.get('MySQL', 'game_database')
        self.mysql_game_app_table = config.get('MySQL', 'game_app_table')
        self.mysql_game_user_like_table = config.get('MySQL', 'game_user_like_table')
        self.mysql_game_popularity_table = config.get('MySQL', 'game_result_popularity_based_table')
        self.mysql_game_content_table = config.get('MySQL', 'game_result_content_based_table')
        self.mysql_game_item_table = config.get('MySQL', 'game_result_item_based_table')
        self.mysql_game_als_table = config.get('MySQL', 'game_result_als_table')
        self.mysql_port = config.get('MySQL', 'port')

        self.consumer_key = config.get('Twitter', 'consumer_key')
        self.consumer_secret = config.get('Twitter', 'consumer_secret')
        self.access_token = config.get('Twitter', 'access_token')
        self.access_token_secret = config.get('Twitter', 'access_token_secret')


def mysql_enginer_init(database, config):
    engine_url = 'mysql+mysqldb://%s:%s@127.0.0.1:%s/%s?charset=utf8mb4' \
        % (config.mysql_username, config.mysql_password, config.mysql_port, database)
    engine = create_engine(engine_url, echo=False)
    return engine


def clean_text(tweet):
    return ' '.join(re.sub(r"(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())


class BaseModel:
    def __init__(self):
        self.lemmatizer = nltk.WordNetLemmatizer()
        self.stop = stopwords.words('english')

        self.model = None
        self.vec = None

    # Load Vec
    def load_vec(self, vec_path, mode='rb'):
        with open(vec_path, mode) as pkl_file:
            self.vec = pickle.load(pkl_file)

    # Load Model
    def load_model(self, model_path, mode='rb'):
        with open(model_path, mode) as pkl_file:
            self.model = pickle.load(pkl_file)

    # Preprocessing
    def preprocessing(self, line: str) -> str:
        line = html.unescape(str(line))
        line = str(line).replace("can't", "cann't")
        line = word_tokenize(line.lower())

        tokens = []
        negated = False
        for t in line:
            if t in ['not', "n't", 'no']:
                negated = not negated
            elif t in string.punctuation or not t.isalpha():
                negated = False
            else:
                tokens.append('not_' + t if negated else t)

        tokens = [self.lemmatizer.lemmatize(t, 'v') for t in tokens if t not in self.stop]

        return ' '.join(tokens)

    # Predict
    def predict(self, line):
        if self.model is None or self.vec is None:
            print('Modle / Vec is not loaded')
            return ""

        line = self.preprocessing(line)
        features = self.vec.transform([line])

        return self.model.predict(features)[0]


class ReviewModel(BaseModel):
    def __init__(self):
        super().__init__()

        self.load_vec('models/tf_vec.pkl')
        self.load_model('models/mnb_model.pkl')

    def predict(self, line, highlight=True):
        sentiment = super(ReviewModel, self).predict(line)

        # highlight words, hack
        if highlight:
            highlight_words = [w for w in self.preprocessing(line).split()
                               if super(ReviewModel, self).predict(w) == sentiment]
            return sentiment, highlight_words
        else:
            return sentiment


class GameFeatureForm(FlaskForm):
    review_text = StringField('Review Text')
    go = SubmitField("Let\'s see what you like!")

class HashtagFeatureForm(FlaskForm):
    review_text = StringField('Review Text')
    go = SubmitField("Go!")

class GeoFeatureForm(FlaskForm):
    review_text = StringField('Review Text')
    go = SubmitField("Where to?")