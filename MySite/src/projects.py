#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    contact part
"""

__author__ = 'Oreki47'

from flask import Flask, render_template

def run_projects(app, engine, config):

	@app.route('/projects/')
	def projects():
		welcome_message = 'see below of a list of available projects'
		projects_list = [
			('/static/imgs/game.png', '/recommendation', 'Game Recommendation'),
			('/static/imgs/sentiments.jpg', '/sentiments', 'Tweet Data Sentimental Analysis')
		]
		return render_template('projects.html', welcome_message=welcome_message, projects_list=projects_list)