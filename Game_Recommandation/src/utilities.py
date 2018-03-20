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

        self.steam_api_key1 = config.get('Steam', 'steam_api_key1')
        self.steam_api_key2 = config.get('Steam', 'steam_api_key2')

        self.mail_route_to = config.get('Emails', 'route_to')
        self.mail_sender = config.get('Emails', 'sender')
        self.mail_crawler_failure_subject = config.get('Emails', 'crawler_failuer_subject')
        self.mail_steam_spy_failure_subject = config.get('Emails', 'steam_spy_failuer_subject')
        self.mail_appdata_failure_subject = config.get('Emails', 'appdata_failuer_subject')
        self.test_string = config.get('Others', 'test_string', fallback='Nothing retrieved!')
        
        self.mysql_username = config.get('MySQL', 'username')
        self.mysql_password = config.get('MySQL', 'password')
        self.mysql_database = config.get('MySQL', 'database')
        self.mysql_app_table = config.get('MySQL', 'app_table')
        self.mysql_user_like_table = config.get('MySQL', 'user_like_table')
        self.mysql_popularity_table = config.get('MySQL', 'result_popularity_based_table')
        self.mysql_content_table = config.get('MySQL', 'result_content_based_table')
        self.mysql_item_table = config.get('MySQL', 'result_item_based_table')
        self.mysql_als_table = config.get('MySQL', 'result_als_table')
        self.mysql_port = config.get('MySQL', 'port')



def show_work_status(single_count, total_count, current_count=0):
    current_count += single_count
    percentage = 1. * current_count / total_count * 100
    status =  '>' * int(percentage)  + ' ' * (100 - int(percentage))
    sys.stdout.write('\rStatus: [{0}] {1:.2f}% '.format(status, percentage))
    sys.stdout.flush()
    if percentage >= 100:
        print('\n')


def split_list(lst_long, n):
    lst_splitted = []
    if len(lst_long) % n == 0:
        totalBatches = len(lst_long) // n
    else:
        totalBatches = len(lst_long) // n + 1
    for i in range(totalBatches):
        lst_short = lst_long[i*n:(i+1)*n]
        lst_splitted.append(lst_short)
    return lst_splitted


def logger_init(filename):
    formatter = logging.Formatter('%(asctime)s | %(name)s | %(levelname)s | %(message)s')
        
    handler = logging.FileHandler(filename)
    handler.setLevel(logging.INFO)
    handler.setFormatter(formatter)  

    logger = logging.getLogger(sys.argv[0])
    logger.setLevel(level = logging.INFO)
    logger.addHandler(handler)

    return logger

def mysql_enginer_init(config):
    engine_url = 'mysql+mysqldb://%s:%s@127.0.0.1:%s/%s?charset=utf8mb4' \
        % (config.mysql_username, config.mysql_password, config.mysql_port, config.mysql_database)
    engine = create_engine(engine_url, echo=False)
    return engine