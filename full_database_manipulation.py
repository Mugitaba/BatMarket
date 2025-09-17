import os
import all_supers
import json
from file_extractor import check_or_make_dir_or_file, save_logs
from flask import Flask, request, jsonify, render_template
from wolt import get_wolt_prices as wolt_get_prices
from victory import get_victory_files as victory_get_prices
from shufersal import get_perm_prices as shufersal_get_prices
from carfur import get_perm_prices as carfur_get_prices
from optimal_cart_calculation import get_optimal_cart
import image_scraper

gz_file_path = 'data_files/unified_data'
check_or_make_dir_or_file(gz_file_path, 'dir')


def list_code_name_stores():
    nums = []

    for n in range(100):
        if n < 10:
            nums.append(f'0{n}')
        else:
            nums.append(str(n))

    for num in nums:
        temp_dict = {}

        global_unified_file = f'{gz_file_path}/unified_item_list_{num}.json'
        check_or_make_dir_or_file(global_unified_file, 'file')

        with open(global_unified_file, 'w', encoding='utf-8') as data_from_unified_file:
            for store in all_supers.all_supers_list:
                code_and_name = {}
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
                            value['names'].append(code_and_name[key])
                            value['stores'].append(store.name)
                            code_and_name.pop(key)

                    for key, value in code_and_name.items():
                        temp_dict[key] = {'names': [value], 'stores': [store.name]}
            data_from_unified_file.write(json.dumps(temp_dict or {}))


def search_by_name(name):
    list_code_name_stores()
    dict_of_matching_codes = {}
    name_parts = name.split(' ')
    option_count = 0

    for file in os.listdir(gz_file_path):
        if file.startswith('unified_item_list') and os.path.getsize(f'{gz_file_path}/{file}') > 0:
            with open(f'{gz_file_path}/{file}', 'r', encoding='utf-8') as json_file:
                data = json.load(json_file)
                for key, value in data.items():
                    for name in value['names']:
                        is_value = True
                        for part in name_parts:
                            if part not in name:
                                is_value = False
                                continue
                    if is_value:
                        option_count += 1
                        dict_of_matching_codes[key] = value
                        print(option_count)
                if option_count > 50:
                    return dict_of_matching_codes

    return dict_of_matching_codes


def make_list_of_prices_per_code(store_file_path, store, search_item_code, prices_dict, number_of_items):
    with open(store_file_path, 'r', encoding='utf-8') as price_file:
        list_of_items = price_file.read().split('\n')

        for line in list_of_items:
            split_line = line.split(',')
            if search_item_code == split_line[0]:
                try:
                    normal_price = float(split_line[2])
                except ValueError:
                    normal_price = None
                try:
                    discount_price = float(split_line[5])
                except ValueError:
                    discount_price = None
                try:
                    min_for_discount = int(split_line[4])
                except ValueError:
                    min_for_discount = None

                if discount_price and min_for_discount:
                    normal_price_item_num = number_of_items % min_for_discount
                    discount_price_item_num = number_of_items - normal_price_item_num
                    price = (normal_price * normal_price_item_num) + (discount_price * discount_price_item_num)
                else:
                    price = normal_price * number_of_items

                if 'productCode' in prices_dict.keys() and prices_dict['productCode'] == search_item_code:
                    prices_dict['stores'][store] = price
                    return prices_dict

                if 'productCode' in prices_dict.keys() and prices_dict['productCode'] == search_item_code:
                    prices_dict['stores'][store] = price
                else:
                    prices_dict = {
                        'productCode': search_item_code,
                        'productName': split_line[1],
                        'stores': {store: price}
                    }
    return prices_dict


def search_by_code(code, number_of_items):
    prices_dict = {}

    file_index = code[-2:]
    global_unified_file = f'{gz_file_path}/unified_item_list_{file_index}.json'

    with open(global_unified_file, 'r', encoding='utf-8') as json_file:
        code_dict = json.load(json_file)
        if code in code_dict.keys():
            list_of_stores = code_dict[code]['stores']
        else:
            return 'code not found'

    for store in list_of_stores:
        save_logs(f'searching {code} in {store}')
        store_file_path = f'data_files/{store}/unified_item_list_{file_index}.csv'
        prices_dict = make_list_of_prices_per_code(store_file_path, store, code, prices_dict, number_of_items) or {}
        save_logs(prices_dict)

    return prices_dict


def return_list_of_products_by_name(name):
    forward_dict = {}
    dict_of_products = search_by_name(name)
    for key, value in dict_of_products.items():
        forward_dict[value['names'][0]] = key
    return forward_dict


def search_price_range(code):
    normal_price_range = (9000000, 0)
    discount_price_range = (9000000, 0)
    product_name = None

    file_index = code[-2:]
    global_unified_file = f'{gz_file_path}/unified_item_list_{file_index}.json'

    with open(global_unified_file, 'r', encoding='utf-8') as json_file:
        code_dict = json.load(json_file)
        if code in code_dict.keys():
            list_of_stores = code_dict[code]['stores']
        else:
            return 'code not found'

        for store in list_of_stores:
            store_file_path = f'data_files/{store}/unified_item_list_{file_index}.csv'
            with open(store_file_path, 'r', encoding='utf-8') as price_file:
                list_of_prices = price_file.read().split('\n')
                for line in list_of_prices:
                    split_line = line.split(',')
                    if code in split_line[0]:
                        if not product_name:
                            product_name = split_line[1]
                        try:
                            normal_price = float(split_line[2])
                            if normal_price < normal_price_range[0]:
                                normal_price_range = (normal_price, normal_price_range[1])
                            if normal_price > normal_price_range[1]:
                                normal_price_range = (normal_price_range[0], normal_price)
                        except ValueError:
                            pass
                        try:
                            if split_line[5] != 'n/a' and split_line[5] != 'NaN':
                                discount_price = float(split_line[5])
                                if discount_price < discount_price_range[0]:
                                    discount_price_range = (discount_price, discount_price_range[1])
                                if discount_price > discount_price_range[1]:
                                    discount_price_range = (discount_price_range[0], discount_price)
                        except ValueError:
                            pass

    if normal_price_range[0] > 1000:
        normal_price_range = (0, normal_price_range[1])
    if discount_price_range[0] > 1000:
        discount_price_range = (0, discount_price_range[1])

    price_range = {
        'productCode': code,
        'productName': product_name,
        'lowPrice': normal_price_range[0],
        'highPrice': normal_price_range[1],
        'lowDiscount': discount_price_range[0],
        'highDiscount': discount_price_range[1]
    }

    return price_range


app = Flask(__name__)


@app.route('/search', methods=['GET'])
def search_value():
    result_list = []
    query = request.args.get('q', '')

    if not query:
        result_list = [{
            'productCode': 'none',
            'lowPrice': 'none',
            'highPrice': 'none',
            'lowDiscount': 'none',
            'highDiscount': 'none'
        }]
    elif query.isnumeric():
        save_logs(f'Barcode search: {query}')
        result_list = [search_price_range(query)]
    else:
        list_of_codes = search_by_name(query)
        for b_code in list_of_codes:
            save_logs(f'Name search for barcode: {b_code}')
            result_list.append(search_price_range(b_code))
    return jsonify(result_list)


@app.route('/name-search', methods=['GET'])
def search_product_names():
    query = request.args.get('q', '')
    result_dict = return_list_of_products_by_name(query)
    return jsonify(result_dict)


@app.route('/backend-stuff', methods=['GET'])
def show_backend():
    return render_template('configurations.html')


@app.route('/backend-stuff/run-pull', methods=['GET'])
def scrape_full_data():
    try:
        wolt_get_prices('יד אליהו')
        victory_get_prices()
        shufersal_get_prices()
        carfur_get_prices()
    except Exception as e:
        return jsonify({'status': f'error: {e}'})
    return jsonify({'status': 'done'})


@app.route('/shopping-list', methods=['GET'])
def show_shopping_list():
    return render_template('list-prices.html')


@app.route('/shopping-list/get-prices', methods=['POST'])
def get_shopping_list_prices():
    price_list = []
    shopping_list = request.get_json()
    for item in shopping_list:
        price_list.append(search_by_code(item['barCode'], item['qty']))
    return jsonify(price_list) if price_list else jsonify([])


@app.route('/optimal-cart', methods=['GET'])
def render_optimal_cart():
    return render_template('optimal-cart.html')


@app.route('/optimal-cart/find-optimal-carts', methods=['POST'])
def get_optimal_carts():
    price_list = []
    shopping_list = request.get_json()
    for item in shopping_list:
        price_list.append({
            'code': item['barCode'],
            'qty': item['qty']
        }
        )
    optimal_cart = get_optimal_cart(price_list, search_by_code)
    return jsonify(optimal_cart) if optimal_cart else jsonify({})


@app.route('/')
def present_site():
    return render_template('search-prices.html')


@app.route('/get-image', methods=['GET'])
def get_image():
    code = request.args.get('q', '')
    potential_img_file = f'static/product_images/{code[-2:]}/product_image_{code}.json'

    if os.path.exists(potential_img_file):
        with open(potential_img_file, 'r', encoding='utf-8') as image_file:
            saved_dict = json.load(image_file)
            if code in saved_dict.keys():
                return {'image': saved_dict[code]}
    return {'image': image_scraper.get_image(code)}


if __name__ == '__main__':
    app.run(debug=True)
