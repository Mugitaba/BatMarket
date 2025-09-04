# import os.path
# import victory
# import carfur
# import shufersal
# import wolt
# import all_supers
#
#
# def count_items_per_store():
#     for store in all_supers.all_supers_list:
#         super_name = store.name
#         total_items = 0
#         for i in range(99):
#             index_num = '0' + str(i) if i < 10 else str(i)
#             file_name = f'data_files/{super_name}/unified_item_list_{index_num}.csv'
#             if os.path.exists(file_name):
#                 with open(file_name, 'r') as file_with_items:
#                     total_items += len(file_with_items.read().split('\n'))
#         print(super_name, total_items)
#
#
# def run_scrapes_for_all():
#     carfur.get_perm_prices()
#     victory.full_scrape()
#     shufersal.get_perm_prices()
#     wolt.get_wolt_prices()
#
# # run_scrapes_for_all()
# count_items_per_store()

from wolt import get_wolt_prices as wolt_get_prices
from victory import get_victory_files as victory_get_prices
from shufersal import get_perm_prices as shufersal_get_prices
from carfur import get_perm_prices as carfur_get_prices

wolt_get_prices('יד אליהו')
victory_get_prices()
shufersal_get_prices()
carfur_get_prices()
