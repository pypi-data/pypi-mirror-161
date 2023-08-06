#!/usr/bin/python3
"""Retrieve 'bulletin D' data"""

import datetime
import json
import os
import pathlib
import sys
import typing
import xml.etree.ElementTree
from dataclasses import dataclass, field

import bs4
import platformdirs
import requests
from dataclasses_json import DataClassJsonMixin, config
from marshmallow import fields

# Copyright (C) 2022 Jeff Epler <jepler@gmail.com>
# SPDX-FileCopyrightText: 2022 Jeff Epler
#
# SPDX-License-Identifier: GPL-3.0-only

BULLETIN_D_INDEX = "https://datacenter.iers.org/availableVersions.php?id=17"

DATA_PATHS = [
    platformdirs.user_cache_path(appname="bulletind"),
    pathlib.Path(__file__).resolve().parent / "data",
]


@dataclass
class BulletinDInfo(DataClassJsonMixin):
    """Type representing a Bulletin D dictionary"""

    date: datetime.date = field(
        metadata=config(
            encoder=datetime.date.isoformat,
            decoder=datetime.date.fromisoformat,
            mm_field=fields.DateTime(format="iso"),
        )
    )
    dut1: float
    dut1_unit: str
    number: int
    start_date: datetime.date = field(
        metadata=config(
            encoder=datetime.date.isoformat,
            decoder=datetime.date.fromisoformat,
            mm_field=fields.DateTime(format="iso"),
        )
    )
    start_utc: float


def cache(
    url: str, cache_paths: typing.Optional[list[pathlib.Path]] = None
) -> BulletinDInfo:
    """Download a specific Bulletin & cache it in json format"""
    base = url.split("/")[-1].split(".")[0]

    cache_paths = cache_paths or DATA_PATHS
    for path in cache_paths:
        loc = path / f"{base}.json"
        if loc.exists():
            with open(loc, "r", encoding="utf-8") as data_file:
                return BulletinDInfo.from_json(data_file.read())

    loc = cache_paths[0] / f"{base}.json"
    tmp_loc = cache_paths[0] / f"{base}.json.tmp"

    print(f"Fetching {url} to {loc}", file=sys.stderr)
    buld_xml = requests.get(url).text
    doc = xml.etree.ElementTree.XML(buld_xml)

    def find_el(element_name: str) -> xml.etree.ElementTree.Element:
        element = doc.find(f".//{{http://www.iers.org/2003/schema/iers}}{element_name}")
        assert element is not None
        return element

    def find(element_name: str) -> str:
        element = find_el(element_name)
        return element.text or ""

    def as_date(date_str: str) -> datetime.date:
        return datetime.date.fromisoformat(date_str)

    data = BulletinDInfo(
        date=as_date(find("date")),
        start_date=as_date(find("startDate")),
        start_utc=float(find("startUTC")),
        number=int(find("number")),
        dut1=float(find("DUT1")),
        dut1_unit=find_el("DUT1").attrib.get("unit", "s"),
    )

    with open(tmp_loc, "wt", encoding="utf-8") as data_file:
        print(data.to_json(indent=4), file=data_file)
        data_file.close()
        os.rename(tmp_loc, loc)
        print(data)
        return data


def get_bulletin_d_data(
    cache_paths: typing.Optional[list[pathlib.Path]] = None,
) -> list[BulletinDInfo]:
    """Download and return all available Bulletin D data"""
    for path in DATA_PATHS:
        os.makedirs(path, exist_ok=True)

    buld_text = requests.get(BULLETIN_D_INDEX).text
    buld_data = bs4.BeautifulSoup(buld_text, features="html.parser")
    refs = buld_data.findAll(lambda tag: "xml" in tag.get("href", ""))

    return [cache(r["href"], cache_paths) for r in refs]


def get_cached_bulletin_d_data() -> list[BulletinDInfo]:
    """Return all cached Bulletin D data"""

    def content(filename: pathlib.Path) -> BulletinDInfo:
        with open(filename, "r", encoding="utf-8") as data_file:
            return BulletinDInfo.from_json(data_file.read())

    return [content(p) for path in DATA_PATHS for p in path.glob("*.json")]
