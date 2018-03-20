#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    contact part
"""

__author__ = 'Oreki47'

from flask import Flask, render_template

def run_contact(app, engine, config):

	@app.route('/contact/')
	def contact():
		welcome_message = 'Working...'
		return render_template('contact.html', welcome_message=welcome_message)
   


