import requests
from all_supers import wolt
import datetime
from file_extractor import unzip_file, download_file
import xmltodict
import os
from save_results import save_results

today = datetime.datetime.today().strftime('%Y-%m-%d')
url_with_today = f'{wolt.base_url}/{today}.html'

def get_links():
    response = requests.get(url_with_today).text
    list_of_refs = [x.split('"')[0] for x in response.split('<li><a href="')[1:]]
    return(list_of_refs)

def get_wolt_list_of_stores(links, keyword):
    store_id_list = []
    store_list = []
    link_of_stores = f'{wolt.base_url}/{links[0]}'
    file_name = f'data_files/{link_of_stores.replace("/", "_")}'
    if not os.path.exists(file_name):
        download_file(link_of_stores, file_name)
        print(f'downloading {file_name}')
    content = unzip_file(file_name)
    root = xmltodict.parse(content)
    all_stores = root['Root']['SubChains']['SubChain']['Stores']['Store']
    for store in all_stores:
        if keyword in store['Address'] or keyword in store['StoreName']:
            store_list.append({store['StoreName']: store['StoreID']})
            store_id_list.append(store['StoreID'])
    return store_list,store_id_list


def get_wolt_prices(links, store_list,ids):
    all_codes = {}
    all_prices_list = []
    for link in links[1:]:
        link_of_store = f'{wolt.base_url}/{link}'
        file_name = f'data_files/{link.replace("/", "_")}'
        if not os.path.exists(file_name):
            download_file(link_of_store, file_name)
            print(f'downloading {file_name}')
        content = unzip_file(file_name)
        root = xmltodict.parse(content)
        this_store_id = root['Root']['StoreID']
        if this_store_id in ids:
            all_prices_list.append(root['Root'])
    if not all_prices_list:
        print("found no matches :(")
        return None

    for price in all_prices_list:
        if 'Promotions' in price.keys():
            print('Promotions')
        elif 'Items' in price.keys():
            list_of_items = price['Items']['Item']
            for item in list_of_items:
                try:
                    item_stats = [item['ItemName'], item['ItemCode'], item['ItemPrice'], item['PriceUpdateTime']]
                    if item_stats[1] not in all_codes.keys():
                        all_codes[item_stats[1]] = item_stats
                except TypeError:
                    print(item[:100])
                    raise TypeError

    return all_codes


all_links = get_links()
list_of_stores, ids = get_wolt_list_of_stores(all_links, 'יד אליהו')
all_codes = get_wolt_prices(all_links, list_of_stores, ids)
save_results(wolt.name, all_codes)
