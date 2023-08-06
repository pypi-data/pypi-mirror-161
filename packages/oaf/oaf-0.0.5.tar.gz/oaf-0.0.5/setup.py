import os
import stat
import platform
import sys
import urllib.request
from setuptools import find_packages
from setuptools import setup

REPO = "old-ocean-creature/carvel-imgpkg"
VERSION = "v0.29.3-arc"
BIN_PATH = "./oaf/bin"

lib_folder = os.path.dirname(os.path.realpath(__file__))
requirement_path = lib_folder + "/requirements.txt"
install_requires = []  # Here we'll get: ["gunicorn", "docutils>=0.3", "lxml==0.5a7"]
if os.path.isfile(requirement_path):
    with open(requirement_path) as f:
        install_requires = f.read().splitlines()


def download():
    """Download imgpkg"""

    build = platform.platform()
    os_name = sys.platform
    print(f"downloading imgpkg for '{os_name}' '{build}'")

    asset_url = f"https://github.com/{REPO}/releases/download/{VERSION}"

    if os_name == "darwin":
        if "x86_64" in build:
            asset_url = f"{asset_url}/imgpkg-darwin-amd64"
        if "arm64" in build:
            asset_url = f"{asset_url}/imgpkg-darwin-arm64"
    elif os_name == "linux":
        if "x86_64" in build:
            asset_url = f"{asset_url}/imgpkg-linux-amd64"
        if "arm64" in build:
            asset_url = f"{asset_url}/imgpkg-linux-arm64"
    else:
        raise ValueError(f"os name not supported '{os_name}'")

    # download the url contents in binary format
    headers = {"Accept": "application/octet-stream"}
    print("asset_url: ", asset_url)
    req = urllib.request.Request(asset_url, headers=headers)
    r = urllib.request.urlopen(req)

    if not os.path.exists(BIN_PATH):
        os.mkdir(BIN_PATH)

    file_path = os.path.join(BIN_PATH, "imgpkg")
    with open(file_path, "wb") as code:
        code.write(r.read())

    st = os.stat(file_path)
    os.chmod(file_path, st.st_mode | stat.S_IEXEC)


download()

setup(
    name="oaf",
    version="0.0.5",
    url="https://github.com/old-ocean-creature/oaf",
    project_urls={
        "Documentation": "https://github.com/old-ocean-creature/oaf",
        "Code": "https://github.com/old-ocean-creature/oaf",
        "Issue tracker": "https://github.com/old-ocean-creature/oaf",
    },
    maintainer="Sole Ahab",
    description="Artifact storage using OCI registries",
    python_requires=">=3.6",
    install_requires=install_requires,
    packages=find_packages(include=("oaf", "oaf.*")),
    package_data={"oaf": ["bin/*"]},
)
