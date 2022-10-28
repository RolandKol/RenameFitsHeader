import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

import tkinter as tk
import os
from astropy.io import fits


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

path = r'C:\Users\Roland K\Documents'
# path = filedialog.askdirectory()

mfiles = [os.path.join(root, name)
          for root, dirs, files in os.walk(path)
          for name in files
          if name.lower().endswith(('.fit', '.fits'))]
print('creating file list, please wait...')

f_counter = 0
def rename_filters(old_filter_name,new_filter_name, pbar):
    for f in mfiles:
        try:
            with fits.open(f, mode='update') as astro_f:

                if old_filter_name.upper() in astro_f[0].header['FILTER']:
                    astro_f[0].header['FILTER'] = new_filter_name
                    f_counter = f_counter + 1
                    process_dict.update({f: f_counter})
                    print(f'runing filter: {f}')
        except Exception as e:
            error_list_dict.update({f: e})
            print(f'NOT runing filter: {f}')
            continue
        pbar.update(1)

if __name__ == "__main__":
    urls = mfiles
    with tqdm(total=len(mfiles)/amount_of_filters, desc=f"Renaming: {f_counter}") as pbar:
        with ThreadPoolExecutor(max_workers=amount_of_filters) as ex:
            for k, val in filter_dict.items():
                futures = [ex.submit(rename_filters(k,val, pbar))]
                time.sleep(1)
                for future in as_completed(futures):
                    # result = future.result()
                    pbar.update(1)