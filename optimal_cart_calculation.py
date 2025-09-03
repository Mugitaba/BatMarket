from all_supers import all_supers_list


'''
list_of_items = [
    {
        'code': str, 
        'qty': int
    }, 
    {
        'code': str, 
        'qty': int 
    }
]

prices_dict = {
    'productCode': item barcode,
    'productName': item name,
    store: price
}

must_stores = {
     **store name with cheapest values (str)**: {
        'totalGap': float, 
        'hasUniqueItems': bool, 
        'uniqueItems': {},
        'cheapestItems': {
            '123456789': {
                'name': str, 
                'qty': int, 
                'totalPrice': float, 
                'gap': float
            }, 
            '987654321': {
                'name': str, 
                'qty': int, 
                'totalPrice': float, 
                'gap': float
            }, 
            '7290013585394': {
                'name': str, 
                'qty': int, 
                'totalPrice': float, 
                'gap': float
            }
        }
    }, 
    **store name with unique values (str)**: {
        'totalGap': float, 
        'hasUniqueItems': bool, 
        'cheapestItems': {},
        'uniqueItems': {
            '192837465': {
                'name': str, 
                'qty': int, 
                'totalPrice': float
            }
        }
    }
}
'''

list_of_all_super_names = [x.name for x in all_supers_list]

cheapest_dict = {}
full_gap = {}
for super_name in list_of_all_super_names:
    full_gap[super_name] = 0

def find_price_gaps(list_of_items, search_by_code):

    for item in list_of_items:

        barcode, qty = item['code'], item['qty']
        prices_dict = search_by_code(barcode, qty)

        if prices_dict == 'code not found':
            continue

        cheapest_dict[barcode] = {
            'name': prices_dict['productName'],
            'qty': qty,
            'totalPrice': None,
            'cheapestStores': [],
            'allStores': {},
            'gap': 0
        }

        for supermarket in list_of_all_super_names:
            if supermarket in prices_dict.keys():
                cheapest_dict[barcode]['allStores'][supermarket] = 0
                if not cheapest_dict[barcode]['totalPrice']:
                    cheapest_dict[barcode]['totalPrice'] = prices_dict[supermarket]
                    cheapest_dict[barcode]['cheapestStores'] = [supermarket]

                elif cheapest_dict[barcode]['totalPrice'] == prices_dict[supermarket]:
                    cheapest_dict[barcode]['cheapestStores'].append(supermarket)

                elif cheapest_dict[barcode]['totalPrice'] > prices_dict[supermarket]:
                    cheapest_dict[barcode]['gap'] = cheapest_dict[barcode]['totalPrice'] - prices_dict[supermarket]
                    cheapest_dict[barcode]['totalPrice'] = prices_dict[supermarket]
                    cheapest_dict[barcode]['cheapestStores'] = [supermarket]
                    for existing_store in cheapest_dict[barcode]['allStores'].keys():
                        cheapest_dict[barcode][existing_store] = prices_dict[existing_store] -  cheapest_dict[barcode]['totalPrice']
    return cheapest_dict


def get_high_gap_ane_unique_items(list_of_items, search_by_code):
    must_stores = {}

    cheapest_dict = find_price_gaps(list_of_items, search_by_code)

    for key, value in cheapest_dict.items():
        if len(value['allStores']) == 1:
            unique_store = list(value['allStores'].keys())[0]
            if unique_store not in must_stores.keys():
                must_stores[unique_store] = {
                    'totalGap': 0,
                    'hasUniqueItems': True,
                    'uniqueItems': {key: {}},
                    'cheapestItems': {}
                }

            must_stores[unique_store]['uniqueItems'][key]= {
                'name': value['name'],
                'qty': value['qty'],
                'totalPrice': value['totalPrice']
            }

        else:
            for supermarket in value['cheapestStores']:
                if supermarket not in must_stores.keys():
                    must_stores[supermarket] = {
                        'totalGap': value['gap'],
                        'hasUniqueItems': False,
                        'cheapestItems': {},
                        'uniqueItems': {}
                    }
                else:
                    must_stores[supermarket]['totalGap'] += value['gap']

                must_stores[supermarket]['cheapestItems'][key] = {
                    'name': value['name'],
                    'qty': value['qty'],
                    'totalPrice': value['totalPrice'],
                    'gap': value['gap']
                }



    return must_stores




# must_stores = get_high_gap_ane_unique_items()
