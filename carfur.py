import requests
import datetime
import xmltodict
from file_extractor import unzip_file, download_file
import save_results
from all_supers import carfur


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
    for link in links:
        if f'-{carfur.online_branch_code}-' in link:
            file_name = f'data_files/{link.replace("/", "_")}'
            stores_xml_download_url = f'{carfur.base_url}{datetime.datetime.today().strftime("%Y%m%d")}/{link}'
            download_file(stores_xml_download_url, file_name)
            store_content_unzipped = unzip_file(file_name)
            products_and_prices = xmltodict.parse(store_content_unzipped, "utf-8")
            root_dir = products_and_prices['Root']
            for sub_dir in root_dir:
                if sub_dir == 'Items':
                    items_dir = root_dir[sub_dir]
                    for sub_sub_dir in items_dir:
                        if type(items_dir[sub_sub_dir]) == list:
                            for item in items_dir[sub_sub_dir]:
                                item_stats = [item['ItemName'], item['ItemCode'], item['ItemPrice'], item['PriceUpdateDate']]
                                if item['ItemCode'] not in all_codes:
                                    all_codes[item['ItemCode']] = item_stats
                                elif item['PriceUpdateDate'] > all_codes[item['ItemCode']][3]:
                                    all_codes[item['ItemCode']] = item_stats
                                else:
                                    pass
    return all_codes


links = get_carfur_list_of_stores()
all_codes = get_carfur_prices(links)
save_results.save_results(carfur.name, all_codes)