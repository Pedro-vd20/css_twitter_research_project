import pandas as pd
import os
import sys

#----------

'''
Does aggregate data counting from all the csv files
Merges data into single csv
'''

#----------

NUM_ARGS = 2

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
    
    # check if other paths exist
    if not (os.path.isdir(src_folder) and os.path.isdir(dest_folder)):
        raise(FileNotFoundError(f"Can't find {src_folder} or {dest_folder}"))
    
    # format params
    if src_folder[-1] != '/':
        src_folder += '/'
    if dest_folder[-1] != '/':
        dest_folder += '/'

    return src_folder, dest_folder


'''
Collects a csv file using pandas
Cleans unwanted values
'''
def clean_file(path):
  data = pd.read_csv(path)

  # remove unwanted data
  data = data[data['country'].notna()] # remove where no country

  return data


#----------

def main():
    data_path, dest_path = check_args(sys.argv)

    files = sorted(os.listdir(data_path))

    # collect first dataframe
    merged = clean_file(f'{data_path}{files[0]}')

    for csv_file in files[1:]:
      
        # collect file
        data = clean_file(f'{data_path}{csv_file}')

        # merge data
        merged = pd.concat([merged, data], axis=0, ignore_index=True)
    
    # save data
    merged.to_csv(f'{dest_path}merged_data.csv', index=False)
    
    return 0



if __name__ == '__main__':
    main()
