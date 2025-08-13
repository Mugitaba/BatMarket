import requests
import datetime
import xmltodict
from file_extractor import unzip_file, download_file, map_price_data, map_promo_data, merge_fixed_promo, listify
from save_results import save_results, save_logs
from all_supers import carfur
import os

promo_keys_dict = {
    'update_date': 'PromotionUpdateDate',
    'start_date': 'PromotionStartDate',
    'start_time': 'PromotionStartHour',
    'end_date': 'PromotionEndDate',
    'end_time': 'PromotionEndHour',
    'multiple_allowed': 'AllowMultipleDiscounts',
    'min_number_of_items': 'MinQty',
    'price': 'DiscountedPrice'
}

one_string_date = datetime.datetime.today().strftime('%Y%m%d')



def response_parser(response):
    price_links = []
    parse_response = response.text.split('"fileName\\">')
    for file_name in parse_response:
        clean_file_name = file_name.split('<\\/span>')[0]
        name_length = len(clean_file_name)
        if '.gz' in clean_file_name and 20 < len(clean_file_name) < 80:
            price_links.append(clean_file_name)
    return price_links


def get_carfur_file_links():
    response = requests.get(carfur.base_url)
    save_logs(f'status code: {response.status_code}')
    links_to_prices = response_parser(response)
    if len(links_to_prices) == 0:
        print('no files found for today')
        yesterday = (datetime.datetime.today() - datetime.timedelta(days=1)).strftime('%Y%m%d')
        query_url = f'{carfur.base_url}?p=./{yesterday}'
        carfur.base_url = f'{carfur.base_url}{yesterday}/'
        response = requests.get(query_url)
        links_to_prices  = response_parser(response)
        print(f'found {len(links_to_prices)} files for yesterday')
    else:
        carfur.base_url = f'{carfur.base_url}{one_string_date}/'

    return links_to_prices


def download_and_extract_file(link, n):
    n += 1
    if carfur.online_branch_code not in link:
        return None, n
    gz_file_path = f'data_files/{carfur.name}'
    if not os.path.exists(gz_file_path):
        os.makedirs(gz_file_path)
    name_from_link = link.split('/')[-1].replace('.gz', '')
    file_name = f'{gz_file_path}/{name_from_link}carfur_json_{n}'
    xml_file_name = file_name + '.xml'
    gz_file_name = file_name + '.gz'
    if os.path.exists(xml_file_name):
        extracted_file = xml_file_name
    elif os.path.exists(gz_file_name):
        extracted_file = unzip_file(gz_file_name)
    else:
        stores_xml_download_url = f'{carfur.base_url}{link}'
        print(stores_xml_download_url)
        download_file(stores_xml_download_url, gz_file_name)
        extracted_file = unzip_file(gz_file_name)
    if not extracted_file:
        return None, n
    try:
        with open(extracted_file, 'r') as xml_file:
            xml_data = xmltodict.parse(xml_file.read())
    except TypeError:
        os.remove(gz_file_name)
        save_logs(f'deleted gz_file, redownloading')
        download_file(stores_xml_download_url, gz_file_name)
        extracted_file = unzip_file(gz_file_name)
        with open(extracted_file, 'r') as xml_file:
            xml_data = xmltodict.parse(xml_file.read())

    return xml_data, n

def get_carfur_prices(price_links):
    all_codes = {}
    all_promos = {}
    n = 0
    promos_count = 0
    promo_links = []
    full_list_of_items = []

    for link in price_links:
        products_and_prices, n = download_and_extract_file(link, n)
        if not products_and_prices:
            continue
        if 'Items' in products_and_prices['Root']:
            root = products_and_prices['Root']['Items']['Item']
            full_list_of_items.append(map_price_data(root, carfur.name))
        else:
            save_logs(f'could not find price root, will try promotion root')
            if 'Promotions' in products_and_prices['Root']:
                promo_links.append(products_and_prices['Root']['Promotions'])
    for item in full_list_of_items:
        print(item.keys())
    for promo_root in promo_links:
        items_code = []
        temp_dict = {}
        if 'Promotion' not in promo_root.keys():
            save_logs('item with 0 count')
            continue
        promotion_root = promo_root['Promotion']
        roots = listify(promotion_root)
        for promotion in roots:
            if 'DiscountedPrice' in promotion.keys():
                for key, value in promo_keys_dict.items():
                    temp_dict[key] = promotion[value]
                items_root = promotion['PromotionItems']['Item']
                branches = listify(items_root)
                for item in branches:
                    all_promos[item['ItemCode']] = temp_dict.copy()
                    items_code.append(item['ItemCode'])

                promos_count += 1
                all_codes = map_promo_data(all_promos, all_codes)

    print(f'Found: {len(all_codes)} codes, and {promos_count} promos')
    full_list_of_codes = merge_fixed_promo(all_codes, all_promos)
    return full_list_of_codes



price_links = get_carfur_file_links()
list_of_all_codes = get_carfur_prices(price_links)
save_results(carfur.name, list_of_all_codes)