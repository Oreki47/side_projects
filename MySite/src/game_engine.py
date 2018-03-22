#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    game part
"""

__author__ = 'Oreki47'
from flask import Flask, render_template, redirect, url_for
from src.utilities import GameFeatureForm


def run_game_engine(app, engine, config):

    @app.route('/recommendation/<string:user_id>')
    def recommendation_user(user_id):
        result = engine.execute('''
            SELECT g1, g2, g3, g4, g5, g6, g7, g8, g9, g10 FROM %s WHERE user_id=%s;
            ''' % (config.mysql_game_user_like_table, user_id)).first()

        if result is None:
            message = "Sorry, but steam id %s is not in our system." % user_id
            return render_template('recommendation.html', user_id='error',
                lst_recommended_games=[], result_message=message)
        
        lst_recommended_games = []
        for app_id in list(result):
            app_data = engine.execute('''
                            SELECT name, initial_price, header_image FROM %s WHERE steam_appid = %s;
                        ''' % (config.mysql_game_app_table, app_id)).first()
            if app_data != None:
                lst_recommended_games.append(app_data)

        return render_template('recommendation.html', user_id=user_id,
            lst_recommended_games=lst_recommended_games)

    @app.route('/recommendation', methods=('GET', 'POST'))
    def recommendation():
        welcome_message = "Type your Steam ID for some recommendations!"

        myform = GameFeatureForm()

        if myform.is_submitted():
            line = myform.review_text.data
            if len(line) == 0:
                line = 0
            return redirect(url_for('recommendation_user', user_id=line))

        return render_template('recommendation_welcome.html', welcome_message=welcome_message, form=myform)



