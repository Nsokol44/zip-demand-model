#!/usr/bin/env python3
"""
fetch_data.py — one-time download of the Tier 2 benchmark data.

All sources are free, public, and key-less:

  1. ZIP Code Business Patterns (ZBP) totals, 2022 and 2019
     U.S. Census Bureau, County Business Patterns datasets.
       https://www2.census.gov/programs-surveys/cbp/datasets/2022/zbp22totals.zip
       https://www2.census.gov/programs-surveys/cbp/datasets/2019/zbp19totals.zip
     Each zip holds one pipe-delimited text file with one row per ZIP:
     ZIP, ESTAB (total establishments), EMP, PAYANN, ... (totals file).

  2. IRS Statistics of Income (SOI) ZIP Code Data, tax year 2022
     "2022 (all States, includes AGI)" CSV linked from
     https://www.irs.gov/statistics/soi-tax-stats-individual-income-tax-statistics-2022-zip-code-data-soi
       https://www.irs.gov/pub/irs-soi/22zpallagi.csv
     One row per ZIP x AGI bracket (AGI_STUB); AGI_STUB = 1 is the total.
     N1 = number of returns; A00100 = adjusted gross income ($000s).

Files land in ../data/ relative to this script. Rerunning re-downloads
and overwrites; SHA-256 of each landed file is printed for the record.
"""

import hashlib
import os
import sys
import urllib.request
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")

SOURCES = [
    ("zbp22totals.zip",
     "https://www2.census.gov/programs-surveys/cbp/datasets/2022/"
     "zbp22totals.zip"),
    ("zbp19totals.zip",
     "https://www2.census.gov/programs-surveys/cbp/datasets/2019/"
     "zbp19totals.zip"),
    ("22zpallagi.csv",
     "https://www.irs.gov/pub/irs-soi/22zpallagi.csv"),
]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    os.makedirs(DATA, exist_ok=True)
    for name, url in SOURCES:
        dst = os.path.join(DATA, name)
        print(f"downloading {url}")
        req = urllib.request.Request(
            url, headers={"User-Agent": "Mozilla/5.0 (research fetch)"})
        with urllib.request.urlopen(req, timeout=300) as r, \
                open(dst, "wb") as fh:
            while True:
                chunk = r.read(1 << 20)
                if not chunk:
                    break
                fh.write(chunk)
        print(f"  -> {dst}  {os.path.getsize(dst):,} bytes  "
              f"sha256 {sha256(dst)[:16]}...")
    for name in ("zbp22totals.zip", "zbp19totals.zip"):
        zpath = os.path.join(DATA, name)
        with zipfile.ZipFile(zpath) as z:
            print(name, "contains:", z.namelist())
    return 0


if __name__ == "__main__":
    sys.exit(main())
