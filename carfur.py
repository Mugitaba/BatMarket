import requests
import datetime
import xmltodict
from file_extractor import unzip_file, download_file, map_price_data
from save_results import save_results, save_logs
from all_supers import carfur
from barcode_db import todays_date


def get_carfur_list_of_stores():
    links = []
    response = requests.get(carfur.base_url)
    parse_response = response.text.split('"fileName\\">')
    for link in parse_response:
        clean_link = link.split('<')[0]
        links.append(clean_link)
    return links

def get_carfur_prices(links):
    all_codes = {}
    n = 0
    for link in links:
        if f'-{carfur.online_branch_code}-' in link:
            n += 1
            xml_file_name = f'data_files/carfur_xml_{todays_date}_{n}.xml'
            stores_xml_download_url = f'{carfur.base_url}{datetime.datetime.today().strftime("%Y%m%d")}/{link}'
            download_file(stores_xml_download_url, xml_file_name)
            products_and_prices = xmltodict.parse(unzip_file(xml_file_name), "utf-8")
            if 'Promotions' in products_and_prices['Root']:
                save_logs('promo')
            elif 'Items' in products_and_prices['Root']:
                root = products_and_prices['Root']['Items']['Item']
                all_codes = map_price_data(link, root, carfur.name)

            else:
                save_logs(f'could not find root in: {products_and_prices['Root']}')
    return all_codes


list_of_links = get_carfur_list_of_stores()
list_of_all_codes = get_carfur_prices(list_of_links)
save_results(carfur.name, list_of_all_codes)