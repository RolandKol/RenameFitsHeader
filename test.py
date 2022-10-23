import os
import time
import threading
import tkinter as tk

from tkinter import filedialog
from astropy.io import fits
from tqdm import tqdm


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
amount_of_filters = num_to_change()
if amount_of_filters > 0:
    for file_num in range(amount_of_filters):
        print(f'\nFilter N: {file_num + 1}')
        filter_to_change = input('Enter the Filter name to change: ')
        filter_change_to = input('Enter new Filter name/value: ')
        filter_dict.update({filter_to_change.strip(): filter_change_to.strip()})
else:
    print(f'script terminated as Zero filters were selected')
    exit()

root = tk.Tk()
root.withdraw()
print('\nPlease select the folder')
path = filedialog.askdirectory()
if len(path) == 0:
    print('\nNo folder selected, script Canceled')
    exit()

print(f'\nWorking in directory: {path}')
print('\nThe following changes will be done in the selected folder')
for k, val in filter_dict.items():
    print(f'Filter: {k} rename to -> {val}')

if input('Are you sure? (y/n) ').lower() != "y":
    print('\nFilter naming script canceled')
    exit()

sub_folder_q = input('Do you want to include subfolders? (y/n) ').lower()
if sub_folder_q == "n":
    mfiles = [os.path.join(path, f)
              for f in os.listdir(path)
              if f.endswith(('.fit', '.fits'))]
elif sub_folder_q == "y":
    mfiles = [os.path.join(root, name)
              for root, dirs, files in os.walk(path)
              for name in files
              if name.endswith(('.fit', '.fits'))]
else:
    print('The Canceled as the answer was not clear enough')
    exit()

start = time.time()
process_dict = {}


def rename_filters(old_filter_name, new_filter_name):
    f_counter = 0
    for f in mfiles:
        # full_f = os.path.join(path, f)
        with fits.open(f, mode='update') as astro_f:
            if old_filter_name.upper() in astro_f[0].header['FILTER'].upper():
                astro_f[0].header['FILTER'] = new_filter_name
                f_counter = f_counter + 1
                process_dict.update({old_filter_name: f_counter})


threads = []
def start_threads(arg1, arg2):
    with tqdm(total=len(mfiles), desc=arg2) as pbar:
        th = threading.Thread(target=rename_filters, args=(arg1, arg2))
        # th_num.daemon = True
        print(f'{th} process started')
        th.start()
        threads.append(th)
        pbar.update(1)

for k, val in filter_dict.items():
    start_threads(k, val)
    print(f'Filter: {k}')
    # print(f'{process_dict[k]} files updated to "{val}"')

for x in threads:
    x.join()

end = time.time()
hours, rem = divmod(end - start, 3600)
minutes, seconds = divmod(rem, 60)
print('\nRenaming Finished in: ' + "{:0>2}h {:0>2}min {:05.2f}sec".format(int(hours), int(minutes), seconds))
