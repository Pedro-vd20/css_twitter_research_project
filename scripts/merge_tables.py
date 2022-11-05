import pandas as pd
import os
import sys

#----------

'''
Does aggregate data counting from all the csv files
Merges data into single csv
'''

#----------

NUM_ARGS = 3

#----------

'''
Goes through all arguments passed to file
Checks validity and formats args
'''
def check_args(args):
    # check num args
    if len(args) < NUM_ARGS + 1:
        print('Insufficient arguments, expected path to csv, path to cities JSON')
        raise(IndexError(f'Need {NUM_ARGS} args: path to csv files, path to cities json'))

    # extract args
    src_folder = args[1]
    dest_folder = args[2]
    confounders_path = args[3]

    # check if other paths exist
    if not (os.path.isdir(src_folder) and os.path.isfile(confounders_path) and os.path.isdir(dest_folder)):
        print(f"Can't find {src_folder} or {confounders_path} or {dest_folder}")
        raise(FileNotFoundError(f"Can't find {src_folder} or {confounders_path}"))
    
    # format params
    if src_folder[-1] != '/':
        src_folder += '/'
    if dest_folder[-1] != '/':
        dest_folder += '/'

    return src_folder, dest_folder, confounders_path

#----------

def main():
    data_path, dest_path, df_path = check_args(sys.argv)

    df_merged = pd.DataFrame({'country': [], 'date': [], 'sentiment': []})    

    # loop through each folder in data_path
    for sub_folder in sorted(os.listdir(data_path)):
        '''
        Expected file struct
            data_folder/
            |   sub_folder/
            |   |   data1.csv
            |   |   data2.csv
            |   |   ...
            |   sub_folder2/
            |   ...
        ''' 
        # loop through each file
        for in_f in sorted(os.listdir(f'{data_path}{sub_folder}')):
            # load csv
            data = pd.read_csv(f'{data_path}{sub_folder}/{in_f}')

            # calculate aggregate values
            data_aggregate = data[['country', 'sentiment']].groupby('country').mean()
            
            # get date from file
            data_aggregate['date'] = [data['date'].loc[0]] * len(data_aggregate)

            # get country column
            data_aggregate['country'] = data_aggregate.index
            # data_aggregate.reset_index()
            data_aggregate = data_aggregate[['country', 'date', 'sentiment']]

            # merge
            # df_merged = df_merged.append(data_aggregate, ignore_index=True)
            df_merged = pd.concat([df_merged, data_aggregate], axis=0, ignore_index=True)

            # break
        # break

    # load confounder dataset
    confounders = pd.read_excel(df_path)
    confounders.rename(columns={'Country': 'country'}, inplace=True)

    # left join
    df_merged = pd.merge(df_merged, confounders, on='country', how='left')
    
    # save data
    df_merged.to_csv(f'{dest_path}merged_data.csv')
    
    return 0



if __name__ == '__main__':
    main()