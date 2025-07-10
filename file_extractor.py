import requests
import gzip
import os

def download_file(some_url, file_name):
    if os.path.exists(file_name) and os.path.getsize(file_name) > 0:
        print(f'{file_name} already exists')
    else:
        if not os.path.exists('data_files'):
            print('creating data_files folder')
            os.mkdir('data_files')
        print(f'downloading {some_url}')
        request = requests.get(some_url)
        with open(file_name, 'wb') as save_file:
            save_file.write(request.content)
        save_file.close()


def unzip_file(some_file):
    print(f'unzipping {some_file}')
    with gzip.open(some_file, 'rt') as unzipped:
        return unzipped.read()