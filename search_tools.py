
def get_values():
    search_by = input('Search by bar(C)ode/item (N)ame?')
    search_value = input('Insert value to search')
    print('\n\n\n\n')
    return search_by, search_value


with open(f'data_files/price_compare.csv', 'r') as dataset:
    item_list = dataset.read().split('\n')

headers = item_list[0].split(',')

def search_by_barcode(barcode):
    for item in item_list[1:]:
        if barcode in item:
            parsed_list = item.split(',')
            for i in range(len(headers)):
                print(f'{headers[i]}: {parsed_list[i]}')
            print('\n\n')

def search_by_name(names):
    item_index = 0
    all_matches = []
    for item in item_list[1:]:
        in_list = True
        for name in names:
            if name not in item:
                in_list = False
        if in_list:
            parsed_list = item.split(',')
            all_matches.append(parsed_list)
            item_name = parsed_list[0]
            print(f'{item_index} - {item_name}')
            item_index += 1
    if len(all_matches) == 0:
        print('no matches found')
    else:
        chosen_index = int(input('type item index: '))
        print('\n\n')
        chosen_item = all_matches[chosen_index]
        for i in range(len(headers)):
            print(f'{headers[i]}: {chosen_item[i]}')
        print('\n\n')

def search():
    search_by, search_value = get_values()
    if search_by.lower() == 'n' or 'name' in search_by.lower():
        multiple_values = search_value.split(' ')
        search_by_name(multiple_values)
        return True
    elif search_by.lower() == 'c' or 'barcode' in search_by.lower():
        search_by_barcode(search_value)
        return True
    else:
        return False


keep_going = True

while keep_going:
    keep_going = search()