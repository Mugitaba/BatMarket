from datetime import datetime, timedelta
import os
from all_supers import all_supers_list

todays_date = datetime.today().strftime('%Y_%m_%d')
yesterday_date = (datetime.today() - timedelta(days=1)).strftime('%Y_%m_%d')

def get_existing_codes():
    full_code_list = {}
    if os.path.exists(f'data_files/barcode_base_{todays_date}.csv'):
        with open(f'data_files/barcode_base_{todays_date}.csv', 'r') as f:
            for line in f.readlines():
                data = line.split(',')
                full_code_list[data[0]] = data[1]
    elif os.path.exists(f'data_files/barcode_base_{yesterday_date}.csv'):
        with open(f'data_files/barcode_base_{yesterday_date}.csv', 'r') as f:
            for line in f.readlines():
                data = line.split(',')
                full_code_list[data[0]] = data[1]
    return full_code_list


def add_codes_from_supermarkets(existing_codes):
    for supermarket in all_supers_list:
        supermarket_file = f'data_files/{supermarket.name}.csv'
        if os.path.exists(supermarket_file):
            print(f'pulling list of codes from {supermarket.name}')
            with open(supermarket_file, 'r') as f:
                for line in f.readlines():
                    list_of_products = line.split(',')
                    if list_of_products[1] not in existing_codes:
                        existing_codes[list_of_products[1]] = list_of_products[0]
    return existing_codes


def save_codes(existing_codes):
    with open(f'data_files/barcode_base_{todays_date}.csv', 'w') as f:
        f.write('code,name\n')
        for code in existing_codes:
            f.write(f'{code},{existing_codes[code].strip()}\n')

def find_code(name):
    if os.path.exists(f'data_files/barcode_base_{todays_date}.csv'):
        with open(f'data_files/barcode_base_{todays_date}.csv', 'r') as f:
            for line in f.readlines():
                if name in line:
                    return line
    elif os.path.exists(f'data_files/barcode_base.csv'):
        with open(f'barcode_base.csv', 'r') as f:
            for line in f.readlines():
                if name in line:
                    return line
    return "couldn't find code"

updated_codes = add_codes_from_supermarkets(get_existing_codes())
save_codes(updated_codes)

print(find_code('טופו'))
