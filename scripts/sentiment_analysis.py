#Sentiment Analysis using VADER from a json file of tweets and outputting to a csv file 

import json
import csv
import os
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pycountry

#Create a SentimentIntensityAnalyzer object.
analyser = SentimentIntensityAnalyzer()

#Open the json file and read it
tweets = []
lang = []
country = []
for filename in os.listdir('/Users/pavly/Desktop'):
    if filename.endswith(".json"):
        with open(filename, 'r') as f:
            df = [json.loads(line) for line in f]
            tweets = [tweet['full_text'] for tweet in df]
            lang = [tweet['lang'] for tweet in df]
            country_place = [tweet['place'] for tweet in df]
            user = [tweet['user']['screen_name'] for tweet in df]
            location = [tweet['user']['location'] for tweet in df]

            #get the country from list country
            country_place = [tweet['country'] for tweet in country if tweet is not None]

            #get country from location
            country_location = [tweet.split(',')[-1] for tweet in location if tweet is not None]
            country_location = [tweet.split(' ')[-1] for tweet in country_location]

            #combine the two lists
            country = country_place + country_location

            #Attempts to gather country data based on tweet geoloc or user location
            #country = [tweet['place']['country'] for tweet in df if tweet['place'] is not None]
            #country = [tweet['user']['location'] for tweet in df if tweet['user']['location'] is not None]



#Create a csv file to write the results to.
with open('sentiment.csv', 'w') as csvfile:
    fieldnames = ['tweet', 'neg', 'neu', 'pos', 'compound'] 
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    print("CSV File Created")

    #For each tweet in the list, run the sentiment analysis and write the results to the csv file.
    for tweet in tweets:
        score = analyser.polarity_scores(tweet)
        #neg, neu, pos, compound are the keys for the dictionary "score" returned by the sentiment analysis function "polarity_scores"
        writer.writerow({'tweet': tweet, 'neg': score['neg'], 'neu': score['neu'], 'pos': score['pos'], 'compound': score['compound']}) 
    print("Sentiment Analysis Complete")


#count the number of tweets that are found and the number of tweets that are not found
count = 0
not_found = 0
for tweet in tweets:
    if tweet != "":
        count += 1
    else:
        not_found += 1

print("Number of tweets found: ", count)
print("Number of tweets not found: ", not_found)

#count the tweets in english and the tweets in other languages
count_en = 0
count_other = 0
for lang in lang:
    if lang == "en":
        count_en += 1
    else:
        count_other += 1

print("Number of tweets in English: ", count_en)
print("Number of tweets in other languages: ", count_other)

#count the number of tweets from per country for ukraine, russia, and other countries
count_ukr = 0
count_rus = 0
count_other = 0
for country in country:
    if country == "Ukraine":
        count_ukr += 1
    elif country == "Russia":
        count_rus += 1
    else:
        count_other += 1

print("Number of tweets from Ukraine: ", count_ukr)
print("Number of tweets from Russia: ", count_rus)
print("Number of tweets from other countries: ", count_other)

#count the number of unique users that tweeted
unique_users = set(user)
print("Number of unique users: ", len(unique_users))


#save the printed results to csv file called "results.csv"
with open('results.csv', 'w') as csvfile:
    fieldnames = ['Number of tweets found', 'Number of tweets not found', 'Number of tweets in English', 'Number of tweets in other languages', 'Number of tweets with no country']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerow({'Number of tweets found': count, 'Number of tweets not found': not_found, 'Number of tweets in English': count_en, 'Number of tweets in other languages': count_other, 'Number of tweets with no country': count_other})
    print("Results saved to CSV file")
    
#Close the csv file.
csvfile.close()

#Close the json file.
f.close()

