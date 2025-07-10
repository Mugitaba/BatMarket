class Supermarket:
    def __init__(self, name, online_branch_code, base_url):
        self.online_branch_code = online_branch_code
        self.base_url = base_url
        self.name = name



shufersal = Supermarket('shufersal', '0',
                                       'https://prices.shufersal.co.il/FileObject/UpdateCategory?catID=0&storeId=')
carfur = Supermarket('carfur', '5304', 'https://prices.carrefour.co.il/')
all_supers_list = [shufersal, carfur]

victory = Supermarket('victory', '097', 'https://laibcatalog.co.il/')
all_supers_list = [shufersal, carfur, victory]