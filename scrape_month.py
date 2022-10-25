import tweepy

# here you must define the following variables (spelling-sensitvie):
#   api_key
#   api_secrets
#   access_token
#   access_secret
from secret import *

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


ID = '1498447924967137282'
# the below code will raise exception if user suspended / tweet deleted
tweet = api.get_status(ID)._json

for key in tweet.keys():
    print(f'{key}: {tweet[key]}', end='\n\n')


