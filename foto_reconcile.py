from os import listdir, remove
from os.path import isfile, join
import time
import sys

import configparser

config = configparser.ConfigParser(interpolation=None)
config.sections()
config.read(['.env', 'config'])
IMAGE_DIR = config['DEFAULT'].get("imageDir")


def reconcile(file_names):
    if not file_names:
        print("file_names cannot be empty")
        return 0
    print("Begin local file reconciliation")
    total_deleted = 0
    tic = time.perf_counter()
    if file_names:
        for filename in listdir(IMAGE_DIR):
            file_with_path = join(IMAGE_DIR, filename)
            if isfile(file_with_path):
                if filename not in file_names:
                    remove(file_with_path)
                    total_deleted += 1
                    print(
                        "{} was found locally but not on server - deleted".format(file_with_path))
    toc = time.perf_counter()
    print(f"Deleted {total_deleted} files in {toc - tic:0.2f} seconds")

    return total_deleted


if __name__ == '__main__':
    reconcile(sys.argv[1:])
