import os
import all_supers
import json
from file_extractor import check_or_make_dir_or_file, save_logs
from flask import Flask, request, jsonify, render_template

gz_file_path = 'data_files/unified_data'
check_or_make_dir_or_file(gz_file_path, 'dir')

def list_code_name_stores():
    nums = [(str(x) + '0') for x in range(0, 10)] + [str(x) for x in range(10, 100)]

    for num in nums:
        temp_dict, code_and_name = {}, {}

        global_unified_file = f'{gz_file_path}/unified_item_list_{num}.json'
        check_or_make_dir_or_file(global_unified_file, 'file')

        with open(global_unified_file, 'w', encoding='utf-8') as data_from_unified_file:
            for store in all_supers.all_supers_list:
                store_unified_file = f'data_files/{store.name}/unified_item_list_{num}.csv'
                with open(store_unified_file, 'r', encoding='utf-8') as data_from_store_file:
                    list_of_lines_per_store = [line for line in
                                               data_from_store_file.read().split('\n')][1:]
                    for item in list_of_lines_per_store:
                        if item:
                            broken_item = item.split(',')
                            code_and_name[broken_item[0]] = broken_item[1]
                    for key, value in temp_dict.items():
                        if key in code_and_name.keys():
                            value.append(store.name)
                            code_and_name.pop(key)
                    for key, value in code_and_name.items():
                        temp_dict[key] = [value, store.name]
            json_with_codes_and_stores = json.dumps(temp_dict)
            data_from_unified_file.write(json_with_codes_and_stores)
            
            
def search_by_name(name):
    dict_of_matching_codes = {}
    
    name_parts = name.split(' ')

    for file in os.listdir(gz_file_path):
        if file.startswith('unified_item_list'):
            with open(f'{gz_file_path}/{file}') as json_file:
                data = json.load(json_file)
                for key, value in data.items():
                    if key not in dict_of_matching_codes.keys():
                        name_found = True
                        for part in name_parts:
                            if part not in value[0]:
                                name_found = False
                                break
                        if name_found:
                            dict_of_matching_codes[key] = value
    return dict_of_matching_codes

def search_by_code(code):

    prices_dict = {}

    file_index = code[-2:]
    global_unified_file = f'{gz_file_path}/unified_item_list_{file_index}.json'

    with open(global_unified_file, 'r', encoding='utf-8') as json_file:
        code_dict = json.load(json_file)
        if code in code_dict.keys():
            list_of_stores = code_dict[code][1:]
        else:
            return 'code not found'

        for store in list_of_stores:
            store_file_path = f'data_files/{store}/unified_item_list_{file_index}.csv'
            with open(store_file_path, 'r', encoding='utf-8') as price_file:
                list_of_prices = price_file.read().split('\n')
                for line in list_of_prices:
                    split_line = line.split(',')
                    if code in split_line[0]:
                        if code in prices_dict.keys():
                            prices_dict[code][store] = split_line[2:5]
                        else:
                            prices_dict[code] = {'name': split_line[1] ,store: split_line[2:5]}
    return prices_dict


app = Flask(__name__)
@app.route('/search', methods=['GET'])
def search_value():
    result_dict = {}
    query = request.args.get('q', '')

    if not query:
        return jsonify(None)
    elif query.isnumeric():
        save_logs(f'Barcode search: {query}')
        result_dict[query] = search_by_code(query)
    else:
        list_of_codes = search_by_name(query)
        for b_code in list_of_codes:
            save_logs(f'Name search for barcode: {b_code}')
            result_dict[b_code] = search_by_code(b_code)
    return jsonify(result_dict)

@app.route('/')
def present_site():
    return render_template('search-prices.html')

if __name__ == '__main__':
    app.run(debug=True)







