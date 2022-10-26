import csv
import os
import threading
import time
import tkinter as tk
from time import sleep
from tkinter import filedialog

from astropy.io import fits
from tqdm import tqdm


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def num_to_change():
    # function for user to enter the amount of filters he wants to rename
    # only whole number (integer) will be accepted to continue
    global user_num
    while True:
        try:
            user_num = int(input('\nEnter the NUMBER of filters to change: '))
            # int(amount_of_filters)
        except ValueError:
            print('This is not a whole integer number.')
            print('Try again')
            continue
        break
    return int(user_num)


filter_dict = {}  # dictionary holding old Filter name as Key and new filter name as item.
process_dict = {}  # dictionary holding files names with amended filters
error_list_dict = {} # dictionary holding Errors if any

amount_of_filters = num_to_change()

if amount_of_filters > 0:
    for file_num in range(amount_of_filters):
        filter_to_change = input(f'\nEnter the current Filter name you want to change: ')
        filter_change_to = input('Enter new Filter name/value: ')
        filter_dict.update({filter_to_change.strip(): filter_change_to.strip()})
else:
    print(f'\nscript terminated as Zero filters were selected')
    exit()

root = tk.Tk()
root.withdraw()
print('\nPlease select the folder')

# path = r'C:\Users\Roland K\PycharmProjects\RenameFitsHeader\Tests'
path = filedialog.askdirectory()

if len(path) == 0:
    print('\nNo folder selected, script Canceled')
    exit()
elif path == "C:/":
    print(f'{bcolors.FAIL}you selected the root directory: "{path}"  {bcolors.ENDC}')
    print(f'{bcolors.WARNING}<<It may be VERY Time Consuming!!!>> {bcolors.ENDC}')
    if input(f'{bcolors.FAIL}Are you sure? (y/n) {bcolors.ENDC}').lower() != "y":
        print('\nFilter naming script canceled')
        exit()
    else:
        print('\nIn this case, do not forget to grab the cup of tea or the bottle of beer')

print(f'\nWorking directory set to: "{path}"')
print('\nThe following changes will be done in the selected folder')
for k, val in filter_dict.items():
    print(f'Filter: {k} rename to -> {val}')

if input(f'Are you sure? (y/n) ').lower() != "y":
    print('\nFilter naming script canceled')
    exit()

sub_folder_q = input('Do you want to include subfolders? (y/n) ').lower()

if sub_folder_q == "n":
    print('\nCollecting filenames... please wait')
    mfiles = [os.path.join(path, f)
              for f in os.listdir(path)
              if f.lower().endswith(('.fit', '.fits'))]
elif sub_folder_q == "y":
    print('\nCollecting filenames... please wait')
    mfiles = [os.path.join(root, name)
              for root, dirs, files in os.walk(path)
              for name in files
              if name.lower().endswith(('.fit', '.fits'))]
else:
    print('Canceled, - Your answer was not clear enough')
    exit()

start = time.time()

totalfiles = len(mfiles)


def rename_filters(old_filter_name, new_filter_name):
    f_counter = 0
    with tqdm(total=totalfiles / 3, desc=f'Renaming To: "{new_filter_name}"') as pbar:
        for f in mfiles:
            try:
                with fits.open(f, mode='update') as astro_f:
                    if old_filter_name.upper() in astro_f[0].header['FILTER']:
                        astro_f[0].header['FILTER'] = new_filter_name
                        f_counter = f_counter + 1
                        process_dict.update({f: f_counter})

            except Exception as e:
                error_list_dict.update({f: e})
                continue

            sleep(0.01)
            pbar.update(totalfiles / (totalfiles / 3))


threads = []


def start_threads(arg1, arg2):
    th = threading.Thread(target=rename_filters, args=(arg1, arg2))
    # th_num.daemon = True
    th.start()
    threads.append(th)


for k, val in filter_dict.items():
    start_threads(k, val)

for x in threads:
    x.join()

sleep(0.1)
end = time.time()
hours, rem = divmod(end - start, 3600)
minutes, seconds = divmod(rem, 60)

print('\nProcess Finished in: ' + "{:0>2}h {:0>2}min {:05.2f}sec".format(int(hours), int(minutes), seconds))

if len(process_dict) > 0:
    print(f'\n{bcolors.WARNING}{len(process_dict)} files renamed from Total: {totalfiles}{bcolors.ENDC}')
    print('The "renamed_file_list.csv" is saved into the parent directory of the script')
    with open('renamed_file_list.csv', 'w') as f:
        w = csv.writer(f)
        w.writerows(process_dict.items())
else:
    print(f'\n{bcolors.FAIL}>>> NO files renamed!!!<<<{bcolors.ENDC}')
    print(f'Check if Filter names were selected correctly')
    print(f'or')
    print(f'If the correct folder was chosen')

if len(error_list_dict) > 0:
    print(f'\n{bcolors.WARNING}Amount of errors: {len(error_list_dict)}{bcolors.ENDC}')
    print('Error_List.csv is saved into the parent directory of the script')
    with open('Error_List.csv', 'w') as f:
        w = csv.writer(f)
        w.writerows(error_list_dict.items())


print(f'\n\n{bcolors.WARNING}Press ENTER to finish or simply close the window{bcolors.ENDC}')
finito = input("")
