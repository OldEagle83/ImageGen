from bs4 import BeautifulSoup
import requests
import re
import random
import time
import os
import logging
import string


logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')


def get_ua():
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
    'User-Agent': f'{get_ua()}'
    }


def get_soup(search: str, orientation: str, color=None) -> BeautifulSoup:
    """
    Builds soup for unsplash
    :param search: the search parameter for images
    :param orientation: orientation: ['landscape', 'portrait', 'square']
    :return: Soup if valid, else False
    """
    if orientation not in ['landscape', 'portrait', 'square']:
        orientation = 'landscape'
    url = f"https://unsplash.com/s/photos/{search}"
    if orientation:
        url += f'?orientation={orientation}'
    if color:
        url += f'?color={color}'
    req = requests.get(url, headers)
    soup = BeautifulSoup(req.content, 'html.parser')
    return soup


def get_links(s) -> list:
    # Returns all a tags from a soup (s)
    if s:
        results = s.findAll("a")
    else:
        return False
    return results


def parse_urls(a: list) -> list:
    """
    Returns all urls in a list. Accepts a soup findall(a) result
    :param a: soup.findall(a) result
    :return: urls
    """
    urls = []
    for res in a:
        try:
            if res['title'] == "Download photo":
                urls.append(res["href"])
        except KeyError:
            continue
    logging.info(f'Found {len(urls)} links')
    return urls


def download_from_list(url_list: list, folder: str):
    """
    Downloads every file in url_list to folder
    :param url_list: list of urls to download
    :param folder: folder to download to
    :return:
    """
    counter = 0
    logging.debug(f'Downloading {len(url_list)} files to {folder}')

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


def create_dir(name: str):
    """
    Creates a subdirectory (if it doesn't exist) in img/ directory
    :param name: folder name (proofed)
    :return:
    """
    cwd = os.getcwd()
    try:
        os.mkdir(cwd + '/img/' + name)
    except OSError:
        print(f'Directory {name} exists, moving on.')


def nametize(text: str) -> str:
    """
    Replaces all spaces with underscore and turns letters to lowercase, ignores all other characters
    :param text: short text
    :return: snakecase of text
    """
    result = ''
    for i, char in enumerate(text):
        if char == ' ' and 0 < i < len(text) - 1:
            result += '_'
        elif char.lower() in string.ascii_lowercase:
            result += char.lower()

    return result


def download(phrase: str, limit: int, orientation='landscape', color=None) -> str:
    """
    Downloads [limit] pictures from Unsplash, landscape orientation, returns dir path. Will skip if directory exists
    :param orientation: orientation of pictures to download
    :param phrase: phrase to search for
    :param limit: how many files to download
    :return: destination folder (relative path)
    """

    folder = nametize(phrase)

    if not os.path.exists(f'img/{folder}'):
        create_dir(folder)
        a_results = get_links(get_soup(phrase + ' faceless textless', orientation, color))
        download_from_list(parse_urls(a_results)[:limit], folder)

    return f'img/{folder}'


if __name__ == '__main__':
    assert nametize('Some Text') == 'some_text'
    assert nametize(' s0me MesSed t$xt') == 'sme_messed_txt'

