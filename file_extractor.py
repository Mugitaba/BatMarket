import requests
import gzip
import os
from save_results import save_logs

def download_file(some_url, file_name):
    if os.path.exists(file_name) and os.path.getsize(file_name) > 0:
        save_logs(f'{file_name} already exists')
    else:
        if not os.path.exists('data_files'):
            save_logs('creating data_files folder')
            os.mkdir('data_files')
        save_logs(f'downloading {some_url}')
        request = requests.get(some_url)
        with open(file_name, 'wb') as save_file:
            save_file.write(request.content)
        save_file.close()


def unzip_file(some_file):
    save_logs(f'unzipping {some_file}')
    with gzip.open(some_file, 'rt') as unzipped:
        return unzipped.read()

def map_price_data(link, raw_data, super_name, keys_dict=None):
    prices_dict = {}

    if keys_dict:
        item_code = keys_dict['code']
        item_name = keys_dict['name']
        item_price = keys_dict['price']
        item_date = keys_dict['date']
    else:
        item_code = 'ItemCode'
        item_name = 'ItemName'
        item_price = 'ItemPrice'
        item_date = 'PriceUpdateDate'

    if isinstance(raw_data, list):
        try:
            for price in raw_data:
                prices_dict[price[item_code]] = [
                    price[item_name],
                    price[item_code],
                    price[item_price],
                    price[item_date]
                ]
        except Exception as er:
            save_logs(f'Got: {er} \nfor {super_name} \n link: {link} \n raw: {raw_data}')
            raise TypeError
    elif isinstance(raw_data, dict):
        try:
            prices_dict[raw_data[item_code]] = [
                raw_data[item_name],
                raw_data[item_code],
                raw_data[item_price],
                raw_data[item_date]
            ]
        except Exception as er:
            save_logs(f'Got: {er} \nfor {super_name} \n link: {link} \n raw: {raw_data}')
            raise TypeError
    else:
        save_logs('could not determine data structure')
        save_logs(type(raw_data))
        save_logs(raw_data)


    return prices_dict

