import csv
import os.path
from operator import itemgetter

'''
program to handle CSV file
'''

'''
Open the File
'''


def extract_csv_data(my_file):
    data = open(my_file, encoding='utf-8')
    csv_data = csv.reader(data, delimiter=",")
    line_csv_data = list(csv_data)
    return line_csv_data


def create_file_name(fname):
    fpn=get_split_file_path(fname)
    new_name = fpn[0]+'\sort_out_' + fpn[1]
    print(f'New FileName for Sort output is {new_name}')
    return new_name


def sort_file_out(pk, my_file, new_file_name):
    sort_csv_data = []
    header = my_file[0]
    body = my_file[1:]
    for line in sorted(body, key=itemgetter(pk)):
        sort_csv_data.append(line)
    file_to_output = open(new_file_name, mode='w', newline='')
    csv_writer = csv.writer(file_to_output, delimiter=',')
    csv_writer.writerow(header)
    csv_writer.writerows(sort_csv_data)


def get_file_name(num):
    while True:
        file_path = input("enter "+num+" file path:")
        if os.path.isfile(file_path):
            print(f'{num} file entered found: {file_path}')
            break
        else:
            print(f'{num} file entered NOT FOUND: {file_path}')
            continue
    return file_path


def get_primary_key(header, num):
    while True:
        try:
            print('Choose Primary Key from Header')
            print(header)
            pkey = input(f'Enter Primary Key for {num} File')
            pkey_pos = header.index(pkey)
        except ValueError:
            print(f'Primary Key for {num} File NOT Found')
            continue
        else:
            print(f'Primary Key for {num} File Found: {pkey} at position : {pkey_pos}')
            break
    return pkey_pos


def get_split_file_path(file_pathname):
    fpath = file_pathname
    fpn = list(os.path.split(os.path.abspath(fpath)))
    return fpn

'''
Start of main program
ask use for file name with check
get headers from the file
ask user for the primary key with check
create filename for storing sort data
sort the file
'''


def compare_2_file():
    w = 1
    while w < 3:
        if w == 1:
            v = "First"
        else:
            v = "Second"
        w += 1
        # Ask User for input:
        file = get_file_name(v)

        # Call function to load Original
        file_data = extract_csv_data(file)
        header = file_data[0]
        print(f'Header of {v} File is : {header}')

        # Get Primary Key
        pk = get_primary_key(header, v)
        print(f'Value of pk : {pk}')

        # Call function to create Sort File Name
        new_out_file = create_file_name(file)
        print(f'Value of new_out_file : {new_out_file}')

        # Call function to create Physical Sort File
        sort_file_out(pk, file_data, new_out_file)

compare_2_file()