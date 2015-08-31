#!/usr/bin/env python
from setuptools import setup, find_packages
import re
import os.path

install_requires = [
    "boto",
    "iso8601",
    "pyramid",
    "pyramid_beaker",
    "pyramid_whoauth",
    "pytz",
    "repoze.who",
    "simplejson",
    "waitress",
]

VERSION_REGEX = re.compile(r"""
    ^__version__\s=\s
    ['"](?P<version>.*?)['"]
""", re.MULTILINE | re.VERBOSE)

VERSION_FILE = os.path.join("cloudviz", "version.py")

def get_version():
    """Reads the version from the package"""
    with open(VERSION_FILE) as handle:
        lines = handle.read()
        result = VERSION_REGEX.search(lines)
        if result:
            return result.groupdict()["version"]
        else:
            raise ValueError("Unable to determine __version__")

setup(
    name='cloudviz',
    version=get_version(),
    description='Expose Amazon CloudWatch as a data source for Google Chart Tools.',
    author='Mike Babineau',
    author_email='michael.babineau@gmail.com',
    url='https://github.com/mbabineau/cloudviz',
    packages=find_packages(exclude=("tests", "tests.*", "ez_setup")),
    install_requires=install_requires,
    license="Apache Version 2.0",
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: Apache Software License",
    ],
    test_suite = 'nose.collector',
    entry_points="""
        [paste.app_factory]
        main=cloudviz:main
    """,
    include_package_data=True,
    zip_safe=False,
    dependency_links=[
    ],
)
