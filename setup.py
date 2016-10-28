# coding: utf-8

import os
import io
from setuptools import setup

APP_NAME = "django-bit-category"
VERSION = "0.5.2"


def _read(filename):
    abspath = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    with io.open(abspath, "rt") as fx:
        return fx.read().strip()


setup(
    name=APP_NAME,
    version=VERSION,
    description="Django category app with bitwise tree-like structure of primary key.",
    long_description=_read("README.rst"),

    packages=['bitcategory', ],
    package_data={
        "": ["static/bitcategory/*"],
    },
    include_package_data=True,

    author='Tomas Peterka',
    author_email='prestizni@gmail.com',
    license="GPL v3",
    url='http://pypi.python.org/pypi/{0}/'.format(APP_NAME),
    keywords="django category hierarchy",

    install_requires=_read("requirements.txt").split("\n"),
)
