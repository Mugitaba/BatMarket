from all_supers import all_supers_list
from save_results import save_logs


def find_cheapest_prices(list_of_items,search_by_code):
    shopping_carts = {}
    gap_dict = {}
    for supermarket in all_supers_list:
        shopping_carts[supermarket.name] = {
            'totalPrice': supermarket.delivery_price,
            'cheapestProducts': [],
            'allProductsList': {}
        }

    for cart_item_code in list_of_items:
        barcode, qty = cart_item_code['code'], cart_item_code['qty']
        prices_dict = search_by_code(barcode, qty)
        sorted_price = sorted(prices_dict['stores'].items(), key=lambda x: x[1])
        min_price = sorted_price[0][1]
        if len(sorted_price) > 1:
            min_gap = sorted_price[1][1] - min_price
        else:
            min_gap = 0
        gap_dict[barcode] = min_gap
        for supermarket in prices_dict['stores'].keys():
            price = prices_dict['stores'][supermarket]
            shopping_carts[supermarket]['allProductsList'][barcode] = {
                'productName': prices_dict['productName'],
                'productPrice': price,
                'productQty': qty,
            }
            shopping_carts[supermarket]['totalPrice'] += price

            if price == min_price:
                shopping_carts[supermarket]['cheapestProducts'].append(barcode)

    return shopping_carts, gap_dict


def rank_stores(list_of_items, search_by_code):
    shopping_carts, gap_dict = find_cheapest_prices(list_of_items, search_by_code)

    sorted_shopping_carts = sorted(shopping_carts.items(), key=lambda item: item[1]['totalPrice'], reverse=True)
    clean_sorted_shopping_carts = []

    for cart in sorted_shopping_carts:
        if not cart[1]['cheapestProducts']:
            save_logs(f'removing cart {cart[0]} since it has no cheapest items')
        else:
            clean_sorted_shopping_carts.append(cart)
            save_logs(f'cheap products for {cart[0]}:')
            for item in cart[1]['cheapestProducts']:
                save_logs(f'{item}: {cart[1]['allProductsList'][item]}')

    return clean_sorted_shopping_carts, gap_dict


def get_optimal_cart(list_of_items, search_by_code):
    sorted_shopping_carts, gap_dict = rank_stores(list_of_items, search_by_code)
    unchecked_carts = [x[0] for x in sorted_shopping_carts]

    if len(sorted_shopping_carts) == 0:
        save_logs('No shopping carts')
        return {}

    elif len(sorted_shopping_carts) == 1:
        save_logs(f'only one cart. This is the only option')
        full_gap = sum([x for x in gap_dict.values()])
        sorted_shopping_carts[0][1]['fullGap'] = full_gap

    else:
        while unchecked_carts:
            save_logs(f'current number of carts: {len(unchecked_carts)}')
            save_logs(f'trying to dispose of {sorted_shopping_carts[0][0]}')
            current_cart = sorted_shopping_carts.pop(0)
            unchecked_carts.remove(current_cart[0])
            current_cart_content = current_cart[1]
            unique_items = []
            all_gaps = {}
            cart_gap = 0
            if len(sorted_shopping_carts) > 1:
                for cart in sorted_shopping_carts:
                    save_logs(f'checking {cart} as an alternative')
                    alt_cart = cart[1]
                    alt_products = [x for x in alt_cart['allProductsList'].keys()]
                    for product in current_cart_content['cheapestProducts']:
                        if product in alt_products:
                            gap = alt_cart['allProductsList'][product]['productPrice'] - current_cart_content['allProductsList'][product]['productPrice']
                            if product in all_gaps.keys():
                                all_gaps[product].append(gap)
                            else:
                                all_gaps[product] = [gap]
                            if product in unique_items:
                                unique_items.remove(product)
                            save_logs(f'found product: {product}. Gap: {gap}')
                        else:
                            unique_items.append(product)
                            save_logs(f'did not find product {product}')

                for key, value in all_gaps.items():
                    cart_gap += min(value)

                save_logs(f'this cart is cheaper by {cart_gap}')
                save_logs(f'this cart has the following unique items {unique_items}')

                if cart_gap > 30 or unique_items:
                    current_cart_content['fullGap'] = cart_gap
                    sorted_shopping_carts.append(current_cart)

                    if unique_items:
                        current_cart_content['uniqueItems'] = unique_items
                else:
                    save_logs(f'removed {current_cart} since the gap ({cart_gap}) did not exceed delivery cost')
                    save_logs(f'current status of carts: {sorted_shopping_carts}')

            else:
                save_logs(f'only one cart left. This one is the cheapest option')
                sorted_shopping_carts[0][1]['fullGap'] = cart_gap
                sorted_shopping_carts.append(current_cart)
                unchecked_carts = None

    for item in sorted_shopping_carts:
        total_sum = 0
        for code in item[1]['cheapestProducts']:
            price = item[1]['allProductsList'][code]['productPrice']
            save_logs(f'summing item {item} price {price}')
            total_sum += price
        item[1]['totalPrice'] = total_sum

    save_logs(f'final cart(s): {sorted_shopping_carts}')
    return sorted_shopping_carts