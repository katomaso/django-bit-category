from setuptools import setup

APP_NAME = "django-bit-category"
VERSION = 0.2

setup(
    name=APP_NAME,
    version=VERSION,
    description="Django category app which uses tree-like structure using bitwise primary key.",

    packages=[
        'bitcategory',
    ],
    package_data={
        "": ["static/bitcategory/*"],
    },
    include_package_data=True,

    author='Tomas Peterka',
    author_email='prestizni@gmail.com',
    license="GPL v3",
    url='http://pypi.python.org/pypi/{0}/'.format(APP_NAME),
    keywords="django category hierarchy",

    install_requires=[
        "django>=1.5",
    ],
)
