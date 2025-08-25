import os.path

import victory
import all_supers

for store in all_supers.all_supers_list:
    super_name = store.name
    total_items = 0
    for i in range(99):
        index_num = '0' + str(i) if i < 10 else str(i)
        file_name = f'data_files/{super_name}/unified_item_list_{index_num}.csv'
        if os.path.exists(file_name):
            with open(file_name, 'r') as file_with_items:
                total_items += len(file_with_items.read().split('\n'))
    print(super_name, total_items)

