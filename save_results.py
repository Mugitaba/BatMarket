import datetime


def cleanup_csv(string):
    return string.replace('"','`').replace("'","`").replace('\n','')


def save_results(file_name, all_codes):
    if not all_codes:
        save_logs('None passed in. No codes to save')
    elif not isinstance(all_codes, dict):
        print(f' This is not a dict. It is a {type(all_codes)}. This will not do!')
    else:
        with open(f'data_files/{file_name}.csv', 'w') as f:
            f.write('name,code,price,date\n')
            for code in all_codes:
                name = cleanup_csv(all_codes[code][0])
                bcode = cleanup_csv(all_codes[code][1])
                price = cleanup_csv(all_codes[code][2])
                date = cleanup_csv(all_codes[code][3])
                f.write(f'{name},{bcode},{[price]},{date}\n')

def save_logs(log):
    with open(f'data_files/run_logs.txt', 'a') as log_file:
        time_now = datetime.datetime.now()
        log_file.write(f'{time_now}: {log}\n')
        log_file.close()