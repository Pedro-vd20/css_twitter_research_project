import os
import datetime
from os.path import isdir
import sys
import json
import pandas as pd

#----------

# Tasked with going through each json file of tweets and creating a csv file 
#   of the 'useful' information. Creates one csv per day, finds country as well

#----------

TWEET_ATTRIBUTES = ['id', 'text', 'lang'] 
USER_ATTRIBUTES = ['id', 'name', 'location', 'geo_enabled', 'lang']
# other important field -> ['user']['withheld_in_countries']
NUM_TWEETS = 1000 # 1000 tweets were collected per day
NUM_ATTRIBUTES = len(TWEET_ATTRIBUTES) + len(USER_ATTRIBUTES) + 1 # include place with + 1

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
                if tweet is None or isinstance(tweet, str):
                    # append empty row
                    data.append([id] + ([None] *  (NUM_ATTRIBUTES-1)))
                    continue
                
                # collect all the data in the order of the attributes
                temp = []
                for attribute in TWEET_ATTRIBUTES:
                    temp.append(tweet.get(attribute, None))
                
                for attribute in USER_ATTRIBUTES:
                    temp.append(tweet['user'].get(attribute, None))

                if tweet.get('place', None) is not None:
                    temp.append(tweet['place'].get('country', None))
                else:
                    temp.append(None)

                # add to data
                data.append(temp)

            # check if dest folder exists
            if not os.path.isdir(f'{dest_folder}{sub_f}'):
                os.mkdir(f'{dest_folder}{sub_f}')

            # save data into csv file
            column_names = [col for col in TWEET_ATTRIBUTES] + [f'user_{col}' for col in USER_ATTRIBUTES] + ['place']
            df = pd.DataFrame(data, columns=column_names)

            # add created_at date
            date_str = f_in.split('.')[0].split('_')[-1].split('-')
            date = datetime.date(int(date_str[0]), int(date_str[1]), int(date_str[2]))
            df['date'] = [date] * len(df['text'])


            # save to file
            df.to_csv(f'{dest_folder}{sub_f}/{f_in.split(".")[0]}.csv', index=False)

    return 0
            

if __name__ == '__main__': 
    main(sys.argv)
