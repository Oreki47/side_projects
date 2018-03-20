#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Steam spy api crawler. Using single worker
    since steam spy does not provide api_key
    and therefore we cannot use multiple keys 
    to accelerate the process.
"""

__author__ = 'Oreki47'

import requests, json, os, sys, time, re
import pandas as pd

sys.path.insert(0, os.path.abspath('/home/ethan/Dropbox/Github/side_projects/Game_Recommandation'))
from src.utilities import show_work_status, ConfigData, logger_init, mysql_enginer_init
from datetime import datetime


def extract_from_local(app_info_path, logger, steam_spy_url):
    r = requests.get('http://steamspy.com/api.php?request=all')
    app_data_dict_temp = r.json()

    app_info_dict = {
        'initial_price':{}, 'name':{}, 'score':{}, 'windows':{}, 'mac':{}, 'linux':{},
        'type':{}, 'release_date':{}, 'recommendation':{}, 'header_image':{},
        'steam_appid':{}, 'description':{}, 'negative_reviews':{}, 'positive_reviews':{},
        'owners':{}, 'score_ranks':{},
        }

    with open(app_info_path, 'r') as f:
        lst_raw_string = f.readlines()

    total_count = len(lst_raw_string)
    current_count = 0
    show_work_status(0, total_count, current_count)

    try:
        for raw_string in lst_raw_string:
            
            steam_appid = list(json.loads(raw_string).keys())[0]
            app_data = json.loads(raw_string).get(steam_appid).get('data')
            app_data_sup = app_data_dict_temp.get(steam_appid)

            if app_data is not None:
                detailed_description = app_data.get('detailed_description')
                initial_price = int(app_data.get('price_overview',{}).get('initial', 0)) / 100
                 
                app_name = app_data.get('name')
                app_type = app_data.get('type')
                app_score = app_data.get('metacritic', {}).get('score')

                for (platform, is_supported) in app_data.get('platforms',{}).items():
                    if is_supported == True:
                        app_info_dict[platform].update({steam_appid: 1})

                release_date = app_data.get('release_date', {}).get('date')
                if release_date is not None:
                    try:
                        release_date = datetime.strptime(release_date, '%b %d, %Y')
                    except:
                        try:
                            release_date = datetime.strptime(release_date, '%d %b, %Y')
                        except:
                            pass
                        
                recommendation = app_data.get('recommendations',{}).get('total')
                header_image = app_data.get('header_image')
                app_info_dict['steam_appid'].update({steam_appid: steam_appid})
                app_info_dict['description'].update({steam_appid: detailed_description})           
                app_info_dict['initial_price'].update({steam_appid: initial_price})
                app_info_dict['name'].update({steam_appid: app_name})
                app_info_dict['score'].update({steam_appid: app_score})
                app_info_dict['type'].update({steam_appid: app_type})
                app_info_dict['release_date'].update({steam_appid: release_date})
                app_info_dict['recommendation'].update({steam_appid: recommendation})
                app_info_dict['header_image'].update({steam_appid: header_image})

            if app_data_sup is not None: 
                                
                positive_reviews = app_data_dict_temp.get(steam_appid).get('positive')
                negative_reviews = app_data_dict_temp.get(steam_appid).get('negative')
                score_ranks = app_data_dict_temp.get(steam_appid).get('score_rank')
                owners = app_data_dict_temp.get(steam_appid).get('owners')

                app_info_dict['negative_reviews'].update({steam_appid: negative_reviews})  
                app_info_dict['positive_reviews'].update({steam_appid: positive_reviews}) 
                app_info_dict['score_ranks'].update({steam_appid: score_ranks}) 
                app_info_dict['owners'].update({steam_appid: owners}) 

            show_work_status(1, total_count, current_count)
            current_count += 1

        logger.info("Successfully extracted information from local file")

    except Exception as e:
        logger.error("Extraction failed:", str(e))

    return app_info_dict


def tranfrom_to_df(app_info_dict):
    app_info_df = pd.DataFrame(app_info_dict)
    return app_info_df


def load_into_database(app_info_df, logger, config):
    try:
        engine = mysql_enginer_init(config)
        app_info_df.to_sql(name=config.mysql_app_table, con=engine, if_exists = 'replace', index=False)
        logger.info('Successfully loaded data into database')
    except Exception as e:
        logger.error("Load data into db failed: %s" % str(e))

def main():
    LOG_PATH  = '/home/ethan/Dropbox/Github/side_projects/Game_Recommandation/logs/app_data_etl_log.txt'
    APP_INFO_PATH = '/home/ethan/Dropbox/Github/side_projects/Game_Recommandation/data/app_detail.txt'
    CONFIG_PATH = '/home/ethan/Dropbox/Github/side_projects/Game_Recommandation/config.ini'
    STEAM_SPY_URL = 'http://steamspy.com/api.php?request=all'

    config = ConfigData(CONFIG_PATH)
    logger = logger_init(LOG_PATH)
    logger.info("Start logging.")

    app_info_dict = extract_from_local(APP_INFO_PATH, logger, STEAM_SPY_URL)
    app_info_df = tranfrom_to_df(app_info_dict)
    load_into_database(app_info_df, logger, config)

    logger.info('')  # as a seperater


if __name__ == "__main__":
    main()