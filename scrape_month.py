import tweepy
import sys
import os
import threading
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
API = None
LOCK = threading.Lock()

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
    except Exception as e:
        print('Failed Authentication')
        raise(e)
 
    return api

    

def main(args):
    # collect folder (month) of twitter data
    try:
        folder = args[1]
        # format input
        if folder[-1] != '/':
            folder += '/'

        # check if exists
        if not os.path.exists(folder):
            raise(FileNotFoundError(f"No such directory: '{folder}'"))

    except IndexError as e:
        print('Must pass directory of id files as argument')
        raise(e)

    except FileNotFoundError as e:
        print(f'{folder} directory could not be found')
        raise(e)

    # auth twitter api
    global API
    API = authenticate()

    threads = []

    # loop through all files in directory
    for f_name in sorted(os.listdir(folder)):
        # read all file
        with open(f'{folder}{f_name}', 'r') as f:
            tweet_ids = f.readlines()
        
        # separate file into batches for different threads
        batch = []
        count = 0
        for tweet_id in tweet_ids:
            # read each id
            tweet_id = tweet_id.strip()
            batch.append(tweet_id)

            count += 1

            # reset count and dispatch thread
            if count >= 1000:
                count = 0
                # send thread to request those 1000 tweets
                threads.append(threading.Thread(target=request_tweets, args=(batch,)))
                threads[-1].start()
                batch = []

            if len(threads) == 4:
                for thread in threads:
                    thread.join()
                threads = []

        # have thread update global variable and merge
        for thread in threads:
            thread.join()

        # store data
        global TWEET_DATA
        with open('out_file.json', 'w') as out_f:
            json.dump(TWEET_DATA, out_f, indent=4)


    return 0

def request_tweets(id_list):
    tweets = {}
    error_count = {}
    
    # request all tweets
    for tw in id_list:
        try:
            tweets[tw] = API.get_status(tw)._json

        except tweepy.errors.Forbidden:
            print('tweepy.errors.Forbiden')
            continue

        except tweepy.errors.NotFound:
            print('tweepy.errors.NotFound')
            continue

        except tweepy.errors.TweepyException as e:
            str_e = str(e)
            if 'Too Many Requests' in str_e or 'Rate limit exceeded' in str_e:
                sleep_time = 900
                # sleep for 15 minutes
                id_list.append(tw)
            else:
                # something else went wrong
                error_count[tw] = error_count.get(tw, 0) + 1
                if error_count[tw] < 5:
                    id_list.append(tw) # re add to try only top 5 times
                sleep_time(5)


            print('Sleeping!')
            time.sleep(sleep_time)
            print('Awake!')
            # try request again
            continue

    print(f'Done with {len(id_list)} threads!')
    # update global variable
    global TWEET_DATA
    global LOCK
    LOCK.aquire()
    TWEET_DATA.update(tweets)
    LOCK.release()

    return 0



if __name__ == '__main__':
    main(sys.argv)
