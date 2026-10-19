"""run_v3.py — one-command rerun of the full v3 pass (2026-10-18 review fixes).

Order: full-data diagnostics -> Tier 2 across 24 draws -> roughness
test -> v3 figures -> manuscript v3 rebuild -> package v3 build.
"""
import subprocess, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
for step in ("diagnostics_full.py", "tier2_draws.py", "roughness.py",
             "figures_v3.py", "rebuild_manuscript_v3.py",
             "build_package_v3.py"):
    print("== " + step, flush=True)
    subprocess.run([sys.executable, os.path.join(HERE, step)], check=True)
print("v3 pass complete.")
