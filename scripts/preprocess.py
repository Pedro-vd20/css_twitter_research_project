import os
from os.path import isdir
import sys
import json
import pandas as pd

#----------

# Tasked with going through each json file of tweets and creating a csv file 
#   of the 'useful' information. Creates one csv per day, finds country as well

#----------

TWEET_ATTRIBUTES = ['id', 'created_at', 'text', 'truncated', 'source', 'in_reply_to_status_id', 'in_reply_to_user_id', 'in_reply_to_screen_name', 'geo', 'coordinates', 'place', 'contributors', 'is_quote_status', 'retweet_count', 'favorite_count', 'favorited', 'retweeted', 'possibly_sensitive', 'possibly_sensitive_appealable', 'lang'] 
USER_ATTRIBUTES = ['id', 'name', 'screen_name', 'location', 'description', 'protected', 'followers_count', 'friends_count', 'listed_count', 'created_at', 'favourites_count', 'utc_offset', 'time_zone', 'geo_enabled', 'verified', 'statuses_count', 'lang', 'contributors_enabled', 'is_translator', 'is_translation_enabled', 'default_profile', 'following', 'follow_request_sent', 'translator_type']
# other important field -> ['user']['withheld_in_countries']
NUM_TWEETS = 1000 # 1000 tweets were collected per day
NUM_ATTRIBUTES = len(TWEET_ATTRIBUTES) + len(USER_ATTRIBUTES)

#----------

'''
Checks validity of args passed to main
Formats folders and passed args before returning them
'''
def verify_args(args):
    # there should be 3 args (py file, src folder, and dest folder)
    if len(args) < 3:
        print('Missing arguments: need source folder and dest folder', file=sys.stderr)
        raise(IndexError('Missing source and destination folders'))
    
    # check if both args are directories
    if not (isdir(args[1]) and isdir(args[2])):
        print(f'"{args[1]} or {args[2]} not valid directories', file=sys.stderr)
        raise(FileNotFoundError(f'{args[1]}, {args[2]} can\'t be found'))

    # format args
    src = args[1]
    if src[-1] != '/':
        src += '/'
    dest = args[2]
    if dest[-1] != '/':
        dest += '/'
    
    return src, dest


#----------

def main(args):

    # validate args passed
    src_folder, dest_folder = verify_args(args) # raises exception if bad args

    # src folder should point to a folder of folders -> each subfolder contains
    #   all the tweet json files
    # dest folder should be empty

    for sub_f in sorted(os.listdir(src_folder)):
        print(sub_f)

        # loop through each file
        for f_in in sorted(os.listdir(f'{src_folder}{sub_f}')):

            # load json object
            with open(f'{src_folder}{sub_f}/{f_in}', 'r') as f:
                tweets = json.load(f)

            # create numpy array to store data
            data = []
            
            for id, tweet in tweets.items(): # loop through each tweet id
                # tweet is now a dict with all the values of interest
                if tweet is None or type(tweet) == str:
                    # append empty row
                    data.append([id] + ([None] *  (NUM_ATTRIBUTES)))
                    continue
                
                # collect all the data in the order of the attributes
                temp = []
                for attribute in TWEET_ATTRIBUTES:
                    temp.append(tweet.get(attribute, None))
                for attribute in USER_ATTRIBUTES:
                    temp.append(tweet['user'].get(attribute, None))
                temp.append(str(tweet['user'].get('withheld_in_countries', None)))


                # add to data
                data.append(temp)

            # check if dest folder exists
            if not os.path.isdir(f'{dest_folder}{sub_f}'):
                os.mkdir(f'{dest_folder}{sub_f}')

            # save data into csv file
            column_names = [col for col in TWEET_ATTRIBUTES] + [f'user_{col}' for col in USER_ATTRIBUTES] + ['user_withheld_in_countries']
            df = pd.DataFrame(data, columns=column_names)

            # save to file
            df.to_csv(f'{dest_folder}{sub_f}/{f_in.split(".")[0]}.csv', index=False)
            

if __name__ == '__main__': 
    main(sys.argv)
