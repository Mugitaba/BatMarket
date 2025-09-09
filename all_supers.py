class Supermarket:
    def __init__(self, name, online_branch_code, base_url,delivery_price):
        self.online_branch_code = online_branch_code
        self.base_url = base_url
        self.name = name
        self.delivery_price = delivery_price



shufersal = Supermarket(
    'shufersal', '0',
    'https://prices.shufersal.co.il/FileObject/UpdateCategory?catID=0&storeId=',
    30.0
)
carfur = Supermarket(
    'carfur',
    '5304',
    'https://prices.carrefour.co.il/',
    30.0
)

victory = Supermarket(
    'victory',
    '097',
    'https://laibcatalog.co.il/',
    30.0)

wolt = Supermarket(
    'wolt',
    'None',
    'https://wm-gateway.wolt.com/isr-prices/public/v1',
    20.0
)

all_supers_list = [shufersal, carfur, victory, wolt]