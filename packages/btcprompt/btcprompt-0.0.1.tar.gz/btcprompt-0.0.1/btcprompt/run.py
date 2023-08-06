#!/usr/bin/env python3 

import time

import requests
from bs4 import BeautifulSoup

FILE_PATH = '/tmp/btcprompt'
time_interval = 30


def main():
    while True:
        r = requests.get('https://www.coingecko.com/en/coins/bitcoin')
        soup = BeautifulSoup(r.text, 'html.parser')
        price_label = soup.find('span', {'data-coin-symbol': 'btc'})
        price = price_label.text
        print(price)
        with open(FILE_PATH, 'w') as f:
            f.write(price)
        time.sleep(time_interval)


if __name__ == '__main__':
    main()
