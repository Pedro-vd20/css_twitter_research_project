import pandas as pd
import os

# Path to the dataset
path = '/scratch/pv850/css/css_twitter_research_project/sentiment_analysis/'
all_files = os.listdir(path) 
all_files = [os.path.join(path, f) for f in all_files if f.endswith('.csv')]
df = pd.concat((pd.read_csv(f) for f in all_files))


df_info = pd.DataFrame({'Number of tweets': [len(df)],
                        'Number of tweets in English': [len(df[df['lang'] == 'en'])],
                        'Number of tweets in Turkish': [len(df[df['lang'] == 'tr'])],
                        'Number of tweets in Spanish': [len(df[df['lang'] == 'es'])],
                        'Number of tweets in Russian': [len(df[df['lang'] == 'ru'])],
                        'Number of tweets in Ukrainian': [len(df[df['lang'] == 'uk'])],
                        'Number of unique users': [len(df['user_id'].unique())],
                        'Number of tweets per top 10 users': [df['user_name'].value_counts()[:10]]})

#save the dataframe as a csv file in specified path
destination = '/scratch/pv850/css/css_twitter_research_project/'
df_info.to_csv(os.path.join(destination, 'tweet_dataset_info.csv'))

print(os.path.join(destination, 'tweet_dataset_info.csv'))






