from all_supers import all_supers_list
from full_database_manipulation import search_by_code, list_code_name_stores


list_of_items = [
    {'code': '9720188060108','qty': 40},
    {'code': '7290000063300','qty': 1},
    {'code': '7290001594155','qty': 1},
    {'code': '7290013585394','qty': 40}
]

'''
final_super_list = [
    {super name: [[product list], total price],
     super name: [[product list], total price], 
    ...
    }
]

prices_dict = {
    'productCode': item barcode,
    'productName': item name,
    store: price
}
'''

list_of_all_super_names = [x.name for x in all_supers_list]

final_super_list = []

must_stores = {}
cheapest_dict = {}
full_gap = {}
for super_name in list_of_all_super_names:
    cheapest_dict[super_name] = {}
    full_gap[super_name] = 0
    for single_item in list_of_items:
        cheapest_dict[super_name][single_item['code']] = 0

def find_price_gaps(list_of_items):
    barcode_dict = {}

    for item in list_of_items:
        current_cheapest = None
        barcode, qty = item['code'], item['qty']
        prices_dict = search_by_code(barcode, qty)
        if prices_dict == 'code not found':
            continue
        barcode_dict[barcode] = prices_dict['productName']

        for supermarket in list_of_all_super_names:
            if supermarket in prices_dict.keys():
                if not current_cheapest:
                    current_cheapest = prices_dict[supermarket]
                    cheapest_dict[supermarket][barcode] = 1
                elif current_cheapest <= prices_dict[supermarket]:
                    cheapest_dict[supermarket][barcode] = current_cheapest - prices_dict[supermarket]
                elif cheapest_dict[supermarket][barcode]:
                    current_cheapest = cheapest_dict[supermarket][barcode]
                    for existing_store in cheapest_dict.keys():
                        if barcode in cheapest_dict[existing_store]:
                            cheapest_dict[existing_store][barcode] = current_cheapest - prices_dict[existing_store]

    return cheapest_dict, barcode_dict




def get_high_gap_ane_unique_items():
    cheapest, barcode_dict = find_price_gaps(list_of_items)

    for item in list_of_items:
        item_code = item['code']
        available_stores = []
        for store in cheapest.keys():
            if cheapest[store][item_code]:
                available_stores.append(store)
                item_value = cheapest[store][item_code]
                full_gap[store] += item_value if item_value < 0 else 0
                if full_gap[store] < -30:
                    if store in must_stores.keys():
                        must_stores[store]['isSignificantlyCheaper'] = True
                        must_stores[store]['priceGap'] = full_gap[store]
                    else:
                        cheaper_item_codes =  [x['code'] for x in list_of_items if cheapest[store][x['code']] < 0]
                        must_stores[store] = {
                            'isSignificantlyCheaper': True,
                            'cheaperItemCodes': cheaper_item_codes,
                            'cheaperItemNames': [barcode_dict[x] for x in cheaper_item_codes],
                            'hasUniqueItems': [],
                            'priceGap': full_gap[store]
                        }

        if len(available_stores) == 1:
            available_store = available_stores[0]
            if available_store in must_stores.keys():
                must_stores[available_store]['hasUniqueItems'].append({item_code: barcode_dict[item_code]})
            else:
                cheaper_item_codes = [x['code'] for x in list_of_items if cheapest[available_store][x['code']] < 0]
                must_stores[available_store] = {
                    'isSignificantlyCheaper': False,
                    'cheaperItemCodes': cheaper_item_codes,
                    'cheaperItemNames': [barcode_dict[x] for x in cheaper_item_codes],
                    'hasUniqueItems': [{item_code: barcode_dict[item_code]}],
                    'priceGap': full_gap[available_store]
                }
    return must_stores




must_stores = get_high_gap_ane_unique_items()
# for item in cheapest:
#     print(f'{item}: {cheapest[item]} - {full_gap[item]}')
#
# print('\n\n\n\n')

# for store in must_stores:
#     print(f'{store}: {must_stores[store]}')

print('The folowing stores have these unique items:')
for store in must_stores:
    print(f'{store}: {must_stores[store]['hasUniqueItems']}')
print('\n\n')
print('The following stroes present significantly cheaper options:')
for store in must_stores:
    print(f'{store}: {must_stores[store]['cheaperItemNames']} || Gap: {must_stores[store]['priceGap']}')
