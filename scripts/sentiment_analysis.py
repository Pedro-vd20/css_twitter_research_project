from textblob import TextBlob
import nltk
import sys
import os
import json
import pandas as pd
import numpy as np
import re
import pycountry

#----------

'''
This script goes through the csv files adding data on sentiment analysis, date 
created, and country created
'''

#----------

NUM_ARGS = 3

#----------

'''
Goes through all arguments passed to file
Checks validity and formats args
'''
def check_args(args):
    # check num args
    if len(args) < NUM_ARGS + 1:
        print('Insufficient arguments, expected path to csv, path to cities JSON')
        raise(IndexError('Need 2 args: path to csv files, path to cities json'))

    # extract args
    src_folder = args[1]
    dest_folder = args[2]
    cities_path = args[3]

    # check if other paths exist
    if not (os.path.isdir(src_folder) and os.path.isfile(cities_path) and os.path.isdir(dest_folder)):
        print(f"Can't find {src_folder} or {cities_path}")
        raise(FileNotFoundError(f"Can't find {src_folder} or {cities_path}"))
    
    # format params
    if src_folder[-1] != '/':
        src_folder += '/'
    if dest_folder[-1] != '/':
        dest_folder += '/'

    return src_folder, dest_folder, cities_path
   
'''
Cleans text contents of tweets and calculates average sentiment
Checks if tweet in English
'''
def sentiment_analysis(text_list, language_list):
    sentiment = []
    for text, lang in zip(text_list, language_list):
        # None cases
        if text is None or lang != 'en':
            sentiment.append(None)
            continue

        # clean text (remove links, @, #)
        #text = re.sub('@ | # | http[*]$', '', text)
        text = re.sub(r"#", r"", text)
        text = re.sub(r"@", r"", text)
        text = re.sub(r"http(s).*$", r"", text)
        text = re.sub(r"[^\x00-\x7F]+", r"", text)
        text = re.sub(r"\t", r"", text)
        text = re.sub(r"\n", r" ", text)

        # run sentiment analysis
        blob = TextBlob(text)
        temp = []
        for sentence in blob.sentences:
            temp.append(sentence.sentiment.polarity)

        # compute average
        sentiment_sum = 0
        count = 0
        for s in temp:
            if s != 0:
                sentiment_sum += s
                count += 1
        sentiment.append(0 if count == 0 else sentiment_sum / count)

    return sentiment

'''
Attempts to gather country data based on tweet geoloc or user location
'''
def fetch_country(places, user_locs, city_path):
    # load city info
    with open(city_path, 'r') as in_f:
        cities = json.load(in_f)

    countries = []

    for place, u_loc in zip(places, user_locs):
        # collect based on place
        if place is not np.nan:
            place = place.replace("'", '"') # replace ' with " for json
            place = json.loads(place)
            countries.append(place['country'])
        elif u_loc is not np.nan:
            # split into words, clean for non-alphabet chars
            sentence = re.sub("[^a-zA-Z ]+", "", u_loc).split(' ')

            # search each for country name
            found = False
            for word in sentence:
                try:
                    country = pycountry.countries.search_fuzzy(word)[0]
                    countries.append(country.name)
                    found = True
                    break
                except LookupError:
                    continue
            
            # search by city
            if not found:
                for word in sentence:
                    '''
                    Must check if cities[word] is a string. For cities that map 
                    to many countries (ie London, Canada and London, UK), city
                    alone can't determine the country so None is put
                    '''
                    if (cities.get(word, None) is not None) and (type(cities[word]) is str):
                        countries.append(cities[word])
                        found = True
                        break

            # not found -> append none
            if not found:
                countries.append(None)

        # both data points are None
        else:
            countries.append(None)

    return countries

#----------

def main(args):
    # check args
    data_folder, dest_folder, cities_path = check_args(args)

    # set up nltk
    nltk.download('punkt')

    # loop through folders
    for sub_folder in sorted(os.listdir(data_folder)):
        '''
        Expected file struct
            data_folder/
            |   sub_folder/
            |   |   data1.csv
            |   |   data2.csv
            |   |   ...
            |   sub_folder2/
            |   ...
        '''
        # loop through each file
        for f_in in sorted(os.listdir(f'{data_folder}{sub_folder}')):
            # get file data
            data = pd.read_csv(f'{data_folder}{sub_folder}/{f_in}')
            
            # add created_at
            date = f_in.split('.')[0].split('_')[-1]
            data['date'] = [None if val is None else date for val in data['text']]

            # calculate sentiment analysis
            data['sentiment'] = sentiment_analysis(data['text'], data['lang'])

            # Attempt to fetch country
            data['country'] = fetch_country(data['place'], data['user_location'], cities_path)

            # get dest path to save csv
            dest_path = f'{dest_folder}{sub_folder}/'
            if not os.path.isdir(dest_path):
                os.mkdir(dest_path)

            # save file
            data.to_csv(f'{dest_path}processed_{f_in.split("_")[-1]}', index=False)

    return 0




if __name__ == '__main__':
    main(sys.argv)

