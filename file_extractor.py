import datetime
import requests
import gzip
import os
from save_results import save_logs
import xmltodict
import json

todays_date = datetime.datetime.today().strftime('%Y_%m_%d')

def check_if_updtaed_today(name):
    if os.path.exists('data_files/last_pull_dates.json'):
        with open('data_files/last_pull_dates.json', 'r', encoding='utf-8') as updates_file:
            update_data = json.load(updates_file)
            if update_data[name] == todays_date:
                return True
            else:
                return False
    else:
        return False

def listify(item):
    if isinstance(item, list):
        return item
    else:
        return [item]

def check_or_make_dir_or_file(path, kind):
    all_paths = listify(path)
    for single_path in all_paths:
        if not os.path.exists(single_path):
            if kind == 'dir':
                os.mkdir(single_path)
                save_logs(f'created {single_path}')
            elif kind == 'file':
                open(single_path, 'w', encoding='utf-8').close()
                save_logs(f'created {single_path}')
            save_logs(f'created {single_path}')
        else:
            save_logs(f'{single_path} exists')

def prep_csv_files(gz_file_path):
    check_or_make_dir_or_file(f'{gz_file_path}', 'dir')

    for num in range(0, 10):
        check_or_make_dir_or_file(
            [f'{gz_file_path}/item_list_promo_0{num}.csv', f'{gz_file_path}/item_list_0{num}.csv'], 'file')
        check_or_make_dir_or_file(
            [f'{gz_file_path}/item_list_0{num}.csv', f'{gz_file_path}/item_list_0{num}.csv'], 'file')



    for num in range(10, 100):
        check_or_make_dir_or_file([f'{gz_file_path}/item_list_promo_{num}.csv', f'{gz_file_path}/item_list_{num}.csv'],
                                  'file')
        check_or_make_dir_or_file(
            [f'{gz_file_path}/item_list_{num}.csv', f'{gz_file_path}/item_list_0{num}.csv'], 'file')

def download_file(some_url, file_name, path='data_files', extract=False):
    gz_file_name = f'{path}/{file_name}'
    xml_file_name = gz_file_name.replace('gz', 'xml')
    save_logs(f'downloading {xml_file_name}')
    if os.path.exists(xml_file_name) and os.path.getsize(xml_file_name) > 0:
        save_logs(f'{xml_file_name} already exists')
    else:
        check_or_make_dir_or_file(path, 'dir')
        save_logs(f'downloading {some_url}')
        request = requests.get(some_url)
        save_logs(f'response code: {request.status_code}')
        with open(gz_file_name, 'wb') as download_save_file:
            download_save_file.write(request.content)
        download_save_file.close()
        if extract:
            with gzip.open(gz_file_name, 'rt', encoding='utf-8-sig') as unzipped:
                new_data = unzipped.read()
            with open(xml_file_name, 'w', encoding='utf-8') as xml_file:
                xml_file.write(new_data)
            save_logs(f'extracted {xml_file_name}')
            os.remove(gz_file_name)
            save_logs(f'deleted {gz_file_name}')
    return xml_file_name

def unzip_file(some_file):
    if os.path.exists(some_file):
        if os.path.getsize(some_file) < 500:
            save_logs(f'{some_file} seems to be a junkfile')
            return None
        save_logs(f'unzipping file')
        try:
            with gzip.open(some_file, 'rt', encoding='utf-8-sig') as unzipped:
                new_data = unzipped.read()
            new_file_name = some_file.replace('gz', 'xml')
            with open(new_file_name, 'w',  encoding='utf-8') as zip_save_file:
                zip_save_file.write(new_data)
            return new_file_name
        except gzip.BadGzipFile:
            print(f'failed to unzip the file')
            return None
    else:
        print('file does not exist')
        return None

def convert_date(date, time=None):
    combined_datetime = str(date)
    if time:
        combined_datetime += f' {time}'
    if len(combined_datetime) == 16:
        combined_datetime += ':00'
    elif '.' in combined_datetime:
        combined_datetime = combined_datetime.split('.')[0].replace('T', ' ')
    combined_datetime = combined_datetime.replace('/', '-')
    date_elements = combined_datetime.split('-')
    if len(date_elements[0]) != 4 or len(date_elements[1]) != 2 or int(date_elements[1]) > 12:
        save_logs(f'bad date format: {combined_datetime}, should be: %Y-%m-%d %H:%M:%S')
        raise ValueError
    return datetime.datetime.strptime(combined_datetime, '%Y-%m-%d %H:%M:%S')

def verify_and_add_price_date(root_datas, full_dict):
    n = 0
    root_datas = listify(root_datas)
    for root_data in root_datas:
        save_logs(f'running {n} of {len(root_datas)} codes for the same discount')
        n += 1
        if root_data['ItemCode'] in full_dict:
            if convert_date(root_data['PriceUpdateDate']) < convert_date(full_dict[root_data['ItemCode']]['update_date']):
                continue
        else:
            full_dict[root_data['ItemCode']] = {
                    'item_code': root_data['ItemCode'],
                    'item_name': root_data['ItemName'],
                    'item_price': root_data['ItemPrice'],
                    'item_date': root_data['PriceUpdateDate']
                }
    return full_dict

def save_price_list_to_file(root_datas,gz_file_path, promo):
    n = 0
    root_datas = listify(root_datas)
    for root_data in root_datas:
        n += 1
        temp_dict = {}
        save_logs(f'running {n} of {len(root_datas)} codes for the same root')

        item_code = root_data['ItemCode'].replace(',', '').replace('.','')
        item_name = root_data['ItemName'].replace(',', '')
        item_price = root_data['ItemPrice'].replace(',', '')
        item_date = root_data['PriceUpdateDate'].replace(',', '')
        if 'ManufactureName' in root_data.keys() and root_data['ManufactureName']:
            item_name += f'יצרן: {root_data["ManufactureName"].replace(",", "")}'
        list_index = item_code[-2:]
        list_index = '0' + list_index if len(list_index) < 2 else list_index
        temp_file = f'{gz_file_path}/temp_item_list.csv'
        os.remove(temp_file) if os.path.exists(temp_file) else None
        check_or_make_dir_or_file(temp_file, 'file')


        if promo:
            price_save_file = f'{gz_file_path}/item_list_promo_{list_index}.csv'
            if not root_data['minNumberOfItems']:
                item_min = '1'
            else:
                item_min = str(int(float((root_data['minNumberOfItems'].replace(',', '')))))
        else:
            price_save_file = f'{gz_file_path}/item_list_{list_index}.csv'
            item_min = '1'

        with open(price_save_file, 'r+', encoding='utf-8') as file_to_update:
            save_logs(f'parsing lines for {price_save_file}')
            list_of_lines = file_to_update.read().split('\n')
            for line in list_of_lines:
                break_line = line.split(',')
                if len(break_line) == 5:
                    temp_dict[break_line[0]] = [break_line[1], break_line[2], break_line[3], break_line[4]]

            if item_code in temp_dict:
                save_logs('found existing code. Checking date')
                if convert_date(item_date) > convert_date(temp_dict[item_code][2]):
                    save_logs('updating price')
                    temp_dict[item_code] = [item_name,item_price, item_date, item_min]
            else:
                save_logs('adding price')
                temp_dict[item_code] = [item_name, item_price, item_date, item_min]


            file_to_update.seek(0)
            file_to_update.truncate()

            for key, value in temp_dict.items():
                file_to_update.write(f'{key},{value[0]},{value[1]},{value[2]},{value[3]}\n')

def unify_promos_and_prices(gz_file_path):
    # Results table headers: Code, Name, Price, DiscountPricePerTotal, ItemsPerDiscount, DiscountPricePerItem, UpdateDate, FileUpdateDate
    unified_data = []
    nums = []
    for num in range(100):
        if num < 10:
            nums.append(f'0{num}')
        else:
            nums.append(str(num))
    for num in nums:
        promo_file = f'{gz_file_path}/item_list_promo_{num}.csv'
        price_file = f'{gz_file_path}/item_list_{num}.csv'
        unified_file = f'{gz_file_path}/unified_item_list_{num}.csv'
        check_or_make_dir_or_file([promo_file, price_file, unified_file], 'file')
        with open(price_file, 'r', encoding='utf-8') as data_from_price_file:
            price_data = data_from_price_file.read()
        with open(promo_file, 'r', encoding='utf-8') as data_from_promo_file:
            promo_data = data_from_promo_file.read()

        for price_line in price_data.split('\n'):
            added = False
            if price_line != '':
                for promo_line in promo_data.split('\n'):
                    if promo_line == '':
                        pass
                    elif price_line.split(',')[0] in promo_line.split(',')[0]:
                        price_line_split = price_line.split(',')
                        promo_line_split = promo_line.split(',')
                        items_per_discount = int(promo_line_split[4])
                        full_discount_price = float(promo_line_split[2])
                        if items_per_discount == 0:
                            break
                        discount_price_per_item = full_discount_price/items_per_discount
                        unified_data.append(f'{price_line_split[0]}, {price_line_split[1]}, {price_line_split[2]}'
                                            f',{full_discount_price}, {items_per_discount}, {discount_price_per_item}, {price_line_split[3]}, {todays_date}')
                        added = True
                        break
                if not added:
                    price_line_split = price_line.split(',')
                    unified_data.append((f'{price_line_split[0]}, {price_line_split[1]}, {price_line_split[2]}'
                                            f', n/a, n/a, n/a, {price_line_split[3]}, {todays_date}'))
        with open(unified_file, 'w', encoding='utf-8') as data_from_unified_file:
            data_from_unified_file.write('Code, Name, Price, DiscountPricePerTotal, ItemsPerDiscount, DiscountPricePerItem, UpdateDate, FileUpdateDate\n')
            for unified_line in unified_data:
                data_from_unified_file.write(f'{unified_line}\n')

        data_from_unified_file.close()
        data_from_price_file.close()
        data_from_promo_file.close()
        unified_data.clear()

def get_list_of_xmls(gz_file_path):
    full_set = set()
    full_xml_file_list = set(os.listdir(gz_file_path))
    for xml_file in full_xml_file_list:
        if xml_file.endswith('.xml'):
            full_set.add(xml_file)
    return full_set

def parse_data_per_xml_file(gz_file_path, xml_file):
    full_xml_file_path = f'{gz_file_path}/{xml_file}'
    save_logs(f'working on {xml_file}')
    with open(full_xml_file_path, 'r', encoding='utf-8') as f:
        data = f.read()
    xml_data = xmltodict.parse(data)
    return xml_data