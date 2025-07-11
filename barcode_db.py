from datetime import datetime, timedelta
import os
from all_supers import all_supers_list

todays_date = datetime.today().strftime('%Y_%m_%d')
yesterday_date = (datetime.today() - timedelta(days=1)).strftime('%Y_%m_%d')

def prep_line(line):
    strip_line = line.strip()
    line_list = strip_line.split(',')
    return line_list


def get_existing_codes():
    full_code_list = {}
    full_file_name = None

    if os.path.exists(f'data_files/barcode_base_{todays_date}.csv'):
        full_file_name = f'data_files/barcode_base_{todays_date}.csv'
    elif os.path.exists(f'data_files/barcode_base_{yesterday_date}.csv'):
        full_file_name = f'data_files/barcode_base_{yesterday_date}.csv'
    else:
        with open(f'data_files/barcode_base.csv', 'w') as f:
            f.write('code,name\n')
            print('no existing codes file found')
            return full_code_list

    with open(full_file_name, 'r') as f:
        for line in f:
            if not line.startswith('code'):
                data = prep_line(line)
                full_code_list[data[0]] = data[1]

    return full_code_list


def add_codes_from_supermarkets(existing_codes):
    for supermarket in all_supers_list:
        supermarket_file = f'data_files/{supermarket.name}.csv'
        if os.path.exists(supermarket_file):
            print(f'pulling list of codes from {supermarket.name}')
            with open(supermarket_file, 'r') as f:
                for line in f.readlines():
                    if not line.startswith('code'):
                        list_of_products = prep_line(line)
                        if list_of_products[1] not in existing_codes:
                            existing_codes[list_of_products[1]] = list_of_products[0]
    return existing_codes


def save_codes(existing_codes):
    with open(f'data_files/barcode_base_{todays_date}.csv', 'w') as f:
        f.write('code,name\n')
        for code in existing_codes:
            f.write(f'{code},{existing_codes[code].strip()}\n')

def find_product(name):
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

def create_name_list_per_barcode():
    name_list = {}
    if os.path.exists(f'data_files/barcode_base_{todays_date}.csv'):
        file_name = f'data_files/barcode_base_{todays_date}.csv'
    elif os.path.exists(f'data_files/barcode_base.csv'):
        file_name = f'data_files/barcode_base.csv'
    else:
        with open(f'data_files/barcode_base_{todays_date}.csv', 'w') as f:
            f.write('code,name\n')
        file_name = f'data_files/barcode_base_{todays_date}.csv'
    with open(file_name, 'r') as f:
        for line in f.readlines():
            if not line.startswith('code'):
                data = prep_line(line)
                if len(data) == 2:
                    name_list[data[0]] = [data[1]]
    for supermarket in all_supers_list:
        supermarket_file = f'data_files/{supermarket.name}.csv'
        if os.path.exists(supermarket_file):
            with open(supermarket_file, 'r') as f:
                for line in f.readlines():
                    list_of_products = prep_line(line)
                    if list_of_products[1] in name_list:
                        name_list[list_of_products[1]].append(list_of_products[0])
                    else:
                        name_list[list_of_products[1]] = [list_of_products[0]]
    with open(f'data_files/product_name_list_{todays_date}.csv', 'w') as f:
        f.write('code,name\n')
        for code in name_list:
            f.write(f'{code},{name_list[code][0]}\n')
            for name in name_list[code][1:]:
                f.write(f'{code},{name}\n')
    print('name list created')
    return file_name


def get_name_list(type, value):
    file_name = create_name_list_per_barcode()
    with open(file_name, 'r') as f:
        for line in f.readlines():
            data = line.split(',')
            if type == 'code':
                if value in data[0]:
                    return data[1:]
            elif type == 'name':
                if value in data[1]:
                    return data
                return data
    return f'{value} not found'


def refresh_codes_file():
    updated_codes = add_codes_from_supermarkets(get_existing_codes())
    save_codes(updated_codes)

refresh_codes_file()
print(get_name_list('code', '9720188060108'))