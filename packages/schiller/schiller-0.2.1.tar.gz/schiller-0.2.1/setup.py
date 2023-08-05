"""The setup.py file.

Allows installation via pip.
E.g., run `pip install .` to install this library.
"""
import configparser

import setuptools
import os

with open("./README.md") as f:
    long_description = f.read()


# Read config file
config_parser = configparser.ConfigParser()
config_parser.read("config.ini")
config = {
    k: v for config_sec in config_parser for k, v in config_parser[config_sec].items()
}


def _to_list(ini_el: str):
    if ini_el is None or ini_el.strip() == "":
        return []
    return [el.strip() for el in ini_el.split(",")]


version = config["version"]
description = config["description"]
package_name = config["package_name"]
py_version = config["py_version"]
py_min_version = config["py_min_version"]

extra_file_dirs = config.get("extra_file_dirs")
extra_file_dirs = _to_list(extra_file_dirs)


def package_files(directory):
    """Recursively collects all files."""
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join("..", path, filename))
    return paths


# Include files in other specified directories
extra_files = []
for d in extra_file_dirs:
    extra_files += package_files(f"{package_name}/{d}")

install_requires = _to_list(config.get("install_requires"))
setuptools.setup(
    name=package_name,
    version=version,
    description=description,
    packages=setuptools.find_packages(exclude=["docs", "tests"]),
    package_data={package_name: extra_files},
    url="https://schiller.ch",
    author="Schiller AG",
    author_email="your.name@schiller.ch",
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=f">={py_min_version}",
    install_requires=install_requires,
    classifiers=[
        "Programming Language :: Python",
        f"Programming Language :: Python :: {py_version}",
    ],
    entry_points={"console_scripts": [f"{package_name}={package_name}.__main__:main"]},
)
