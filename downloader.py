import io

from PIL import Image
from bs4 import BeautifulSoup
import requests
import random
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


def img_gen(phrase, orientation='landscape', color=None):
    # Generator: Searches keywords from phrase in unsplash.com, yields an image
    a_results = get_links(get_soup(phrase + ' positive', orientation, color))
    url_list = parse_urls(a_results)

    while url_list:
        logging.info(f'{len(url_list)} image options left')
        selected = url_list[0]
        url_list.pop(0)
        response = requests.get(selected)

        if response.status_code < 299:
            logging.info(f'Response {response.status_code}, content size: {round(len(response.content)/1000000, 2)}mb')
            yield Image.open(io.BytesIO(response.content))

        else:
            logging.info(f'Downloading failed, moving to next url')


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


if __name__ == '__main__':
    assert nametize('Some Text') == 'some_text'
    assert nametize(' s0me MesSed t$xt') == 'sme_messed_txt'
    gen = img_gen(phrase='light play')
    while True:
        img = Image.open(next(gen))
        img.show()
        res = input('Load next image? (y/n) ')
        if res.lower() == 'y':
            continue
        else:
            break

