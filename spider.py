#!/usr/bin/env python3

import re
import os
import argparse
from typing import Generator
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

VERBOSE = False
DEFAULT_LEVEL = 5
LINK_ELEMENTS = {
    'src': [
        'frame',
        'iframe',
        'img',
        'embed',
        'audio',
        'input',
        'script',
        'source',
        'track',
        'video',
    ],
    'href': [
        'a',
        'link',
        'base',
        'area',
        'image',
    ],
    'action': [
        'form',
    ],
    'data': [
        'object',
    ],
    'codebase': [
        'applet',
        'object',
    ],
    'cite': [
        'blockquote',
        'del',
        'ins',
        'q',
    ],
    'background': [
        'body',
    ],
    'longdesc': [
        'frame',
        'iframe',
        'img',
    ],
    'profile': [
        'head',
    ],
    'usemap': [
        'img',
        'input',
        'object',
    ],
    'classid': [
        'object',
    ],
    'formaction': [
        'button',
        'input',
    ],
    'icon': [
        'command',
    ],
    'manifest': [
        'html',
    ],
    'poster': [
        'video',
    ],
}

def make_url(base: str, path: str) -> str:
    if path and path[0] == '/':
        return base + '/' + path
    elif path.startswith('http'):
        return path
    else:
        return base + '/' + path

def find_urls(base_url: str, text: str) -> Generator[str, None, None]:
    soup = BeautifulSoup(text, 'html.parser')
    domain = urlparse(base_url).netloc
    protocol = 'https' if base_url.startswith('https') else 'http'
    base = protocol + '://' + domain
    for attribute, elements in LINK_ELEMENTS.items():
        for element in elements:
            for link in soup.find_all(element, attrs={attribute: True}):
                yield make_url(base, link[attribute])
    for match in re.finditer(r'https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)', text):
        yield make_url(base, match.group(0))

def download_and_save(url: str, save_base_dir: str) -> None:
    dir, file = os.path.split(urlparse(url).path)
    domain = urlparse(url).netloc
    dest_dir = os.path.normpath(os.path.join(save_base_dir, os.path.join(domain, './' + dir)))
    if os.path.exists(dest_dir) and not os.path.isdir(dest_dir):
        print(f'File {dest_dir} already exists and is not a directory.', flush=True)
        raise SystemExit(1)
    if not os.path.exists(dest_dir):
        try:
            os.makedirs(dest_dir, exist_ok=True)
        except OSError:
            print(f'Failed to create dir {dest_dir}')
            raise SystemExit(1)
    dest_path = os.path.join(dest_dir, file)
    if os.path.exists(dest_path):
        print(f'Warning: file "{dest_path}" already exists, not downloading again', flush=True)
        return
    print(f'Downloading "{url}" to "{dest_path}"', flush=True)
    resp = requests.get(url)
    if resp.status_code != 200:
        return
    with open(dest_path, 'wb') as f:
        f.write(resp.content)

def crawl(url: str, level: int, save_base_dir: str) -> None:
    if VERBOSE:
        print(f'Crawling {url}')
    if level >= 0 and url.endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')):
        download_and_save(url, save_base_dir)
        return
    if level == 0:
        return
    resp = requests.get(url)
    if resp.status_code != 200:
        return
    text = resp.content.decode('utf-8', errors='ignore')
    for new_url in find_urls(url, text):
        crawl(new_url, level - 1, save_base_dir)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='spider',
        description='A simple DFS web crawler that downloads images from a URL',
        usage='%(prog)s [options] <url>'
    )
    parser.add_argument('url', help='The url to crawl')
    parser.add_argument('-r', '--recurse', action='store_true', help='Recursively download the images. Not specifing this option only tries to download the provided URL if it is an image')
    parser.add_argument('-l', '--level', type=int, help='Maximum recursion level')
    parser.add_argument('-p', '--path', default='./data', help='Path to directory where to download images to, default is ./data')
    parser.add_argument('-v', '--verbose', default=False, action='store_true', help='Print what is being done')
    args = parser.parse_args()
    url = args.url
    recurse = args.recurse
    path = args.path
    level = 0
    VERBOSE = args.verbose
    if args.recurse:
        if args.level:
            level = args.level
        else:
            level = DEFAULT_LEVEL
    elif args.level:
        print("Warning: -l/--level is ignored when not specifying -r/--recurse")
    if level < 0:
        print("Error: LEVEL must be at least 0")
        raise SystemExit(1)
    crawl(url, level, path)
