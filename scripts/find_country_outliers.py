import pandas as pd
import numpy as np
import os
import sys
import pycountry

#----------

'''
Goes through every csv finding anomalies in countries that could not be found.
Prints resulting set of countries
'''

#----------

NUM_ARGS = 1

#----------

'''
Goes through all arguments passed to file
Checks validity and formats args
'''
def check_args(args):
    # check num args
    if len(args) < NUM_ARGS + 1:
        raise(IndexError(f'Need {NUM_ARGS} args: path to csv files'))

    # extract args
    src_folder = args[1]

    # check if other paths exist
    if not os.path.isdir(src_folder):
        
        raise(FileNotFoundError(f"Can't find {src_folder}"))
    
    # format params
    if src_folder[-1] != '/':
        src_folder += '/'

    return src_folder

def find_countries(data_path):
    error_countries = set()  
    
    for csv_file in os.listdir(data_path):
        
        # collect data
        data = pd.read_csv(f'{data_path}{csv_file}')


        # select data with inconsistencies
        inconsistent = data[data['place'].notna()]
        inconsistent = inconsistent[inconsistent['country'].isna()] # select 
                        #where twitter provided place but not country mathced

        # loop through them adding countries to set
        for place in inconsistent['place']:
            error_countries.add(place)

    # output all countries
    print('\n'.join(list(error_countries))) 


def fix_countries(data_path, country_fixes):
    # loop through files
    for csv_file in os.listdir(data_path):
        
        # collect data
        data = pd.read_csv(f'{data_path}{csv_file}')

        # fix wrong data entries
        for i, place in enumerate(data['place']):
            if place is np.nan or place == np.nan or country_fixes.get(place, None) is None:
                continue
            data['country'][i] = pycountry.countries.lookup(country_fixes[place]).name

        data.to_csv(f'{data_path}{csv_file}', index=False)

#----------

def main():
    data_path = check_args(sys.argv)

    # the commented code below is meant to loop through the files finding 
    #   countries with inconsistent data
    # Then the country_fixes dictionary is manually built with the result from this 
    #   code
    # Lastly the uncommented code at the end fixes the data
    find_countries(data_path)

    country_fixes = {
        'La Réunion': 'reu',
        'Sint Maarten': 'sxm',
        'Syria': 'syr',
        'Ivory Coast': 'civ',
        'Republic of Korea': 'kor',
        'East Timor': 'tls',
        'Former Yugoslav Republic of Macedonia': 'mkd',
        'Congo Brazzaville': 'cog',
        'Macau': 'mac',
        'Saint Martin': 'sxm',
        'Swaziland': 'swz',
        'Brunei': 'brn',
        'Democratic Republic of Congo': 'cod',
        'Vatican City': 'vat',
        'Cape Verde': 'cpv',
        'Kosovo': 'srb',
        'The Netherlands': 'nld',
        'Russia': 'rus'
    }

    #fix_countries(data_path, country_fixes)
    

    return 0



if __name__ == '__main__':
    main()

