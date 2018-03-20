#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    game part
"""

__author__ = 'Oreki47'
from flask import Flask, render_template

def run_sentiment_engine(app, engine, config):

    @app.route('/sentiments')
    def sentiments():
        welcome_message = "Place Holder for sentimental Analysis"
        return render_template('index.html', welcome_message=welcome_message)


