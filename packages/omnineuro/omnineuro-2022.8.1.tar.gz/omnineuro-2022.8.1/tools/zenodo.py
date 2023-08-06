#!/usr/bin/env python3
from os.path import abspath, basename, dirname, join
import toml
import json
import sys
import requests

PROJECTDIR = dirname(abspath(dirname(__file__)))
pyproject_file = join(PROJECTDIR, "pyproject.toml")


# handle status
def handle_status(r: requests.Response):
    print("Status: %s" % r.status_code)
    if r.status_code >= 400:
        print(r.json())
        sys.exit(1)


# get the access token
if len(sys.argv) != 3:
    print("Usage: zenodo.py <access_token> <zip_file>")
    sys.exit(1)

# get the access token
ACCESS_TOKEN = sys.argv[1]
zip_file = sys.argv[2]
params = {"access_token": ACCESS_TOKEN}

# access api
print("Accessing zenodo API...")
r = requests.get(f"https://zenodo.org/api/deposit/depositions", params=params)
handle_status(r)

# ready new upload
print("Creating new upload...")
r = requests.post("https://zenodo.org/api/deposit/depositions", params=params, json={})
deposition_id = r.json()["id"]
handle_status(r)

# get bucket url
bucket_url = r.json()["links"]["bucket"]

# form file upload
print("Uploading file...")
with open(zip_file, "rb") as fp:
    r = requests.put(
        "%s/%s" % (bucket_url, basename(zip_file)),
        data=fp,
        params=params,
    )
handle_status(r)
print("\nFile Metadata:")
print(r.json())
print("")

# load the zenodo file
data = {"metadata": {}}
with open(join(PROJECTDIR, ".zenodo.json"), "r") as fp:
    data["metadata"] = json.load(fp)
# add the version
sys.path.append(PROJECTDIR)
from omni.version import __version__  # noqa: E402

data["metadata"]["version"] = __version__
# add description
config = toml.load(pyproject_file)
data["metadata"]["description"] = config["project"]["description"]

# add metadata to record
print("Adding metadata to record...")
r = requests.put(
    "https://zenodo.org/api/deposit/depositions/%s" % deposition_id,
    params=params,
    data=json.dumps(data),
    headers={"Content-Type": "application/json"},
)
handle_status(r)

# publish record
print("Publishing record...")
r = requests.post("https://zenodo.org/api/deposit/depositions/%s/actions/publish" % deposition_id, params=params)
handle_status(r)
