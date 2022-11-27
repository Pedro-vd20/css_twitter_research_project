import tweepy
import sys
import os
import json
import time

# here you must define the following variables (spelling-sensitvie):
#   api_key
#   api_secrets
#   access_token
#   access_secret
from secret import *

##########

TWEET_DATA = {}
COUNT = 1000

##########


# authenticate api on twitter
# uses variables declared in secret
# returns tweepy api
# crashes if fails to authenticate
def authenticate():
    # Authenticate to Twitter
    auth = tweepy.OAuthHandler(api_key,api_secrets)
    auth.set_access_token(access_token,access_secret)

    api = tweepy.API(auth)

    try:
        api.verify_credentials()
        print('Successful Authentication')
    except:
        print('Failed Authentication')
        raise
 
    return api


def check_args(args):
    if len(args) < 3:
        raise(IndexError('Missing arguments, need source and destination folders'))
    # collect folder (month) of twitter data
    try:
        folder = args[1]
        # format input
        if folder[-1] != '/':
            folder += '/'

        dest = args[2]
        if dest[-1] != '/':
            dest += '/'

        # check if exists
        if not os.path.isdir(folder) or not os.path.isdir(dest):
            raise(FileNotFoundError(f"Either '{folder}' or '{dest}' not directories"))

    except FileNotFoundError:
        print(f'{folder}  or {dest} directory could not be found')
        raise

    return folder, dest

def main(args):
    folder, dest = check_args(args)

    # auth twitter api
    global TWEET_DATA
    api = authenticate()

    # open each file
    for f_name in sorted(os.listdir(folder)):
        # open file
        with open(f'{folder}{f_name}', 'r') as in_f:
            # collect 1000 IDs
            ids = []
            for i in range(COUNT):
                ids.append(in_f.readline().strip())

        # request all ids
        tweets = {}
        for tw in ids:
            try:
                tweets[tw] = api.get_status(tw)._json

            # tweet may be banned??
            except tweepy.errors.Forbidden:
                tweets[tw] = 'Forbidden'

            # tweet has been removed / deleted
            except tweepy.errors.NotFound:
                tweets[tw] = 'Not Found'

            except tweepy.errors.TweepyException as e:
                str_e = str(e)

                # sleep
                if 'Too Many Requests' in str_e or 'Rate limit exceeded' in str_e:
                    time.sleep(1000) # 15 minutes
                    ids.append(tw)

        # save data
        with open(f'{dest}{f_name}', 'w') as out_f:
            json.dump(tweets, out_f, indent=4)
        

    return 0


if __name__ == '__main__':
    main(sys.argv)
