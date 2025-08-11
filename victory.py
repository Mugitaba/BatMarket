import requests
import datetime
from file_extractor import (download_file, prep_csv_files, get_list_of_xmls, parse_data_per_xml_file, listify,
                            convert_date, save_price_list_to_file, unify_promos_and_prices)
from save_results import save_logs
from all_supers import victory

base_url = victory.base_url + 'NBCompetitionRegulations.aspx?code='
online_branch_code = '097'
chain_code = '7290661400001'
full_url = base_url + chain_code + online_branch_code
gz_file_path = f'data_files/{victory.name}'

promo_keys_dict = {
    'PriceUpdateDate': 'PriceUpdateDate',
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

def get_victory_files():
    
    result = requests.get(full_url)
    save_logs(full_url)
    if result.status_code != 200:
        save_logs(f' failed with status code {result.status_code}')
    elif 'אין קבצים להצגה' in result.text or f'-{online_branch_code}-' not in result.text:
        save_logs('no files from today, getting yesterday')
        today = datetime.today()
        yesterday = today - datetime.timedelta(days=1)
        result = requests.get(full_url + '&date=' + yesterday.strftime('%d/%m/%Y'))
    results_break = result.text.split("href='")
    
    for line in results_break:
        link = 'https://laibcatalog.co.il/' + line.split("'")[0].replace('\\', '/')
        if f'-{online_branch_code}-' in link and chain_code in link:
            clean_link = link.split(f'latest/{chain_code}/')[1].split('.xml')[0].replace('/', '_').replace('-', '_')
            file_name = f'{clean_link}.gz'
            download_file(link, file_name, path=gz_file_path, extract=True)

def map_victory_prices():
    full_xml_file_list = get_list_of_xmls(gz_file_path)
    for file in full_xml_file_list:
        xml_data = parse_data_per_xml_file(gz_file_path, file)
        if 'Promo' in file:
            roots = listify(xml_data['Promos']['Sales']['Sale'])
            temp_dict = {}

            for promotion in roots:
                if 'DiscountedPrice' in promotion.keys():
                    for key, value in promo_keys_dict.items():
                        if value in promotion.keys():
                            temp_dict[key] = promotion[value]

                    if 'startDate' in temp_dict.keys() and 'endDate' in temp_dict.keys() and 'startTime' in temp_dict.keys() and 'endTime' in temp_dict.keys():
                        if convert_date(temp_dict['startDate'],
                                        temp_dict['startTime']) < datetime.datetime.now() < convert_date(
                                temp_dict['endDate'], temp_dict['endTime']):
                            item_root = temp_dict.copy()
                            item_root['ItemCode'] = promotion['ItemCode']
                            save_price_list_to_file(item_root, gz_file_path, promo=True)

        else:
            is_promo = False
            roots = listify(xml_data['Prices']['Products']['Product'])
            save_price_list_to_file(roots, gz_file_path, promo=is_promo)



            # print(f'price: {xml_data['Prices']['Products']['Product']}')
    #         for product in price_list['Prices']['Products']['Product']:
    #             if product['ItemCode'] not in all_regular_codes:
    #                 all_regular_codes[product['ItemCode']] = [product['ItemName'], product['ItemCode'],
    #                                                           product['ItemPrice'], product['PriceUpdateDate']]
    #             elif product['PriceUpdateDate'] > all_regular_codes[product['ItemCode']][3]:
    #                 all_regular_codes[product['ItemCode']] = [product['ItemName'], product['ItemCode'],
    #                                                           product['ItemPrice'], product['PriceUpdateDate']]
    #
    # for link in promo_price_links:
    #     price_list = xmltodict.parse(unzip_file(link), "utf-8")
    #     try:
    #         for product in price_list['Prices']['Products']['Product']:
    #             if product['ItemCode'] not in all_promo_codes:
    #                 all_promo_codes[product['ItemCode']] = [product['ItemName'], product['ItemCode'], product['ItemPrice'], product['PriceUpdateDate']]
    #             elif product['PriceUpdateDate'] > all_promo_codes[product['ItemCode']][3]:
    #
    #
    # for link in noraml_price_links:
    #
    #     price_list = xmltodict.parse(unzip_file(file_name), "utf-8")
    #     try:
    #
    #             else:
    #                 pass
    #     except KeyError:
    #         save_logs('could not parse xml. existing keys:')
    #         save_logs(price_list['Prices']['Products']['Product'].keys())
    #
    # return all_regular_codes, all_promo_codes


get_victory_files()
map_victory_prices()
unify_promos_and_prices(gz_file_path)

# url_for_url = 'https://laibcatalog.co.il/CompetitionRegulationsFiles/latest/7290661400001/Price7290661400001-239-202507091510-001.xml.gz'