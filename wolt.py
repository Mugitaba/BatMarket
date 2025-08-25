import requests
from all_supers import wolt
import datetime
from file_extractor import (download_file, prep_csv_files, parse_data_per_xml_file, listify,
                            save_price_list_to_file, unify_promos_and_prices)
import xmltodict
import os
from save_results import save_logs

today = datetime.datetime.today().strftime('%Y-%m-%d')
url_with_today = f'{wolt.base_url}/{today}.html'
yesterday = (datetime.datetime.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
url_with_yesterday = f'{wolt.base_url}/{yesterday}.html'
gz_file_path = f'data_files/{wolt.name}'

keys_dict = {
    'ItemCode': 'ItemCode',
    'ItemName': 'ItemName',
    'ItemPrice': 'ItemPrice',
    'PriceUpdateDate': 'PriceUpdateTime'

}

promo_keys_dict = {
    'PriceUpdateDate': 'PromotionUpdateTime',
    'startDate': 'PromotionStartDate',
    'startTime': 'PromotionStartHour',
    'endDate': 'PromotionEndDate',
    'endTime': 'PromotionEndHour',
    'multipleAllowed': 'AllowMultipleDiscounts',
    'minNumberOfItems': 'MinPurchaseAmount',
    'ItemPrice': 'DiscountedPrice',
    'ItemName': 'PromotionDescription',
    'ItemCode': 'ItemCode'
}



def get_wolt_list_of_stores(keyword, today_failed):
    store_dict_list = []
    items_file_names = []

    url_with_day = url_with_yesterday if today_failed else url_with_today
    response = requests.get(url_with_day).text
    links = [x.split('"')[0] for x in response.split('<li><a href="')[1:]]

    link_of_stores = f'{wolt.base_url}/{links[0]}'
    file_name = f'{link_of_stores.split('download')[1].replace("/", "_").replace('-','_')}'

    if not os.path.exists(file_name.replace('.gz', '.xml')):
        save_logs(f'downloading list_of_stores {file_name}')
        downloaded_file_name = download_file(link_of_stores, file_name, path=gz_file_path, extract=True)

    with open(downloaded_file_name, 'r', encoding='utf-8') as stores_file:
        root = xmltodict.parse(stores_file.read())
    all_stores = root['Root']['SubChains']['SubChain']['Stores']['Store']
    for store in all_stores:
        if keyword in store['Address'] or keyword in store['StoreName']:
            store_dict_list.append((store['StoreID'], store['StoreName']))
            save_logs(f'found a store: {store["StoreName"]}')
    if len(store_dict_list) > 1:
        save_logs('there are multiple branches matching the selected query')
        print(f'found more than one branch: {store_dict_list}')
        raise ValueError
    elif len(store_dict_list) == 0:
        save_logs('no stores found')
        raise ValueError
    store_id, store_name = store_dict_list[0]
    for link in links:
        if f'-{store_id}-' in link:
            full_download_link = f'{wolt.base_url}/{link}'
            name_from_link = link.split('download/')[1].replace('/','_').replace('-', '_')
            new_file_name = download_file(full_download_link, name_from_link, path=gz_file_path, extract=True)
            items_file_names.append(new_file_name.replace('data_files/wolt/', ''))
    if not items_file_names:
        save_logs('no links found')
        if not today_failed:
            return get_wolt_list_of_stores(keyword, True)
    return store_name, items_file_names


def get_wolt_prices(branch_name='יד אליהו'):
    prep_csv_files(gz_file_path)
    store_name, file_names = get_wolt_list_of_stores(branch_name, False)
    for file_name in file_names:
        xml_data = parse_data_per_xml_file(gz_file_path, file_name)
        if 'Items' in xml_data['Root'].keys():
            roots = listify(xml_data['Root']['Items']['Item'])
            for root in roots:
                root['PriceUpdateDate'] = root['PriceUpdateTime']
            save_price_list_to_file(roots, gz_file_path, promo=False)
        elif 'Promotions' in xml_data['Root'].keys():
            temp_promotion_dict = {}
            roots = listify(xml_data['Root']['Promotions']['Promotion'])
            for root in roots:
                for key, value in promo_keys_dict.items():
                    if value in root.keys():
                        temp_promotion_dict[key] = root[value]
                root_branches = listify(root['PromotionItems']['PromotionItem'])
                for root_branch in root_branches:
                    for key, value in promo_keys_dict.items():
                        if value in root_branch.keys():
                            temp_promotion_dict[key] = root_branch[value]
                    save_price_list_to_file(temp_promotion_dict, gz_file_path, promo=True)
    unify_promos_and_prices(gz_file_path)
