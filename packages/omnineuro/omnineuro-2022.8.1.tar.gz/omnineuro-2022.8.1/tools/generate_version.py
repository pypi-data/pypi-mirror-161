#!/usr/bin/env python3
from os.path import abspath, dirname, join
import datetime

# get project directory
PROJECT_DIR = dirname(dirname(abspath(__file__)))

today = datetime.date.today()
version = f'__version__ = "{today.year}.{today.month}.{today.day}"\n'
# write version to file
with open(join(PROJECT_DIR, "omni", "version.py"), "w") as f:
    f.write(version)
