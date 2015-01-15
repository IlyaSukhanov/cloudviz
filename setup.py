#!/usr/bin/env python
from setuptools import setup, find_packages

install_requires = [
    "boto",
    "gviz-api-py",
    "pytz",
    "simplejson"
]

setup(
    name='cloudviz',
    version='0.1',
    description='Expose Amazon CloudWatch as a data source for Google Chart Tools.',
    author='Mike Babineau',
    author_email='michael.babineau@gmail.com',
    url='https://github.com/mbabineau/cloudviz',
    packages=find_packages(exclude=("tests", "tests.*")),
    install_requires=install_requires,
    license="Apache Version 2.0",
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: Apache Software License",
    ],
)
