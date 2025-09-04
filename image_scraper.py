import os.path
import requests
from file_extractor import check_or_make_dir_or_file
import json

url = 'https://chp.co.il/%D7%AA%D7%9C%20%D7%90%D7%91%D7%99%D7%91/0/0'

def scrape_image(barcode):
   image_page = requests.get(f'{url}/{barcode}/0')
   image_lines = image_page.text.split('<')
   file_name = f'product_image_{barcode[-2:]}.json'
   folder_name = 'static/product_images/'
   full_path_name = folder_name + file_name
   for line in image_lines:
       if 'img data-uri' in line:
           new_line = f'<{line}'.replace('data-uri', 'src')
           check_or_make_dir_or_file(folder_name, 'dir')
           check_or_make_dir_or_file(full_path_name, 'file')
           with open(full_path_name, 'r+', encoding='utf-8') as image_file:
               if os.path.getsize(full_path_name) > 0:
                   old_dict = json.load(image_file)
               else:
                   old_dict = {}
               old_dict[barcode] = new_line
               image_file.seek(0)
               image_file.write(json.dumps(old_dict))
           return new_line
   else:
       return None