#!/usr/bin/env python3

import sys

from config import env
from lib import check_linked_data
from utils import _colorize_traceback

if __name__ == "__main__":
    path_from = f"{env.HOME}/test_eblocbroker/datasets/"
    link_path_to = f"{env.LINKS}/datasets/BL06-camel-sml/"

    try:
        check_linked_data(path_from, link_path_to, is_continue=True)
    except:
        _colorize_traceback()

    sys.exit(0)
