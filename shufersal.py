from file_extractor import download_file, check_or_make_dir_or_file, save_price_list_to_file, listify, \
    convert_date, prep_csv_files, unify_promos_and_prices, get_list_of_xmls
import requests
import xmltodict
import all_supers
from save_results import save_logs
import datetime

shufersal = all_supers.shufersal

file_name = 'temp_mame'
gz_file_path = 'data_files/shufersal'
store_list_file_name = 'shuersal_list_of_stores.gz'
shufersal_store_id_url = f"https://prices.shufersal.co.il/FileObject/UpdateCategory?catID=5&storeId=0"

promo_keys_dict = {
    'PriceUpdateDate': 'PromotionUpdateDate',
    'startDate': 'PromotionStartDate',
    'startTime': 'PromotionStartHour',
    'endDate': 'PromotionEndDate',
    'endTime': 'PromotionEndHour',
    'multipleAllowed': 'AllowMultipleDiscounts',
    'minNumberOfItems': 'MinQty',
    'ItemPrice': 'DiscountedPrice',
    'ItemName': 'PromotionDescription',
}

prep_csv_files(gz_file_path)

def clean_link(link):
    return link.replace('&amp;', '&')

def get_list_of_shufersal_stores():
    full_store_list_file_path = gz_file_path + '/' + store_list_file_name
    shufersal_store_list = requests.get(shufersal_store_id_url).text
    shufersal_store_list_download_link = [x for x in shufersal_store_list.split("\n") if "a href" in x][0].split('"')[1]
    clean_download_link = clean_link(shufersal_store_list_download_link)
    download_file(clean_download_link, store_list_file_name, gz_file_path, extract=True)
    with open(full_store_list_file_path.replace('gz','xml'), 'r', encoding='utf-8') as store_list_file:
        dict_list_of_stores = xmltodict.parse(store_list_file.read(), "utf-8")
        parsed_list_of_stores = dict_list_of_stores['asx:abap']['asx:values']['STORES']['STORE']
        return parsed_list_of_stores

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
    links = get_shufersal_items_files()
    for link in links:
        clean_link = link.split('.net/')[1].split('?')[0].replace('/', '_').replace('-', '_')
        clean_file_name = f'shufersal_{clean_link}'
        save_logs(f'prepping file: {clean_link}')
        check_or_make_dir_or_file(gz_file_path, 'dir')
        download_file(link, clean_file_name, path=gz_file_path, extract=True)


def get_perm_prices():
    unpack_prices()
    is_promo = False
    full_xml_file_list = get_list_of_xmls(gz_file_path)
    for xml_file in full_xml_file_list:
        if xml_file.startswith('shufersal_price') or xml_file.startswith('shufersal_promo'):
            full_xml_file_path = f'{gz_file_path}/{xml_file}'
            save_logs(f'working on {xml_file}')
            with open(full_xml_file_path, 'r') as f:
                data = f.read()
            xml_data = xmltodict.parse(data)
            save_logs(f'parsing {xml_file}')
            if 'Items' in xml_data['root'] and 'Item' in xml_data['root']['Items']:
                save_logs(f'{xml_file} was identified as a price file')
                root = xml_data['root']['Items']['Item']
                save_price_list_to_file(root, gz_file_path, promo=is_promo)
            else:
                save_logs(f'could not find price root, will try promotion root for {xml_file}')
                if 'Promotions' in xml_data['root']:
                    if 'Promotion' in xml_data['root']['Promotions'].keys():
                        save_logs(f'{xml_file} was identified as a promotion file')
                        get_promo_prices(xml_data['root']['Promotions']['Promotion'], xml_file)
    unify_promos_and_prices(gz_file_path)


def get_promo_prices(promotion_root, xml_file):
    roots = listify(promotion_root)
    n = 0
    for promotion in roots:
        temp_dict = {}
        n += 1
        all_keys_present = True
        for key, value in promo_keys_dict.items():
            if value not in promotion.keys():
                save_logs(f'{n} root in {xml_file} does not have {value}')
                all_keys_present = False
                break
            temp_dict[key] = promotion[value]

        if all_keys_present and 'startDate' in temp_dict.keys() and 'endDate' in temp_dict.keys() and 'startTime' in temp_dict.keys() and 'endTime' in temp_dict.keys():
            if convert_date(temp_dict['startDate'], temp_dict['startTime']) < datetime.datetime.now() < convert_date(temp_dict['endDate'], temp_dict['endTime']):
                save_logs('dates are valid')
                items_root = promotion['PromotionItems']['Item']
                items_root = listify(items_root)
                for item_root in items_root:
                    if 'ItemCode' in item_root.keys():
                        for item_code in listify(item_root['ItemCode']):
                            promos_dict = temp_dict.copy()
                            promos_dict['ItemCode'] = item_code
                            save_price_list_to_file(promos_dict, gz_file_path, promo=True)



