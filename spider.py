#!/usr/bin/env python3

import re
import os
import sys
from typing import Generator
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

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
    dest_dir = os.path.normpath(os.path.join(save_base_dir, './' + dir))
    if os.path.exists(dest_dir) and not os.path.isdir(dest_dir):
        print(f'File {dest_dir} already exists and is not a directory.', file=sys.stderr, flush=True)
        raise SystemExit(1)
    if not os.path.exists(dest_dir):
        try:
            os.makedirs(dest_dir, exist_ok=True)
        except OSError:
            print(f'Failed to create dir {dest_dir}')
            raise SystemExit(1)
    print("Saving to", os.path.join(dest_dir, file))

def crawl(url: str, depth: int, save_base_dir: str = './data') -> None:
    if depth >= 0 and url.endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')):
        download_and_save(url, save_base_dir)
        return
    if depth == 0:
        return
    resp = requests.get(url)
    if resp.status_code != 200:
        return
    text = resp.content.decode('utf-8', errors='ignore')
    for new_url in find_urls(url, text):
        crawl(new_url, depth - 1, save_base_dir)

if __name__ == '__main__':
    url = 'https://rolandschmidt.de'
    depth = 2
    crawl(url, depth)
