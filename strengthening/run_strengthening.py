#!/usr/bin/env python3
"""
run_strengthening.py — the one command that reproduces every
strengthening analysis and figure end to end:

    python fetch_data.py          # once: downloads the free Tier 2 data
    python run_strengthening.py   # benchmark + calibration + figures

Deterministic: the Tier 2 benchmark and all figure inputs use the
pipeline seed 20261013; calibration replicate r uses seed
20261013 + 1000*r (R = 24 replicates, B = 25 bootstrap worlds).
Dependencies: the pipeline's pinned requirements.txt
(the repo-root requirements.txt) plus, for the figures
only, mapclassify==2.11.0 and colorcet (installed 2026-10-18).
The Tier 1 pipeline modules in the repo root are imported
unmodified; nothing in the canonical CEUS package is touched.
"""

import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")


def run(script, force=False):
    marker = {"benchmark.py": "benchmark_results.json",
              "calibration.py": "calibration_results.json"}.get(script)
    if marker and not force and os.path.exists(
            os.path.join(ROOT, "results", marker)):
        print(f"[skip] {script} — {marker} exists (use --force)")
        return
    print(f"[run] {script}", flush=True)
    subprocess.run([sys.executable, os.path.join(HERE, script)],
                   check=True)


def main():
    force = "--force" in sys.argv
    run("benchmark.py", force)
    run("calibration.py", force)
    run("figures_strengthening.py", force=True)
    print("strengthening run complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
