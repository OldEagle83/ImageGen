from bs4 import BeautifulSoup
import requests
import re
import random
import time
import os
import logging


logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

def GET_UA():
    uastrings = [
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36", \
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.72 Safari/537.36", \
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10) AppleWebKit/600.1.25 (KHTML, like Gecko) Version/8.0 Safari/600.1.25", \
        "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:33.0) Gecko/20100101 Firefox/33.0", \
        "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36", \
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36", \
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/600.1.17 (KHTML, like Gecko) Version/7.1 Safari/537.85.10", \
        "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko", \
        "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:33.0) Gecko/20100101 Firefox/33.0", \
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.104 Safari/537.36" \
        ]

    return random.choice(uastrings)


headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Max-Age': '3600',
    'User-Agent': f'{GET_UA()}'
    }


def get_soup(search, orientation):
    """
    Builds soup for unsplash
    :param search: the search parameter for images
    :param orientation: orientation: ['landscape', 'portrait', 'square']
    :return: Soup if valid, else False
    """
    if orientation not in ['landscape', 'portrait', 'square']:
        return False
    url = f"https://unsplash.com/s/photos/{search}?orientation={orientation}"
    req = requests.get(url, headers)
    soup = BeautifulSoup(req.content, 'html.parser')
    return soup


def get_links(s):
    # Returns all a tags from a soup (s)
    results = s.findAll("a")
    return results


def parse_urls(a):
    # Returns all urls in a list. Accepts a soup findall(a) result
    urls = []
    for res in a:
        try:
            if res['title'] == "Download photo":
                urls.append(res["href"])
        except KeyError:
            continue
    logging.info(f'Found {len(urls)} links')
    return urls


def download_from_list(url_list, folder):
    counter = 0
    folder = nametize(folder)
    for url in url_list:
        for match in re.finditer(r'ixid=([a-zA-Z0-9]+)&', url, re.MULTILINE):
            f_name = match.group(1)
        response = requests.get(url)
        if response.status_code < 299:
            path = f'img/{folder}/{f_name}.jpg'
            with open(path, 'wb') as fp:
                fp.write(response.content)
            counter += 1
            print('.', end='')
        else:
            print('f', end='')
        time.sleep(random.randint(2, 5))
    print('Done')
    logging.info(f'Saved {counter} in img/{folder}')


def create_dir(name):
    # Creates a subdirectory (if it doesn't exist) in img/ directory
    name = nametize(name)
    cwd = os.getcwd()
    try:
        os.mkdir(cwd + '/img/' + name)
    except OSError:
        print(f'Directory {name} exists, moving on.')

def nametize(text):
    # Replaces all spaces with underscore
    if ' ' in text:
        text = text.replace(' ', '_').lower()
    return text

def download(phrase):
    # Downloads 16 pictures from Unsplash, landscape orientation, returns dir path
    folder = nametize(phrase)
    if not os.path.exists(f'/img/{folder}'):
        create_dir(folder)
        a_results = get_links(get_soup(phrase + ' faceless textless', 'landscape'))
        download_from_list(parse_urls(a_results), folder)
    return f'/img/{folder}'

if __name__ == '__main__':
    pass
    # search_field = input('What do you want to download from unsplash?')
    # orientation = input('What orientation of pics? Landscape/Portrait/Square')
    #
    # create_dir(search_field)


