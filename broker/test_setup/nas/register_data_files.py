#!/usr/bin/env python3

from contextlib import suppress

from broker._utils._log import log, ok
from broker.eblocbroker_scripts.register_data import _register_data

hashes = [
    "f1de03edab51f281815c3c1e5ecb88c6",
    "03919732a417cb1d14049844b9de0f47",
    "983b9fe8a85b543dd5a4a75d031f1091",
    "f71df9d36cd519d80a3302114779741d",
    "b6aaf03752dc68d625fc57b451faa2bf",
    "c0fee5472f3c956ba759fd54f1fe843e",
    "63ffd1da6122e3fe9f63b1e7fcac1ff5",
    "9e8918ff9903e3314451bf2943296d31",
    "eaf488aea87a13a0bea5b83a41f3d49a",
    "e62593609805db0cd3a028194afb43b1",
    "3b0f75445e662dc87e28d60a5b13cd43",
    "ebe53bd498a9f6446cd77d9252a9847c",
    "f82aa511f8631bfc9a82fe6fa30f4b52",
    "082d2a71d86a64250f06be14c55ca27e",
    "f93b9a9f63447e0e086322b8416d4a39",
    "761691119cedfb9836a78a08742b14cc",
    "779745f315060d1bc0cd44b7266fb4da",
    "9d5d892a63b5758090258300a59eb389",
    "fa64e96bcee96dbc480a1495bddbf53c",
    "1bfca57fe54bc46ba948023f754521d6",
    "050e6cc8dd7e889bf7874689f1e1ead6",
    "0d6c3288ef71d89fb93734972d4eb903",
    "8f6faf6cfd245cae1b5feb11ae9eb3cf",
    "fe801973c5b22ef6861f2ea79dc1eb9c",
    "45281dfec4618e5d20570812dea38760",
    "dd0fbccccf7a198681ab838c67b68fbf",
    "4613abc322e8f2fdeae9a5dd10f17540",
]


def main():
    data_price = 1
    commitment_blk_dur = 600
    for code_hash in hashes:
        with suppress(Exception):
            _register_data(code_hash, data_price, commitment_blk_dur)

    log(f"## registering data {len(hashes)} files {ok()}")


if __name__ == "__main__":
    main()
