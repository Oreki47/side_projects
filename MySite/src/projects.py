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
			('/home/ethan/Dropbox/Github/side_projects/MySite/imgs/1.jpg', '/recommendation', 'Game Recommendation'),
			('/home/ethan/Dropbox/Github/side_projects/MySite/imgs/1.jpg', '/sentiments', 'Tweet Data Sentimental Analysis')
		]
		return render_template('projects.html', welcome_message=welcome_message, projects_list=projects_list)