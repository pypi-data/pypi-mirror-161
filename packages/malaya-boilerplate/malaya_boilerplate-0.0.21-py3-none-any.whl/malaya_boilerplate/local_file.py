import os
from pathlib import Path


def check_file(file):
    for key, item in file.items():
        if 'version' in key:
            continue
        if not os.path.isfile(item):
            return False
    return True
