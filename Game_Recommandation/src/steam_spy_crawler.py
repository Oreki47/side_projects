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
from datetime import datetime
from multiprocessing import Pool

sys.path.insert(0, os.path.abspath('/home/ethan/Dropbox/Github/side_projects/Game_Recommandation'))
from src.utilities import show_work_status, logger_init
from datetime import datetime

def main():
    # parameter definition
    LOG_PATH  = '/home/ethan/Dropbox/Github/side_projects/Game_Recommandation/logs/steam_spy_crawler_log.txt'
    APP_INFO_PATH = '/home/ethan/Dropbox/Github/side_projects/Game_Recommandation/data/app_detail_test.txt'

    logger = logger_init(LOG_PATH)
    logger.info("Start logging.")

    r = requests.get('http://steamspy.com/api.php?request=all')
    dict_app_data = r.json()
    lst_app_id = list(dict_app_data.keys())

    total_count = len(lst_app_id) # when crawling the entire set
    current_count = 0
    show_work_status(0, total_count, current_count)

    try:
        with open(APP_INFO_PATH, 'wb') as f:
            for app_id in lst_app_id[:total_count]:
                url_app_detail = ('http://store.steampowered.com/api/appdetails?appids=%s') % (app_id)
                for _ in range(3):
                    try:
                        r = requests.get(url_app_detail)
                        result = r.json()
                        f.write(json.dumps(result).encode("utf-8"))
                        f.write(b'\n')                   
                        break
                    except:
                        time.sleep(5)
                        pass

                show_work_status(1, total_count, current_count)
                current_count += 1
                if current_count % 200 == 0:
                    time.sleep(300)
                else:
                    time.sleep(.5)
        logger.info('Successfully retrieved information from steam spy.')

    except Exception as e:
         logger.error("Load data into db failed: %s" % str(e))
    
    logger.info("")
        
if __name__ == "__main__":
    main()