#!/usr/bin/env python3.12

import requests
import sys
import time
from bs4 import BeautifulSoup # type: ignore

def to_dict(lst):
    result = {}
    for line in lst:
        parts = line.split()
        name_parts = []
        values = []
        for part in parts:
            cleaned_part = part.replace(",", "").replace("-", "")
            if cleaned_part.isdigit():
                values.append(part)
            else:
                name_parts.append(part)
        metric_name = ' '.join(name_parts).capitalize()
        values.insert(0, metric_name)
        if metric_name:
            result[metric_name] = tuple(values)
    return result

def parser(url, headers):
    response = requests.get(url, headers=headers)
    bs = BeautifulSoup(response.text, "lxml")
    data = bs.find("div", "tableBody yf-9ft13").text
    data_lst = data.strip().split('   ')
    data_dict = to_dict(data_lst)
    return data_dict

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("need 2 arguments: ticker and row(yahoo finance financials)")
        sys.exit(0)
    try:
        url = f'https://finance.yahoo.com/quote/{sys.argv[1].capitalize()}/financials'
        headers = {'User-Agent': 'Mozilla/5.0'}

        result = parser(url, headers)
        time.sleep(5)
        try:
            print(result[sys.argv[2].capitalize()])
        except KeyError:
            print("has no this row in table")
            sys.exit(0)
    except Exception as e:
        print("has no this ticker")
        sys.exit(0)