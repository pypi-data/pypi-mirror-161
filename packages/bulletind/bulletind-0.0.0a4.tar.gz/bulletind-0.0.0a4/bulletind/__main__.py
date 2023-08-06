#!/usr/bin/python3
# Copyright (C) 2022 Jeff Epler <jepler@gmail.com>
# SPDX-FileCopyrightText: 2022 Jeff Epler
#
# SPDX-License-Identifier: GPL-3.0-only

"""Commandline interface to 'Bulletin D' data"""
import json
import pathlib

import click

from . import BulletinDInfo, get_bulletin_d_data, get_cached_bulletin_d_data


@click.command()
@click.option(
    "--cache-only/--no-cache-only",
    default=False,
    help="Only retrieve cached data files",
)
@click.option(
    "--update-package-data/--no-update-package-data",
    default=False,
    help="Update package data, not user cache",
)
def main(cache_only: bool, update_package_data: bool) -> None:
    """Download and show Bulletin D data in json format"""
    if update_package_data:
        get_bulletin_d_data([pathlib.Path(__file__).resolve().parent / "data"])
    else:
        if cache_only:
            data = get_cached_bulletin_d_data()
        else:
            data = get_bulletin_d_data()
        data = sorted(data, key=lambda x: x.number)
        json_data = BulletinDInfo.schema().dump(data, many=True)
        print(json.dumps(json_data, indent=4))


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
