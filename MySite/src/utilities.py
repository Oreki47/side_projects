import os, sys, time, re
import requests, json, logging
import configparser

from datetime import datetime
from multiprocessing import Pool
from sqlalchemy import create_engine

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


def mysql_enginer_init(database, config):
    engine_url = 'mysql+mysqldb://%s:%s@127.0.0.1:%s/%s?charset=utf8mb4' \
        % (config.mysql_username, config.mysql_password, config.mysql_port, database)
    engine = create_engine(engine_url, echo=False)
    return engine