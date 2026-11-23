#!/usr/bin/env python3
"""Build index.html and ats/index.html from cv_data.json with cvkit (https://github.com/noah-42/cvkit).

All settings (links, page head, section titles, contact) live in cv_data.json under "site".

Run either:
    uvx --from git+https://github.com/noah-42/cvkit cvkit build
    python3 build.py            (when cvkit is installed)
"""
import sys
from pathlib import Path

try:
    from cvkit.build import build
except ImportError:
    sys.exit("cvkit is not installed. Run: uvx --from git+https://github.com/noah-42/cvkit cvkit build")

for path in build(Path(__file__).parent):
    print(f"wrote {path}")
