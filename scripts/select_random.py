import random
import os
import sys

def main(args):
    # check source path
    if len(args) < 2 or not os.path.isdir(args[1]):
        print('Source folder not provided / does not exist')
        return 1

    # check dest path
    if len(args) < 3 or not os.path.isdir(args[2]):
        print('Dest folder not provided / does not exist')
        return 1
    
    # format folders
    source_folder = args[1]
    if source_folder[-1] != '/':
        source_folder += '/'
    
    dest_folder = args[2]
    if dest_folder[-1] != '/':
        dest_folder += '/'

    # Get all months in source folder
    month_folders = sorted(os.listdir(source_folder))

    # loop through each month folder
    for month in month_folders:
        if not os.path.isdir(f'{source_folder}{month}') or month[0] == '.':
            continue
        print('month')
        
        # loop through each file in the folder
        files = sorted(os.listdir(f'{source_folder}{month}'))
        for f in files:
            print(f)
            # open file
            with open(f'{source_folder}{month}/{f}', 'r') as in_f:
                # read lines
                lines = in_f.readlines()

            # shuffle
            random.shuffle(lines)

            # check if output directory exists
            if not os.path.exists(f'{dest_folder}{month}'):
                os.mkdir(f'{dest_folder}{month}')

            # save file
            with open(f'{dest_folder}{month}/{f}', 'w') as out_f:
               out_f.write(''.join(lines)) 

    return 0



if __name__ == '__main__':
    main(sys.argv)
