#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'steam web api crawler main. Pretty ugly.'

__author__ = 'Oreki47'

import os, sys, requests, time, json, logging

sys.path.insert(0, os.path.abspath('/home/ethan/Dropbox/Github/side_projects/Game_Recommandation'))
from src.utilities import ConfigData, split_list, logger_init, show_work_status
from multiprocessing import Pool


def user_game_worker(lst_user_id_temp, api_key):
    '''
        From user id gets user owned games
    '''
    dic_temp = {}
    for user_id in lst_user_id_temp:
        base_url = 'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/'
        params = {
            'key' : api_key,
            'steamid' : user_id.strip(),
            'format' : 'json' }
        r = requests.get(base_url, params = params)
        user_inventory = r.json().get('response').get('games')
        dic_temp.update({user_id.strip().decode("utf-8"): user_inventory})
        time.sleep(1.0)
    return dic_temp


def main():
    '''
        Intended to retrieve all 5000 users from steam_user_id.txt.
        With SPLITS = 50 and NUM_USERS = 5000.
        For the purpose of streaming and testing,
        Set SPLITS = 10 and NUM_USERS = 20.
    '''

    logger = logger_init("/home/ethan/Dropbox/Github/side_projects/Game_Recommandation/logs/steam_crawl_log.txt")
    logger.info("Start logging.")

    SPLITS = 10
    N_THREADS = 2
    NUM_USERS = 20
    p = Pool(N_THREADS)
    config = ConfigData('/home/ethan/Dropbox/Github/side_projects/Game_Recommandation/config.ini')

    with open('/home/ethan/Dropbox/Github/side_projects/Game_Recommandation/data/steam_user_id.txt', 'rb') as f:
        lst_user_id = f.readlines()[:NUM_USERS]
    
    current_count = 0
    total_count = len(lst_user_id)
    show_work_status(0, total_count, current_count)

    logger.info("Retrieving %i users with n_thread=%i" % (NUM_USERS, N_THREADS))

    try:
        dict_master = {}
        for i in split_list(lst_user_id, total_count // SPLITS):

            args = zip(split_list(i, len(i) // N_THREADS), [config.steam_api_key1, config.steam_api_key2])
            lst_temp_dict = p.starmap(user_game_worker, args)

            for j in lst_temp_dict:
                dict_master.update(j)

            show_work_status(len(i), total_count, current_count)
            current_count += len(i)
            time.sleep(1)

        with open('/home/ethan/Dropbox/Github/side_projects/Game_Recommandation/data/results_user_inventory_test.txt', 'wb') as f:
            for user_id, user_inventory in dict_master.items():
                f.write(json.dumps({user_id:user_inventory}).encode("utf-8"))
                f.write(b'\n')

        assert(len(dict_master) == NUM_USERS)
        logger.info('Successfully retrieved all information.')
    except:
        logger.error('%i users retrieved. Something is wrong. Please check!' %len(dict_master))

    logger.info('')


if __name__ == '__main__':
    main()
