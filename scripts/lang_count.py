import pandas as pd
import numpy as np
import os
import sys
import json

def main():
    
    data_path = '/scratch/pv850/css/css_twitter_research_project/sentiment_analysis/'
    output_f = '/scratch/pv850/css/css_twitter_research_project/Dataset_info/Data_info.json'

    print('Starting...')

    unique_users = set()
    en_counter = 0
    tr_counter = 0
    es_counter = 0
    ru_counter = 0
    uk_counter = 0
    no_of_tweets_per_user = {}
    total_tweets = 0


    # loop through all files
    for csv_file in sorted(os.listdir(data_path)):
        data = pd.read_csv(f'{data_path}{csv_file}', dtype=str)
        #collect total number of tweets
        total_tweets += len(data)
        # collect all unique users
        unique_users.update(data['user_id'].unique())

        # collect all tweets in English
        en_counter += len(data[data['lang'] == 'en'])

        # collect all tweets in Turkish
        tr_counter += len(data[data['lang'] == 'tr'])

        # collect all tweets in Spanish
        es_counter += len(data[data['lang'] == 'es'])

        # collect all tweets in Russian
        ru_counter += len(data[data['lang'] == 'ru'])

        # collect all tweets in Ukrainian
        uk_counter += len(data[data['lang'] == 'uk'])

        # collect all tweets per user (top 10)
        for user_name, user_tweets in data.groupby('user_name'):
            no_of_tweets_per_user[user_name] = len(user_tweets)

    # sort the tweets per user
    no_of_tweets_per_user = sorted(no_of_tweets_per_user.items(), key=lambda x: x[1], reverse=True)

    # create the output dictionary
    output = {
        'Total number of tweets': total_tweets,
        'Number of unique users': len(unique_users),
        'Number of tweets in English': en_counter,
        'Number of tweets in Turkish': tr_counter,
        'Number of tweets in Spanish': es_counter,
        'Number of tweets in Russian': ru_counter,
        'Number of tweets in Ukrainian': uk_counter,
        'Number of tweets per top 10 users': no_of_tweets_per_user[:10]
    }

    with open(output_f, 'w') as f:
        json.dump(output, f)

    print('Done!')
        
if __name__ == '__main__':
    main()
