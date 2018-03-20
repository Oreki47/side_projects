#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    About part.
"""

__author__ = 'Oreki47'
from flask import render_template

def run_about(app, engine, config):

    @app.route('/about/')
    def about():
        welcome_message = 'Hello! This is something about me.'
        return render_template('about.html', welcome_message=welcome_message)
