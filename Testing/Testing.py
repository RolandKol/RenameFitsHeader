import csv
import os
import threading
import time
from atpbar import atpbar
import random
import tkinter as tk
from time import sleep
from tkinter import filedialog

from astropy.io import fits
from atpbar import flush

filter_dict = {}  # dictionary holding old Filter name as Key and new filter name as item.
process_dict = {}  # dictionary holding files names with amended filters
error_list_dict = {}  # dictionary holding Errors if any

amount_of_filters = int(input('\nEnter the NUMBER of filters to change: '))

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

path = r'C:\Users\Roland K\PycharmProjects\RenameFitsHeader\Files for Tests'
# path = filedialog.askdirectory()

start = time.time()

mfiles = [os.path.join(root, name)
          for root, dirs, files in os.walk(path)
          for name in files
          if name.lower().endswith(('.fit', '.fits'))]
print('creating file list, please wait...')

totalfiles = len(mfiles)


# sleep(0.01)
# pbar.update(totalfiles / (totalfiles / amount_of_filters))

def rename_filters(old_filter_name, new_filter_name):
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


def run_with_threading():
    def task(old_filter_name, new_filter_name, n, name):
        # for i in atpbar(range(n), name=name):
        for f in atpbar(mfiles, name=name):
            try:
                with fits.open(f, mode='update') as astro_f:
                    if old_filter_name.upper() in astro_f[0].header['FILTER']:
                        astro_f[0].header['FILTER'] = new_filter_name
                        f_counter = f_counter + 1
                        process_dict.update({f: f_counter})

            except Exception as e:
                error_list_dict.update({f: e})
                continue
        time.sleep(1.0001)

    threads = []
    for k, val in filter_dict.items():
        name = 'thread {}'.format(k)
        n = random.randint(5, 100000)
        t = threading.Thread(target=task, args=(k, val, n, name))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    flush()


run_with_threading()

sleep(0.1)
end = time.time()
hours, rem = divmod(end - start, 3600)
minutes, seconds = divmod(rem, 60)

print('\nProcess Finished in: ' + "{:0>2}h {:0>2}min {:05.2f}sec".format(int(hours), int(minutes), seconds))

if len(process_dict) > 0:
    print(f'\n{len(process_dict)} files renamed from Total: {totalfiles}')
    print('The "renamed_file_list.csv" is saved into the parent directory of the script')
    with open('renamed_file_list.csv', 'w') as f:
        w = csv.writer(f)
        w.writerows(process_dict.items())
else:
    print(f'\n>>> NO files renamed!!!<<<')
    print(f'Check if Filter names were selected correctly')
    print(f'or')
    print(f'If the correct folder was chosen')

if len(error_list_dict) > 0:
    print(f'\nAmount of errors: {len(error_list_dict)}')
    print('Error_List.csv is saved into the parent directory of the script')
    with open('Error_List.csv', 'w') as f:
        w = csv.writer(f)
        w.writerows(error_list_dict.items())

print(f'\n\nPress ENTER to finish or simply close the window')
finito = input("")
