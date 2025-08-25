from barcode_db import todays_date
from file_extractor import unzip_file, download_file
import requests
import xmltodict
import all_supers
from save_results import save_results, save_logs
import os

shufersal = all_supers.shufersal

file_name = 'data_files/temp_mame'
store_list_file_name = 'data_files/shuersal_list_of_stores.xml'

shufersal_store_id_url = f"https://prices.shufersal.co.il/FileObject/UpdateCategory?catID=5&storeId=0"

def clean_link(link):
    return link.replace('&amp;', '&')

def get_list_of_shufersal_stores():
    shufersal_store_list = requests.get(shufersal_store_id_url).text
    shufersal_store_list_download_link = [x for x in shufersal_store_list.split("\n") if "a href" in x][0].split('"')[1]
    download_file(clean_link(shufersal_store_list_download_link), store_list_file_name)
    store_list_file = unzip_file(store_list_file_name)
    dict_list_of_stores = xmltodict.parse(store_list_file, "utf-8")['asx:abap']['asx:values']['STORES']['STORE']
    return dict_list_of_stores

def get_shufersal_online_branch_code():
    shufersal_store_id_dict = {}
    dict_list_of_stores = get_list_of_shufersal_stores()
    for store in dict_list_of_stores:
        shufersal_store_id_dict[store['STORENAME']] = store['STOREID']
        for key, value in shufersal_store_id_dict.items():
            if key == 'שופרסל ONLINE':
                return value
    return None


def get_shufersal_items_files():
    links_from_table =[]
    shufersal.online_branch_code = get_shufersal_online_branch_code()
    store_site_content = requests.get(shufersal.base_url+str(shufersal.online_branch_code))
    table = str(store_site_content.content)
    break_lines = table.split('<td><a href="')
    for line in break_lines:
        if line.startswith('http'):
            link_from_table = clean_link(line.split('"')[0])
            links_from_table.append(link_from_table)
            save_logs(f'got this link: {link_from_table}')
    return links_from_table


def unpack_prices():
    n = 0
    links = get_shufersal_items_files()
    db_codes = get_existing_prices()
    all_codes = parse_shufersal_prices({}, '', db_codes)
    for link in links:
        n += 1
        xml_file_name = f'data_files/shufersal_xml_{todays_date}_{n}.xml'
        all_codes = parse_shufersal_prices(all_codes, link, xml_file_name)

    return all_codes


def get_existing_prices():
    db_file_name = f'data_files/{shufersal.name}_historic_db.xml'
    if os.path.exists(db_file_name):
        save_logs('found historic db, retrieving data')
        with open(db_file_name, 'r') as f:
            existing_data = f.read()
            parsed_prices = xmltodict.parse(existing_data, "utf-8")
    else:
        save_logs('no historic db found')
        parsed_prices = {}
    return parsed_prices


def parse_shufersal_prices(all_codes, link, xml_file_name):

    if 'promo' in link.lower():
        save_logs('promo link')
    elif '/Price' in link:
        save_logs('fixed price link')
        download_file(link, xml_file_name)
        xml_data = xmltodict.parse(unzip_file(xml_file_name), "utf-8")
        if 'Promotions' in xml_data['Root'].keys():
            pass
        else:
            raw_data = xml_data['Root']['Items']['Item']
            all_prices = map_price_data(link, raw_data,shufersal.name)
            for price in all_prices:
                if price in all_codes and all_prices[price][3] <= all_codes[price][3]:
                    pass
                else:
                    all_codes[price] = all_prices[price]
    else:
        save_logs('could not determine the link type')

    return all_codes


prices = unpack_prices()

save_results(shufersal.name, prices)
