#TODO: add a mechanism ot check if the xml already existst and avoid downloading it
#TODO: delete older xmls

from all_supers import carfur
import requests
from save_results import save_logs
import datetime
from file_extractor import (download_file, convert_date, save_price_list_to_file, listify, prep_csv_files,
                            unify_promos_and_prices, get_list_of_xmls, parse_data_per_xml_file)
import xmltodict

# Preset vars:
file_list_url = carfur.base_url
yesterday = (datetime.datetime.today() - datetime.timedelta(days=1)).strftime('%Y%m%d')
gz_file_path = f'data_files/{carfur.name}'

# define mapping dicts:
promo_keys_dict = {
    'PriceUpdateDate': 'PromotionUpdateDate',
    'startDate': 'PromotionStartDate',
    'startTime': 'PromotionStartHour',
    'endDate': 'PromotionEndDate',
    'endTime': 'PromotionEndHour',
    'multipleAllowed': 'AllowMultipleDiscounts',
    'minNumberOfItems': 'MinQty',
    'ItemPrice': 'DiscountedPrice',
    'ItemName': 'PromotionDescription'
}

prep_csv_files(gz_file_path)

def get_response(file_url):
    raw_site = requests.get(file_url)
    save_logs(f'link: {file_url} -- status code: {raw_site.status_code}')
    return raw_site

def attempt_to_get_links ():
    page_with_links = get_response(file_list_url)
    if page_with_links.status_code == 200 and 'אין קבצים להצגה' not in page_with_links.text:
        return page_with_links
    else:
        query_url = f'{carfur.base_url}?p=./{yesterday}'
        carfur.base_url = f'{carfur.base_url}{yesterday}/'
        page_with_links = get_response(query_url)
        return page_with_links

def extract_links_from_page():
    page_with_links = attempt_to_get_links()
    clean_links = set()
    split_page = page_with_links.text.split('<a href=')
    for link in split_page[1:]:
        clean_link = carfur.base_url + link.split('"')[1].replace('\\/', '/')[2:-1]
        if carfur.online_branch_code in clean_link:
            clean_links.add(clean_link)
    return clean_links

def download_and_extract_file():
    clean_links = extract_links_from_page()
    for clean_link in clean_links:
        clean_file_name = clean_link.replace('https://prices.carrefour.co.il/', '').replace('/', '_').replace('-', '_')
        download_file(clean_link, clean_file_name, path=gz_file_path, extract=True)

def get_perm_prices():
    download_and_extract_file()
    is_promo = False

    full_xml_file_list = get_list_of_xmls(gz_file_path)
    for xml_file in full_xml_file_list:
        xml_data = parse_data_per_xml_file(gz_file_path, xml_file)
        if 'Items' in xml_data['Root']:
            if 'Item' in xml_data['Root']['Items']:
                root = xml_data['Root']['Items']['Item']
                save_price_list_to_file(root, gz_file_path, promo=is_promo)
        else:
            save_logs(f'could not find price root, will try promotion root')
            if 'Promotions' in xml_data['Root']:
                if 'Promotion' in xml_data['Root']['Promotions'].keys():
                    get_promo_prices(xml_data['Root']['Promotions']['Promotion'])
    save_logs('unifying promos and prices')
    unify_promos_and_prices(gz_file_path)




def get_promo_prices(promotion_root):
    temp_dict = {}
    roots = listify(promotion_root)

    for promotion in roots:
        if 'DiscountedPrice' in promotion.keys():
            for key, value in promo_keys_dict.items():
                if value in promotion.keys():
                    temp_dict[key] = promotion[value]

            if 'startDate' in temp_dict.keys() and 'endDate' in temp_dict.keys() and 'startTime' in temp_dict.keys() and 'endTime' in temp_dict.keys():
                if convert_date(temp_dict['startDate'], temp_dict['startTime']) < datetime.datetime.now() < convert_date(temp_dict['endDate'], temp_dict['endTime']):
                    items_root = promotion['PromotionItems']['Item']
                    items_root = listify(items_root)
                    for item_root in items_root:
                        if 'ItemCode' in item_root.keys():
                            for item_code in listify(item_root['ItemCode']):
                                promos_dict = temp_dict.copy()
                                promos_dict['ItemCode'] = item_code
                                save_price_list_to_file(promos_dict, gz_file_path, promo=True)


