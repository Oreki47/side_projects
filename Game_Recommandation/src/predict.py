#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Prediction file (local version),
    based on surprise.
"""

__author__ = 'Oreki47'

import requests, json, os, sys, time, re
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.abspath('/home/ethan/Dropbox/Github/side_projects/Game_Recommandation'))
from src.utilities import show_work_status, ConfigData, logger_init, mysql_enginer_init
from sklearn.metrics.pairwise import linear_kernel, cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MinMaxScaler
from sqlalchemy import create_engine
from datetime import datetime

from surprise import NMF
from surprise import NormalPredictor
from surprise import Dataset
from surprise import Reader


def extract_like_game(uesr_info_path):
    return None


def find_most_played(path, logger, config, engine):
    with open(path, 'r') as f:
        raw_strings = f.readlines()

    dic_user_favorite_app = {}
    
    try:          
        for raw_string in raw_strings:
            user_id, lst_inventory = list(json.loads(raw_string).items())[0]
            if lst_inventory != None and lst_inventory != []:
                most_played_app_id = sorted(lst_inventory, key=lambda k: k['playtime_forever'])[-1].get('appid')
                dic_user_favorite_app.update({user_id:most_played_app_id})
            else:
                pass
        # df_user_favorite_app = pd.Series(dic_user_favorite_app).to_frame().reset_index()
        # df_user_favorite_app.columns = ['steam_user_id','favorite_game']
        # df_user_favorite_app.to_sql(config.mysql_user_like_table, engine, if_exists='replace', index=False)
        # logger.info('Successfully inserted into table %s' % config.mysql_user_like_table)
    except Exception as e:
        logger.error("Load data into db failed: %s" % str(e))


def popularity_based_model(config, engine, df_valid_games):
    df_popularity_based_results = df_valid_games[['steam_appid', 'owners']]
    df_popularity_based_results.sort_values(ascending=False, by='owners', inplace=True)
    df_popularity_based_results.to_sql(config.mysql_popularity_table, engine, if_exists='replace')


def content_based_model(config, engine, df_valid_games):

    tfidf = TfidfVectorizer(strip_accents='unicode',stop_words='english').fit_transform(df_valid_games.description)
    lst_app_id = list(df_valid_games.steam_appid)
    dic_recomended = {}
    total_count = len(lst_app_id)
    current_count = 0
    for index in range(tfidf.shape[0]):
        cosine_similarities = linear_kernel(tfidf[index:index+1], tfidf).flatten()
        related_docs_indices = cosine_similarities.argsort()[-2:-22:-1]
        dic_recomended.update({lst_app_id[index]:[lst_app_id[i] for i in related_docs_indices]})
        show_work_status(1,total_count,current_count)
        current_count+=1

    df_content_based_results = pd.DataFrame(dic_recomended).T
    df_content_based_results.index.name = 'steam_appid'
    df_content_based_results.reset_index(inplace=True)
    df_content_based_results.to_sql(config.mysql_content_table, engine, if_exists='replace')


def colaborative_filtering_based_model(path, config, engine, df_valid_games):
    with open(path, 'r') as f:
        raw_strings = f.readlines()

    total_count = len(raw_strings)
    current_count = 0

    user_ratings = []
    scaler = MinMaxScaler((1, 5))

    for raw_string in raw_strings:
        user_id, user_inventory = list(json.loads(raw_string).items())[0]
        if user_inventory is not None:
            app_ids = [item['appid'] for item in user_inventory]
            app_scores = [item['playtime_forever'] for item in user_inventory]
            app_scores = scaler.fit_transform(np.log1p(app_scores).reshape(-1, 1))
            
            user_ratings_temp = [[user_id, app_ids[i], app_scores[i].item()] for i in range(len(app_ids))]
            user_ratings += user_ratings_temp

        show_work_status(1,total_count,current_count)
        current_count+=1

    user_item_ratings = pd.DataFrame(user_ratings)
    user_item_ratings.columns = ['user_id', 'item_id', 'rating']

    # Prediction part
    game_ids_set = set(df_valid_games.steam_appid)
    grouped_user_item_ratings = user_item_ratings.groupby('user_id')
    reader = Reader(rating_scale=(1, 5))
    data = Dataset.load_from_df(user_item_ratings[['user_id', 'item_id', 'rating']], reader)

    alg = NMF(n_factors=20)
    alg.fit(data.build_full_trainset())

    total_count = len(user_item_ratings.user_id.unique())
    current_count = 0
    dict_user_recommendations = {}
    for user in user_item_ratings.user_id.unique().tolist():
        temp = grouped_user_item_ratings.get_group(user)
        not_purchased_ids = game_ids_set - set([str(x) for x in temp.item_id])
        
        user_test_temp = [[user, not_purchased_id, 0] for not_purchased_id in not_purchased_ids]
        user_test_temp = pd.DataFrame(user_test_temp)
        user_test_temp.columns = ['user_id', 'item_id', 'rating']
        
        data = Dataset.load_from_df(user_test_temp[['user_id', 'item_id', 'rating']], reader)
        user_test = data.build_full_trainset().build_testset()
        results = alg.test(user_test)
        dict_user_recommendations.update({user: pd.DataFrame(results).sort_values('est', ascending=False).iloc[:10, 1].values.tolist()})
        
        show_work_status(1,total_count,current_count)
        current_count+=1   

    df_cf_based_results = pd.DataFrame(dict_user_recommendations).T
    df_cf_based_results.index.name = 'user_id'
    df_cf_based_results.reset_index(inplace=True)
    df_cf_based_results.to_sql(config.mysql_user_like_table, engine, if_exists='replace')


def item_based_model(path, config, engine):
    with open(path, 'r') as f:
        raw_strings = f.readlines()

    dict_purchase = {}

    total_count = len(raw_strings)
    current_count = 0
    for raw_string in raw_strings:
        user_id, user_inventory = list(json.loads(raw_string).items())[0]
        if user_inventory != [] and user_inventory != None and user_inventory != {}:
            dict_purchase[user_id] = {}
            for playtime_info in user_inventory:
                appid = playtime_info.get('appid')
                dict_purchase[user_id].update({appid:1})
        show_work_status(1,total_count,current_count)
        current_count+=1

    df_purchase = pd.DataFrame(dict_purchase).fillna(0)
    purchase_matrix = df_purchase.values
    lst_app_id = df_purchase.index

    total_count = purchase_matrix.shape[0]
    current_count = 0

    dic_recomended_item_based = {}
    for index in range(total_count):
        cosine_similarities = linear_kernel(purchase_matrix[index:index+1], purchase_matrix).flatten()
        lst_related_app = np.argsort(-cosine_similarities)[1:21]
        dic_recomended_item_based.update({lst_app_id[index]:[lst_app_id[i] for i in lst_related_app]})
        show_work_status(1,total_count,current_count)
        current_count+=1

    df_item_based_result = pd.DataFrame(dic_recomended_item_based).T
    df_item_based_result.index.name = 'steam_appid'
    df_item_based_result.reset_index(inplace=True)
    df_item_based_result.to_sql(config.mysql_item_table, engine, if_exists='replace')


def main():
    LOG_PATH  = '/home/ethan/Dropbox/Github/side_projects/Game_Recommandation/logs/prediction_log.txt'
    CONFIG_PATH = '/home/ethan/Dropbox/Github/side_projects/Game_Recommandation/config.ini'
    USER_INFO_PATH = '/home/ethan/Dropbox/Github/side_projects/Game_Recommandation/data/results_user_inventory.txt'

    config = ConfigData(CONFIG_PATH)
    engine = mysql_enginer_init(config)
    logger = logger_init(LOG_PATH)
    logger.info("Start logging.")

    df_steam_app = pd.read_sql(config.mysql_app_table, engine)
    df_valid_games = df_steam_app.query('type == "game" and release_date <= "{}" \
         and initial_price >= 0'.format(datetime.today().date().isoformat()))

    # find_most_played(USER_INFO_PATH, logger, config, engine)
    # popularity_based_model(config, engine, df_valid_games)
    # content_based_model(config, engine, df_valid_games)
    # item_based_model(USER_INFO_PATH, config, engine)
    # colaborative_filtering_based_model(USER_INFO_PATH, config, engine, df_valid_games)

if __name__ == "__main__":
    main()