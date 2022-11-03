import os
import sys
import json

#----------

'''
This script transforms the cities dataset to be useable by our processing files
Original format:
    {
        "id": 52,
        "name": "Ashkāsham",
        "state_id": 3901,
        "state_code": "BDS",
        "state_name": "Badakhshan",
        "country_id": 1,
        "country_code": "AF",
        "country_name": "Afghanistan",
        "latitude": "36.68333000",
        "longitude": "71.53333000",
        "wikiDataId": "Q4805192"
    },
Output format:
    {
        "city_name": "country_name"
    }
'''

#----------

NUM_ARGS = 1

#----------

'''
Checks if args passed are valid and formats them for later use
'''
def check_args(args):
    if len(args) < NUM_ARGS + 1:
        print('Insufficient args, need path to "cities.json" file')
        raise(IndexError('Insufficient args, need path to "cities.json" file'))

    # check path to cities
    src_file = args[1]
    if not os.path.isfile(src_file):
        print(f'Path to {src_file} invalid')
        raise(FileNotFoundError(f"Can't find {src_file}"))

    # get path from src
    path = '/'.join(src_file.split('/')[:-1]) + '/'

    return src_file, path

#----------

def main():
    # collect path to cities
    cities_path, folder = check_args(sys.argv)

    # load file
    with open(cities_path, 'r') as in_f:
        cities = json.load(in_f)

    # convert
    cities_new = {}
    for city in cities:
        city_name = city['name']
        country = city['country_name']

        # if not yet in dict
        if city_name not in cities_new.keys() or cities_new[city_name] == country:
            cities_new[city_name] = country
        # if already 1 country in dict
        elif type(cities_new[city_name]) is str:
            cities_new[city_name] = [cities_new[city_name], country]
        elif country not in cities_new[city_name]:
            cities_new[city_name].append(country)
            
    # save processed file
    # print(cities_new)
    with open(f'{folder}cleaned_cities.json', 'w') as out_f:
        json.dump(cities_new, out_f, indent=4)

    return 0


if __name__ == '__main__':
    main()

