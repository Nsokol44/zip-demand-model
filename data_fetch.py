#!/usr/bin/env python3
"""
data_fetch.py - ONE-TIME data acquisition for the ZIP demand model.

Run once:  python data_fetch.py
After that, `python run_all.py` works from the cached files in data/
alone (no network). Re-running data_fetch.py overwrites the cache.

Sources (all U.S. Census Bureau, www2.census.gov):
  * ACS 5-year 2023 table-based summary files - ZCTA rows (summary
    level 860). The Census API requires a personal key (verified
    2026-10-12), so - exactly as in
    ~/workspace/video-factory/pipeline/receptivity.py - the same
    published estimates are pulled from the official summary files.
  * 2023 ZCTA Gazetteer - centroids + land area.
  * Cartographic boundary files - states & counties (2023, 500k) for
    centroid-based region assignment; ZCTA polygons (2020, 500k) for
    maps. ZCTAs are a 2020-vintage geography, matching the polygons.
    ZCTA -> region assignment is by INTERNAL POINT (gazetteer
    centroid) falling inside the state/county polygon, with a
    nearest-polygon fallback for the handful of centroids that land
    in water; every fallback is counted and printed.

Outputs (data/):
  features.csv               one row per study ZCTA (see README)
  acs_zcta_raw.csv           raw ACS cells the features derive from
  geometry_nyc.parquet       ZCTA polygons, NYC metro subset
  geometry_southeast.parquet ZCTA polygons, Southeast subset
"""

import io
import os
import sys
import urllib.request
import zipfile

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config

USER_AGENT = "zip-demand-model/1.0 (urllib; ACS public data)"

SF_BASE = (
    "https://www2.census.gov/programs-surveys/acs/summary_file/"
    "2023/table-based-SF/data/5YRData"
)
# table -> {output field: summary-file column}
TABLE_COLUMNS = {
    "B01003": {"population": "B01003_E001"},
    "B01002": {"median_age": "B01002_E001"},
    "B19013": {"median_hh_income": "B19013_E001"},
    "B19001": {
        "hh_income_total": "B19001_E001",
        "hh_income_100_125": "B19001_E014",
        "hh_income_125_150": "B19001_E015",
        "hh_income_150_200": "B19001_E016",
        "hh_income_200_plus": "B19001_E017",
    },
    "B25001": {"housing_units": "B25001_E001"},
    "B25003": {
        "occupied_units": "B25003_E001",
        "owner_occupied": "B25003_E002",
        "renter_occupied": "B25003_E003",
    },
    "B25004": {"seasonal_vacant": "B25004_E006"},
    "B25024": {
        "units_in_structure": "B25024_E001",
        "units_1_detached": "B25024_E002",
        "units_1_attached": "B25024_E003",
        "units_20_49": "B25024_E008",
        "units_50_plus": "B25024_E009",
    },
    "B25010": {"avg_hh_size": "B25010_E001"},
}

GAZ_ZCTA_URL = (
    "https://www2.census.gov/geo/docs/maps-data/data/gazetteer/"
    "2023_Gazetteer/2023_Gaz_zcta_national.zip"
)
STATE_SHP_URL = ("https://www2.census.gov/geo/tiger/GENZ2023/shp/"
                 "cb_2023_us_state_500k.zip")
COUNTY_SHP_URL = ("https://www2.census.gov/geo/tiger/GENZ2023/shp/"
                  "cb_2023_us_county_500k.zip")
ZCTA_SHP_URL = ("https://www2.census.gov/geo/tiger/GENZ2020/shp/"
                "cb_2020_us_zcta520_500k.zip")


def fetch_bytes(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=600) as resp:
        return resp.read()


def parse_value(raw):
    """ACS cell -> float; blanks/sentinels -> NaN (as receptivity.py)."""
    if raw is None:
        return np.nan
    text = str(raw).strip()
    if text in ("", ".", "-", "(X)", "N", "null"):
        return np.nan
    try:
        value = float(text)
    except ValueError:
        return np.nan
    return np.nan if value <= -100000000 else value


def load_acs_table(table, columns):
    """Stream one summary file; keep ZCTA rows only (level 860)."""
    url = f"{SF_BASE}/acsdt5y2023-{table.lower()}.dat"
    print(f"  streaming {url}", flush=True)
    kept = {}
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=900) as resp:
        text = io.TextIOWrapper(resp, encoding="utf-8", newline="")
        header = text.readline().rstrip("\n").split("|")
        idx = {name: i for i, name in enumerate(header)}
        geo_i = idx["GEO_ID"]
        col_i = {field: idx[col] for field, col in columns.items()}
        for line in text:
            # ZCTA rows carry summary level 860 in the table-based
            # files with GEO_ID like "860Z200US00601" (Z200 = the
            # 2020 ZCTA vintage marker).
            if not line.startswith("860"):
                continue
            parts = line.rstrip("\n").split("|")
            if not parts[geo_i].startswith("860"):
                continue
            zcta = parts[geo_i][-5:]
            kept[zcta] = {f: parse_value(parts[i])
                          for f, i in col_i.items()}
    print(f"    {len(kept):,} ZCTAs", flush=True)
    return kept


def load_gazetteer():
    print("  fetching ZCTA gazetteer", flush=True)
    payload = fetch_bytes(GAZ_ZCTA_URL)
    with zipfile.ZipFile(io.BytesIO(payload)) as zf:
        member = [n for n in zf.namelist() if n.endswith(".txt")][0]
        with zf.open(member) as fh:
            df = pd.read_csv(fh, sep="\t", dtype={"GEOID": str})
    df.columns = [c.strip() for c in df.columns]
    return pd.DataFrame({
        "zcta": df["GEOID"].str.strip().str.zfill(5),
        "land_sqmi": df["ALAND_SQMI"],
        "lat": df["INTPTLAT"],
        "lon": df["INTPTLONG"],
    })


def load_shp(url):
    import geopandas as gpd
    print(f"  fetching {url.rsplit('/', 1)[-1]}", flush=True)
    return gpd.read_file(io.BytesIO(fetch_bytes(url)))


def assign_regions(df):
    """Centroid-in-polygon region assignment with nearest fallback."""
    import geopandas as gpd
    pts = gpd.GeoDataFrame(
        df[["zcta"]], geometry=gpd.points_from_xy(df["lon"], df["lat"]),
        crs="EPSG:4326")

    states = load_shp(STATE_SHP_URL)[["STUSPS", "geometry"]]
    counties = load_shp(COUNTY_SHP_URL)[["GEOID", "geometry"]]
    counties = counties.rename(columns={"GEOID": "county_fips"})

    sj = gpd.sjoin(pts, states, how="left", predicate="within")
    state_by_zcta = sj.groupby("zcta")["STUSPS"].first()
    cj = gpd.sjoin(pts, counties, how="left", predicate="within")
    county_by_zcta = cj.groupby("zcta")["county_fips"].first()

    n_state_fb = n_county_fb = 0
    miss = state_by_zcta[state_by_zcta.isna()].index
    if len(miss):
        near = gpd.sjoin_nearest(pts[pts["zcta"].isin(miss)], states,
                                 how="left", max_distance=0.35)
        fb = near.groupby("zcta")["STUSPS"].first()
        state_by_zcta.loc[fb.index] = fb
        n_state_fb = len(fb)
    miss = county_by_zcta[county_by_zcta.isna()].index
    if len(miss):
        near = gpd.sjoin_nearest(pts[pts["zcta"].isin(miss)], counties,
                                 how="left", max_distance=0.35)
        fb = near.groupby("zcta")["county_fips"].first()
        county_by_zcta.loc[fb.index] = fb
        n_county_fb = len(fb)
    print(f"  assignment fallbacks: state {n_state_fb}, "
          f"county {n_county_fb}", flush=True)

    df = df.copy()
    df["state"] = df["zcta"].map(state_by_zcta)
    df["county_fips"] = df["zcta"].map(county_by_zcta)

    def region_of(row):
        if row["county_fips"] in config.NYC_METRO_COUNTIES:
            return config.REGION_NYC
        if row["state"] in config.SOUTHEAST_STATES:
            return config.REGION_SOUTHEAST
        return None

    df["region"] = df.apply(region_of, axis=1)
    return df[df["region"].notna()].copy()


def build_features():
    print("== ACS summary files (ZCTA rows only) ==", flush=True)
    merged = None
    for table, columns in sorted(TABLE_COLUMNS.items()):
        part = pd.DataFrame(load_acs_table(table, columns)).T
        part.index.name = "zcta"
        merged = part if merged is None else merged.join(part, how="outer")
    merged = merged.reset_index()
    raw_path = os.path.join(config.DATA_DIR, "acs_zcta_raw.csv")
    merged.to_csv(raw_path, index=False)
    print(f"wrote {raw_path} ({len(merged):,} ZCTAs)", flush=True)

    print("== gazetteer + region assignment ==", flush=True)
    gaz = load_gazetteer()
    df = merged.merge(gaz, on="zcta", how="inner")
    print(f"  ACS x gazetteer: {len(df):,} ZCTAs", flush=True)
    study = assign_regions(df)

    study["households"] = study["occupied_units"]
    study["renter_share"] = (study["renter_occupied"] /
                             study["occupied_units"])
    study["seasonal_share"] = (study["seasonal_vacant"] /
                               study["housing_units"])
    inc_hi = study[["hh_income_100_125", "hh_income_125_150",
                    "hh_income_150_200", "hh_income_200_plus"]].sum(axis=1)
    study["share_income_100k"] = inc_hi / study["hh_income_total"]
    study["pct_single_family"] = (
        (study["units_1_detached"] + study["units_1_attached"]) /
        study["units_in_structure"])
    study["pct_large_building"] = (
        (study["units_20_49"] + study["units_50_plus"]) /
        study["units_in_structure"])
    study["pop_density"] = study["population"] / study["land_sqmi"]

    before = len(study)
    study = study[(study["population"] >= config.MIN_POPULATION) &
                  (study["households"] >= config.MIN_HOUSEHOLDS)]
    print(f"  size filter: {before:,} -> {len(study):,} ZCTAs", flush=True)
    for region, part in study.groupby("region"):
        print(f"  {region}: {len(part):,} ZCTAs", flush=True)

    cols = ["zcta", "region", "state", "county_fips", "lon", "lat",
            "land_sqmi", "population", "households", "housing_units",
            "median_hh_income", "share_income_100k", "renter_share",
            "seasonal_share", "pct_single_family", "pct_large_building",
            "avg_hh_size", "median_age", "pop_density"]
    features = study[cols].sort_values(["region", "zcta"])
    fpath = os.path.join(config.DATA_DIR, "features.csv")
    features.to_csv(fpath, index=False)
    print(f"wrote {fpath}", flush=True)
    return features


def cache_geometry(features):
    print("== ZCTA polygons (clipped to study regions) ==", flush=True)
    polys = load_shp(ZCTA_SHP_URL)
    polys = polys.rename(columns={"ZCTA5CE20": "zcta"})
    keep = set(features["zcta"])
    polys = polys[polys["zcta"].isin(keep)][["zcta", "geometry"]]
    region_map = dict(zip(features["zcta"], features["region"]))
    polys["region"] = polys["zcta"].map(region_map)
    for region, fname in ((config.REGION_NYC, "geometry_nyc.parquet"),
                          (config.REGION_SOUTHEAST,
                           "geometry_southeast.parquet")):
        sub = polys[polys["region"] == region].drop(columns=["region"])
        path = os.path.join(config.DATA_DIR, fname)
        sub.to_parquet(path)
        print(f"wrote {path} ({len(sub):,} polygons)", flush=True)


def main():
    os.makedirs(config.DATA_DIR, exist_ok=True)
    features = build_features()
    cache_geometry(features)
    print("data_fetch complete.", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
