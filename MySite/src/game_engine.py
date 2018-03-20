#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    game part
"""

__author__ = 'Oreki47'
from flask import Flask, render_template

def run_game_engine(app, engine, config):

    @app.route('/recommendation/<string:user_id>')
    def recommendation_user(user_id):
        result = engine.execute('''
            SELECT g1, g2, g3, g4, g5, g6, g7, g8, g9, g10 FROM %s WHERE user_id=%s;
            ''' % (config.mysql_game_user_like_table, user_id)).first()

        lst_recommended_games = []
        for app_id in list(result):
            app_data = engine.execute('''
                            SELECT name, initial_price, header_image FROM %s WHERE steam_appid = %s;
                        ''' % (config.mysql_game_app_table, app_id)).first()
            if app_data != None:
                lst_recommended_games.append(app_data)

        return render_template('recommendation.html', user_id=user_id, lst_recommended_games=lst_recommended_games)

    @app.route('/recommendation')
    def recommendation():
        welcome_message = "\n\nAppend /<userid> to the current url\n\nSome availble userids: 76561198249026172, 76561198082481473, 76561198040992485, 76561197960464402"
        return render_template('index.html', welcome_message=welcome_message)


