#!/usr/bin/env python3

import owncloud

from broker.config import env
from broker.utils import print_tb


def share_list(oc):
    shareList = oc.list_open_remote_share()
    for i in range(len(shareList) - 1, -1, -1):
        input_folder_name = shareList[i]["name"]
        input_folder_name = input_folder_name[1:]  # removes '/' on the beginning
        input_id = shareList[i]["id"]
        owner = shareList[i]["owner"]
        if input_folder_name == "5c3c4018fbf2e1d1ef2555ede86cf626":
            print(shareList[i])
            print(owner)
            oc.accept_remote_share(int(input_id))
            print("here")

    # print(oc.file_info('/3a46cc092e8681212dac00d3564f5a64.tar.gz').attributes['{DAV:}getcontentlength'])
    # fn = '/17JFYbtys56cgrk2AF84qI52nAegTf9cW/17JFYbtys56cgrk2AF84qI52nAegTf9cW.tar.gz'
    # print(eudat.get_size(fn, oc))
    fn = "/5c3c4018fbf2e1d1ef2555ede86cf626/5c3c4018fbf2e1d1ef2555ede86cf626.tar.gz"
    # print(oc.file_info(fn))
    print(oc.file_info(fn).attributes)
    fn = "/5c3c4018fbf2e1d1ef2555ede86cf626"
    print(oc.file_info(fn).attributes)
    # oc.get_directory_as_zip(fn, 'alper.tar.gz')
    # oc.put_file('getShareList.py', 'getShareList.py')
    # print(oc.list('alper'))
    # print(oc.list('9a44346985f190a0af70a6ef6f0d35ee'))


def main():
    oc = owncloud.Client("https://b2drop.eudat.eu/")
    user = env.OC_USER
    with open(env.LOG_PATH.joinpath(".eudat_client.txt"), "r") as content_file:
        paswd = content_file.read().strip()

    try:
        oc.login(user, paswd)
        print(oc.list("."))
        oc.mkdir("alper")
    except Exception as e:
        print_tb(e)

    # share_list(oc)


if __name__ == "__main__":
    main()
