from file_extractor import unzip_file, download_file
import requests
import xmltodict
import all_supers
import save_results

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
    for value in dict_list_of_stores:
        shufersal_store_id_dict[value['STORENAME']] = value['STOREID']
        for key, value in shufersal_store_id_dict.items():
            if key == 'שופרסל ONLINE':
                return value


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
            print(f'got this link: {link_from_table}')
    return links_from_table


def download_and_unzip_prices():
    all_codes = {}
    discounts = {}
    links = get_shufersal_items_files()
    for link in links:
        file_name = f'data_files/{link.replace("/", "_")}'
        download_file(link, file_name)
        prices = xmltodict.parse(unzip_file(file_name), "utf-8")
        try:
            if 'Items' in prices['root']:
                all_prices = prices['root']['Items']['Item']
                for price in all_prices:
                    if price['ItemCode'] in all_codes and price['PriceUpdateDate'] <= all_codes[price['ItemCode']][3]:
                        pass
                    else:
                        all_codes[price['ItemCode']] = [price['ItemName'], price['ItemCode'], price['ItemPrice'],
                                                        price['PriceUpdateDate']]
            elif 'Promotions' in prices['root']:
                all_prices = prices['root']['Promotions']['Promotion']
                for promotion in all_prices:
                    items = promotion['PromotionItems']['Item']
                    for item in items:
                        if 'promo' + item['ItemCode'] in all_codes and promotion['PriceUpdateDate'] <= \
                                all_codes[item['ItemCode']][3]:
                            pass
                        else:
                            all_codes['promo' + item['ItemCode']] = [promotion['PromotionDescription'],
                                                                     item['ItemCode'], promotion['DiscountedPrice'],
                                                                     promotion['PromotionUpdateDate']]

        except KeyError:
            print(f'error with this link: {link}')
            print('key Map:')
            for key in prices['root'].keys():
                print(key)
                if type(prices['root'][key]) == dict:
                    print(f'{key}: {prices["root"][key].keys()}')
        except TypeError:
            print(f'type error with this link: {link}')
            print('type Map:')
            for key in prices['root'].keys():
                print(key)
                print(type(prices['root'][key]))
    return all_codes


prices = download_and_unzip_prices()

save_results.save_results(shufersal.name, prices)
