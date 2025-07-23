import requests
from datetime import datetime, timedelta
import xmltodict
from file_extractor import unzip_file, download_file
from save_results import save_results, save_logs
from all_supers import victory

base_url = victory.base_url + 'NBCompetitionRegulations.aspx?code='
online_branch_code = '097'
chain_code = '7290661400001'
full_url = base_url + chain_code + online_branch_code

noraml_price_links = []
promo_price_links = []

def get_victory_price():
    all_regular_codes = {}
    all_promo_codes = {}
    
    result = requests.get(full_url)
    save_logs(full_url)
    if result.status_code != 200:
        save_logs(f' failed with status code {result.status_code}')
    elif 'אין קבצים להצגה' in result.text or '-097-' not in result.text:
        save_logs('no files from today, getting yesterday')
        today = datetime.today()
        yesterday = today - timedelta(days=1)
        result = requests.get(full_url + '&date=' + yesterday.strftime('%d/%m/%Y'))
    results_break = result.text.split("href='")
    
    for line in results_break:
        link = 'https://laibcatalog.co.il/' + line.split("'")[0].replace('\\', '/')
        if '-097-' in link and '7290661400001' in link:
            if 'Promo' in link:
                promo_price_links.append(link)
            else:
                noraml_price_links.append(link)
    
    for link in noraml_price_links:
        file_name = 'data_files/' + link.replace('/', '_')
        download_file(link, file_name)
        unzip_file(file_name)
        price_list = xmltodict.parse(unzip_file(file_name), "utf-8")
        try:
            for product in price_list['Prices']['Products']['Product']:
                if product['ItemCode'] not in all_regular_codes:
                    all_regular_codes[product['ItemCode']] = [product['ItemName'], product['ItemCode'], product['ItemPrice'], product['PriceUpdateDate']]
                elif product['PriceUpdateDate'] > all_regular_codes[product['ItemCode']][3]:
                    all_regular_codes[product['ItemCode']] = [product['ItemName'], product['ItemCode'], product['ItemPrice'], product['PriceUpdateDate']]
                else:
                    pass
        except KeyError:
            save_logs('could not parse xml. existing keys:')
            save_logs(price_list['Prices']['Products']['Product'].keys())
    
    return all_regular_codes, all_promo_codes


all_codes, promo_codes = get_victory_price()
save_results(victory.name, all_codes)

# url_for_url = 'https://laibcatalog.co.il/CompetitionRegulationsFiles/latest/7290661400001/Price7290661400001-239-202507091510-001.xml.gz'