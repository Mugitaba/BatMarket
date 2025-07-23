import all_supers
import os
from save_results import save_logs, cleanup_csv

list_of_files = all_supers.all_supers_list


def get_prices_per_product(code):
    prices = {}
    for supermarket in all_supers.all_supers_list:
        supermarket_file = f'data_files/{supermarket.name}.csv'
        if os.path.exists(supermarket_file):
            with open(supermarket_file, 'r') as f:
                for line in f.readlines():
                    list_of_products = line.split(',')
                    if code in list_of_products[1]:
                        prices[supermarket.name] = list_of_products[2]
    return prices


def create_all_codes():
    all_codes = {}
    for supermarket in all_supers.all_supers_list:
        supermarket_file = f'data_files/{supermarket.name}.csv'
        if os.path.exists(supermarket_file):
            save_logs(f'pulling list of codes from {supermarket.name}')
            with open(supermarket_file, 'r') as f:
                for line in f.readlines():
                    list_of_products = line.split(',')
                    if list_of_products[1] not in all_codes:
                        all_codes[list_of_products[1]] = list_of_products[0]
    with open(f'data_files/all_codes.csv', 'w') as f:
        f.write('code\n')
        for code in all_codes:
            f.write(f'{code}, {all_codes[code]}\n')

def find_codes_with_multiple_prices():
    multiple_prices_dict = {}
    multiple_prices_num = 0
    with open(f'data_files/all_codes.csv', 'r') as f:
        for line in f.readlines():
            if not line.startswith('code'):
                clean_line = line.split(',')[0].strip()
                multiple_prices_dict[clean_line] = [line.split(',')[1].strip(), 0]
    for supermarket in all_supers.all_supers_list:
        supermarket_file = f'data_files/{supermarket.name}.csv'
        if os.path.exists(supermarket_file):
            with open(supermarket_file, 'r') as f:
                for line in f.readlines():
                    clean_line = line.strip()
                    list_of_products = clean_line.split(',')
                    if list_of_products[1] in multiple_prices_dict:
                        multiple_prices_dict[list_of_products[1]][1] += 1
                        if multiple_prices_dict[list_of_products[1]][1] > 1:
                            multiple_prices_num += 1
    save_logs(f'there are {multiple_prices_num} codes with multiple prices')
    return multiple_prices_dict


def find_prices_for_all_codes():
    create_all_codes()
    codes = find_codes_with_multiple_prices()
    with open(f'data_files/price_compare.csv', 'w') as f:
        f.write('name')
        for supermarket in all_supers.all_supers_list:
            f.write(f', {supermarket.name}')
        f.write('\n')
        for code in codes:
            if codes[code][1] > 1:
                product_name = cleanup_csv(codes[code][0])
                f.write(product_name)
                prices = get_prices_per_product(code)
                for supermarket in all_supers.all_supers_list:
                    if supermarket.name in prices:
                        f.write(f', {prices[supermarket.name]}')
                    else:
                        f.write(', N/A')
                f.write('\n')

find_prices_for_all_codes()





