#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    game part
"""

__author__ = 'Oreki47'


import tweepy
import numpy as np
import warnings

from flask import Flask, render_template, redirect, url_for, request
from src.utilities import clean_text, HashtagFeatureForm, GeoFeatureForm
warnings.filterwarnings("ignore")

def run_sentiment_engine(app, engine, config, clf, api):

    @app.route('/sentiments', methods=('GET', 'POST'))
    def sentiments():

        hashtag_form = HashtagFeatureForm()
        geo_form = GeoFeatureForm()

        trends = []
        for trend in api.trends_place('2442047')[0].get('trends')[:3]:
            name = trend.get('name')
            tweets = []
            for item in tweepy.Cursor(api.search, q=name).items(3):
                tweets.append(item.text)

            tweets = np.array(list(map(clean_text, tweets)))
            sentiments = [clf.predict(tweet, highlight=False) for tweet in tweets]

            trends.append((name, list(zip(tweets, sentiments))))

        if request.method == 'POST':
            form_name = request.form['form-name']
            if form_name == 'form1':
                if hashtag_form.is_submitted():
                    line = hashtag_form.review_text.data
                    return redirect(url_for('sentiments_hashtags', hashtag=line, api=api))
                return render_template('welcome.html', welcome_message='Buh')
            elif form_name == 'form2':
                if geo_form.is_submitted():
                    line = geo_form.review_text.data
                    return redirect(url_for('sentiments_woeid', woeid=line))
                return render_template('welcome.html', welcome_message="here")


        welcome_message = "Tweet Trends Sentimental Analysis"
        return render_template('tweet_welcome.html', welcome_message=welcome_message,
            hashtag_form=hashtag_form, list_tweets=trends,
            geo_form=geo_form)


    @app.route('/sentiments/hashtag', methods=('GET', 'POST'))
    def sentiments_hashtags():
        hashtag = request.args['hashtag']
        tweets = []
        for item in tweepy.Cursor(api.search, q=hashtag).items(100):
            tweets.append(item.text)

        tweets = np.array(list(map(clean_text, tweets)))
        sentiments = [clf.predict(tweet, highlight=False) for tweet in tweets]
        pos_ids = np.array([i for i, sentiment in enumerate(sentiments) if sentiment == 'pos'])
        pos_tot = len(pos_ids)
        pos_tweets = tweets[pos_ids][:3]
        neg_tot = 100 - pos_tot
        neg_tweets = tweets[~pos_ids][:3]

        return render_template('tweet_hashtag.html', welcome_message="results", hashtag=hashtag,
            pos_tweets=pos_tweets, pos_tot=pos_tot,
            neg_tweets=neg_tweets, neg_tot=neg_tot)


    @app.route('/sentiments/woeid', methods=('GET', 'POST'))
    def sentiments_woeid():
        woeid = request.args['woeid']

        trends = []
        for trend in api.trends_place(woeid)[0].get('trends')[:3]:
            name = trend.get('name')
            tweets = []
            for item in tweepy.Cursor(api.search, q=name).items(3):
                tweets.append(item.text)

            tweets = np.array(list(map(clean_text, tweets)))
            sentiments = [clf.predict(tweet, highlight=False) for tweet in tweets]

            trends.append((name, list(zip(tweets, sentiments))))

        return render_template('tweet_woeid.html', welcome_message="", list_tweets=trends)