#!/usr/bin/env python3

import os
import argparse
import datetime

from PIL import Image, ExifTags

def show_exif_data(file) -> None:
    with open(file, 'rb') as f:
        print(f'File:{file}')
        img = Image.open(f)
        img_exif = img.getexif()

        mtime = datetime.datetime.fromtimestamp(os.path.getmtime(file)).strftime('%B %d, %Y, %H:%M:%S')
        atime = datetime.datetime.fromtimestamp(os.path.getatime(file)).strftime('%B %d, %Y, %H:%M:%S')
        ctime = datetime.datetime.fromtimestamp(os.path.getctime(file)).strftime('%B %d, %Y, %H:%M:%S')
        print(f'Last Modified:{mtime}')
        print(f'Last Accessed:{atime}')
        print(f'Last Changed:{ctime}')
        if img_exif is None:
            print("No EXIF data")
        else:
            for key, val in img_exif.items():
                if key in ExifTags.TAGS:
                    print(f'{ExifTags.TAGS[key]}:{val}')
                else:
                    print(f'{key}:{val}')
            if not img_exif.items():
                print("No EXIF data")
        print()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='scorpion',
        description='A simple EXIT viewer for image files',
        usage='%(prog)s FILE1 [FILE2...]'
    )
    parser.add_argument('files', metavar="FILE1 [FILE2...]", type=str, nargs='+', help='List of image files to show EXIT data for, at least one is expected')
    args = parser.parse_args()
    for file in args.files:
        show_exif_data(file)
