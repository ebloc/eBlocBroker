#!/usr/bin/env python3

import json
import os
from contextlib import suppress

from broker._utils.tools import read_json
from broker.config import env


def add_item(data, key, item):
    data[key] = item


def remove_item(data, element):
    for item in list(data):
        if element in item:
            del data[element]


def main():
    fn = env.LOG_PATH + "/" + "caching_record.json"
    data = {}
    if os.path.isfile(fn):
        with suppress(Exception):
            data = read_json(fn)

    add_item(data, "jobKey", ["local", "userName", "timestamp", "keepTime"])
    add_item(data, "ipfs_hash", "timestamp")
    with open("data.json", "w") as outfile:
        json.dump(data, outfile)

    if "jobKey" in data:
        print(data["jobKey"][0])
        print(data["jobKey"])

    remove_item(data, "ipfs_hash")
    with open(fn, "w") as data_file:
        json.dump(data, data_file)


if __name__ == "__main__":
    main()
