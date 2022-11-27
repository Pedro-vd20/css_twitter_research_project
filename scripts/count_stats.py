import pandas as pd
import numpy as np
import os
import sys
import json

#----------

'''
Count country-related stats
'''

#----------

NUM_ARGS = 2

#----------

'''
Goes through all arguments passed to file
Checks validity and formats args
'''
def check_args(args):
    # check num args
    if len(args) < NUM_ARGS + 1:
        raise(IndexError(f'Need {NUM_ARGS} args: path to csv files'))

    # extract args
    src_folder = args[1]
    dest_f = args[2]

    # check if other paths exist
    if not (os.path.isdir(src_folder) and os.path.isfile(dest_f)):
        
        raise(FileNotFoundError(f"Can't find {src_folder} or {dest_f}"))
    
    # format params
    if src_folder[-1] != '/':
        src_folder += '/'

    return src_folder, dest_f


#----------

def main():
    print('here')
    # check passed args
    data_path, output_f = check_args(sys.argv)

    # initialize all data_structures to hold counters
    unique_countries = set()
    data_per_country = {} # store tuple of (tweets, users)
    no_sentiment = 0
    no_country = 0
    no_country_no_sentiment = 0

    # loop through all files
    for csv_file in sorted(os.listdir(data_path)):
        data = pd.read_csv(f'{data_path}{csv_file}')

        # collect all countries
        countries = data['country'].dropna().unique()
        unique_countries.update(countries)

        # count tweets per country
        tweet_counts = data.groupby('country').count()['id']

        for country in countries:
            if data_per_country.get(country, None) is None:
                data_per_country[country] = [0, 0]
            
            # tweet counts
            data_per_country[country][0] += int(tweet_counts.at[country])

            # unique users
            data_per_country[country][1] += len(data[data['country'] == country]['user_id'].unique())

        # count no_sentiment and no_country
        no_sentiment += len(data[data['neu'].isna()])

        temp = data[data['country'].isna()]
        no_country += len(temp)
        no_country_no_sentiment += len(temp[temp['neu'].isna()])

    # format output
    out_data = {
        'countries': len(unique_countries),
        'data_per_country': data_per_country,
        'no_sentiment': no_sentiment,
        'no_country': no_country,
        'intersection': no_country_no_sentiment
    }

    # write output 
    with open(output_f, 'w') as out_f:
        json.dump(out_data, out_f)

    return 0
    

if __name__ == '__main__':
    main()
