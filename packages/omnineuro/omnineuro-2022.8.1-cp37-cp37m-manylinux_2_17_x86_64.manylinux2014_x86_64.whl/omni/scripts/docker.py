#!/usr/bin/env python3
import sys
import importlib
from os import listdir
from os.path import abspath, dirname, join

# get this directory
THIS_DIR = dirname(abspath(__file__))

# get list of scripts in directory
SCRIPTS = [
    f.split(".py")[0] for f in listdir(THIS_DIR) if f.endswith(".py") and "__init__.py" not in f and "docker" not in f
]


def main():
    # if no arguments, list the available scripts
    if len(sys.argv) == 1 or sys.argv[1] == "--help" or sys.argv[1] == "-h":
        print("Available scripts:")
        for script in SCRIPTS:
            print("  - {}".format(script))
        return 0

    # get the script name
    command = sys.argv[1]

    # check command is valid
    if command not in SCRIPTS:
        print("Invalid script: {}".format(command))
        print("See --help or -h for available scripts.")
        return 1

    # delete the first argument which is the omni_docker command
    sys.argv = sys.argv[1:]

    # run command
    importlib.import_module(f"omni.scripts.{command}").main()
