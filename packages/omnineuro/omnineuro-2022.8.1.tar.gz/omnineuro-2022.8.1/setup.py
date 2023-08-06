#!/usr/bin/env python3
import os
import re
import sys
import site
import setuptools

from cmake_setuptools_ext import CMakeExtension, CMakeBuild

# get the project directory
PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))

# get the version from version.py file
with open(os.path.join(PROJECT_DIR, "omni", "version.py"), "r") as f:
    version = f.read().rstrip().split('"')[-2]
    # add dev version if in development mode
    if "develop" in sys.argv[1:]:
        version += ".dev1"

# get the CMakeLists.txt file
cmakelists = os.path.join(PROJECT_DIR, "CMakeLists.txt")

# This line enables user based installation when using pip in editable mode with the latest
# pyproject.toml config
site.ENABLE_USER_SITE = "--user" in sys.argv[1:]

# environment variable check for whether this is a readthedocs build
# this will disable the C++ extensions since the readthedocs environment
# will not have the necessary system libraries
READTHEDOCS = os.environ.get("READTHEDOCS", False) is not False

# get scripts path
SCRIPTSPATH = os.path.join(PROJECT_DIR, "omni", "scripts")


if __name__ == "__main__":
    # setup entry points scripts
    entry_points = {
        "console_scripts": [
            "omni_{0}=omni.scripts.{0}:main".format(f.split(".")[0])
            for f in os.listdir(SCRIPTSPATH)
            if not ("__pycache__" in f or "__init__.py" in f or "common" in f or ".DS_Store" in f)
        ]
    }

    # create setup options
    setup_options = {"entry_points": entry_points, "version": version}
    # if not an RTD build, include CMake extension
    if not READTHEDOCS:
        setup_options.update(
            {
                "ext_modules": [CMakeExtension("omni_cpp.omni", cmakelists)],
                "cmdclass": {"build_ext": CMakeBuild},
            }
        )

    # run setup
    setuptools.setup(**setup_options)
