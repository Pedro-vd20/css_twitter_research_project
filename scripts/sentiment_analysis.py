import sys
import json
import csv
import os
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pycountry
import ast
import csv

#----------

'''
This script goes through the csv files adding data on sentiment analysis, date 
created, and country created
'''

#----------

NUM_ARGS = 4

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
    output_info = args[4]

    # check if other paths exist
    if not (os.path.isdir(src_folder) and os.path.isfile(cities_path) and \
        os.path.isdir(dest_folder) and os.path.isfile(output_info)):
        
        raise(FileNotFoundError(f"Can't find {src_folder} or {cities_path} " + \
            f"or {dest_folder} or {output_info}"))
    
    # format params
    if src_folder[-1] != '/':
        src_folder += '/'
    if dest_folder[-1] != '/':
        dest_folder += '/'

    return src_folder, dest_folder, cities_path, output_info
   
'''
Cleans text contents of tweets and calculates average sentiment
Checks if tweet in English
'''
def sentiment_analysis(text_list):
    analyzer = SentimentIntensityAnalyzer()

    sentiment = {'neg': [], 'neu': [], 'pos': [], 'compound': []}
    no_sentiment = 0

    for text in text_list:
        # None cases
        if text is None:
            no_sentiment += 1
            for key in sentiment:
                sentiment[key].append(None)
            continue

        # clean text (remove links, @, #)
        #text = re.sub('@ | # | http[*]$', '', text)
        text = re.sub(r"#", r"", text)
        text = re.sub(r"@", r"", text)
        text = re.sub(r"http(s).*$", r"", text)
        text = re.sub(r"[^\x00-\x7F]+", r"", text)
        text = re.sub(r"\t", r" ", text)
        text = re.sub(r"\n", r". ", text)

        # run sentiment analysis
        v_sentiment = analyzer.polarity_scores(text)
        for key in v_sentiment:
            sentiment[key].append(v_sentiment[key])
        

    return sentiment, no_sentiment

'''
Attempts to gather country data based on tweet geoloc or user location
'''
def fetch_country(places, user_locs, city_path):
    # load city info
    with open(city_path, 'r') as in_f:
        cities = json.load(in_f)

    countries = []
    no_country_count = 0

    for place, u_loc in zip(places, user_locs):
        # collect based on place
        if place is not np.nan:
            # print(place)
            country = pycountry.countries.search_fuzzy(place)[0]
            countries.append(country.name)
        elif u_loc is not np.nan:
            # split into words, clean for non-alphabet chars
            sentence = re.sub("[^a-zA-Z ]+", "", u_loc)

            # search each for country name
            found = False
            try:
                country = pycountry.countries.search_fuzzy(sentence)[0]
                countries.append(country.name)
                found = True
            except LookupError:
                found = False
            
            # search by city
            if not found and cities.get(sentence, None) is not None and type(cities[sentence]) is str:
                try:
                    country = pycountry.countries.search_fuzzy(cities[sentence])[0]
                    countries.append(country.name)
                    found = True
                except LookupError:
                    found = False

            # not found -> append none
            if not found:
                countries.append(None)
                no_country_count += 1

        # both data points are None
        else:
            countries.append(None)
            no_country_count += 1

    return countries, no_country_count

#----------

def main(args):
    # check args
    data_folder, dest_folder, cities_path, output = check_args(args)

    stats = {'total': 0, 'no_country': 0, 'no_sentiment': 0}

    # loop through each file
    for csv_file in sorted(os.listdir(data_folder)):
        # get file data
        try:
            data = pd.read_csv(f'{data_folder}{csv_file}')
        except pd.errors.ParserError as e:
            print(f"Could not read {csv_file}")
            # if crashes, use csv to read file
            try:
                with open(f'{data_folder}{csv_file}', 'r') as in_f:
                    parser = csv.reader(in_f)
                    data = list(parser)
            # if NUL byte
            except csv.Error:
                with open(f'{data_folder}{csv_file}', 'r') as in_f:
                    parser = csv.reader(x.replace('\0', '') for x in in_f)
                    data = list(parser)
            
            cols = data[0]
            data_vals = data[1:]
            data = pd.DataFrame(data_vals, columns=cols)

            
            # raise(e)
        
        # compute totals
        stats['total'] += len(data)

        # calculate sentiment analysis
        sentiment_dict, sent_count = sentiment_analysis(data['full_text'])
        stats['no_sentiment'] += sent_count

        for key in sentiment_dict:
            data[key] = sentiment_dict[key]
        
        # Attempt to fetch country
        data['country'], no_count = fetch_country(data['place'], data['user_location'], cities_path)
        stats['no_country'] += no_count

        # save file
        data.to_csv(f'{dest_folder}processed_{f_in.split("_")[-1]}', index=False)

        break
    exit(0)
    print('Sentiment Analysis done!')

    # save stats
    with open(output, 'r') as in_f:
        out_stats = json.load(in_f)
    out_stats['sentiment'] = stats
    with open(output, 'w') as out_f:
        json.dump(out_stats, out_f, indent=4)


    return 0




if __name__ == '__main__':
    main(sys.argv)

