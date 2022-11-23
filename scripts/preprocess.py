import os
import datetime
import os
import sys
import json
import pandas as pd
import gzip

#----------

# Tasked with going through each json file of tweets and creating a csv file 
#   of the 'useful' information. Creates one csv per day, finds country as well

#----------

TWEET_ATTRIBUTES = ['id', 'full_text', 'lang', 'created_at'] 
USER_ATTRIBUTES = ['id', 'name', 'location', 'geo_enabled', 'lang']
# other important field -> ['user']['withheld_in_countries']
NUM_TWEETS = 1000 # 1000 tweets were collected per day
NUM_ATTRIBUTES = len(TWEET_ATTRIBUTES) + len(USER_ATTRIBUTES) + 1 # include place with + 1
NUM_ARGS = 4

#----------

'''
Checks validity of args passed to main
Formats folders and passed args before returning them
'''
def verify_args(args):
    # there should be 3 args (py file, src folder, and dest folder)
    if len(args) < 3:
        raise(IndexError('Missing source and destination folders, output file'))
    
    # check if both args are directories
    if not (os.path.isdir(args[1]) and os.path.isdir(args[2])):
        print(f'"{args[1]} or {args[2]} not valid directories', file=sys.stderr)
        raise(FileNotFoundError(f'{args[1]}, {args[2]} can\'t be found'))

    # format args
    src = args[1]
    if src[-1] != '/':
        src += '/'
    dest = args[2]
    if dest[-1] != '/':
        dest += '/'

    # test out opening output_f in case it fails
    output_f = dest[3]
    open(output_f, 'a').close()

    return src, dest, output_f


#----------

def main(args):

    # validate args passed
    src_folder, dest_folder, output = verify_args(args) # raises exception if bad args

    total_tweets = 0
    not_found_tweets = 0

    # print(os.listdir(src_folder))

    # src folder should hold all the jsonl.gz files
    for file in sorted(os.listdir(src_folder)):

        # check file
        if file.split('.')[-1] != 'gz':
            continue

        # open file
        with gzip.open(f'{src_folder}{file}', 'r') as in_f:
            tweets = in_f.read().decode('utf-8').split('\n')

        # create array for tweets
        data = []
        
        for tweet in tweets: # loop through each tweet id
            total_tweets += 1

            # convert tweet to json
            try:
                tweet = json.loads(tweet)
            except json.decoder.JSONDecodeError:
                not_found_tweets += 1
                print(f'Tweet error: {tweet}')
                continue

            # tweet is now a dict with all the values of interest
            if tweet is None or isinstance(tweet, str):
                not_found_tweets += 1
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

        # save data into csv file
        column_names = [col for col in TWEET_ATTRIBUTES] + [f'user_{col}' for col in USER_ATTRIBUTES] + ['place']
        df = pd.DataFrame(data, columns=column_names)



        # save to file
        df.to_csv(f'{dest_folder}{file.split(".")[0]}.csv', index=False)


    # write output information
    output_info = {'to_csv': {'total': total_tweets, 'not_found': not_found_tweets, 'percentage_kept': (total_tweets - not_found_tweets) / max(total_tweets, 1) * 100}}
        
    with open(output, 'w') as out_f:    
        json.dump(output_info, out_f, indent=4)

    return 0
            

if __name__ == '__main__': 
    main(sys.argv)
