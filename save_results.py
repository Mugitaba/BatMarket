
def save_results(file_name, all_codes):
    with open(f'data_files/{file_name}.csv', 'w') as f:
        f.write('name,code,price,date\n')
        for code in all_codes:
            f.write(f'{all_codes[code][0]},{all_codes[code][1]},{all_codes[code][2]},{all_codes[code][3]}\n')