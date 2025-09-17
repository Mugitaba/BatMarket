import os.path
import requests
from file_extractor import check_or_make_dir_or_file
import json
from save_results import save_logs
from bs4 import BeautifulSoup as bs

url = 'https://chp.co.il/%D7%AA%D7%9C%20%D7%90%D7%91%D7%99%D7%91/0/0'

def scrape_image_from_external_source(barcode):
    correct_image = False

    save_logs(f'downloading image for {barcode}')
    image_page = requests.get(f'{url}/{barcode}/0')

    if not image_page.ok:
        save_logs(f'error from image site: {image_page.text}')
        return None

    image_page_soup = bs(image_page.text, 'html.parser')

    item_description = image_page_soup.find('meta', attrs={'name':'description'})
    clean_barcode = item_description.get('content').replace('השוואת מחירים בסופר של ', '')
    if barcode == clean_barcode:
        save_logs('confirmed image found')
        image_element = image_page_soup.find('img', attrs={'data-uri': True})
        if image_element:
            correct_image = image_element.get('data-uri')
            print(correct_image)
        else:
            return None

    if correct_image and correct_image.startswith('data:image/png;base64'):
        return correct_image
    else:
        return False

def get_image(barcode):
    file_name = f'product_image_{barcode}.json'
    folder_name = f'static/product_images/{barcode[-2:]:}/'
    full_path_name = folder_name + file_name

    check_or_make_dir_or_file(folder_name, 'dir')
    check_or_make_dir_or_file(full_path_name, 'file')


    with open(full_path_name, 'r+', encoding='utf-8') as img_source:
        if os.path.getsize(full_path_name) > 0:
            img_dict = json.load(img_source)
            if barcode in img_dict.keys():
                return img_dict[barcode]
        else:
            img_dict = {}

        new_line = scrape_image_from_external_source(barcode)

        if new_line:
            img_dict[barcode] = new_line
            img_source.seek(0)
            img_source.write(json.dumps(img_dict))
            return new_line

    return None