from setuptools import setup

APP_NAME = "django-bit-category"
VERSION = 0.1

setup(
    name=APP_NAME,
    version=VERSION,
    description='''Django category app which uses tree-like structure using bitwise primary key.
    Why's that? Because it is simple and blazingly fast!
    You can query a model with relation to all sub-nodes with
    `SomeModel.objects.filter(category_id__gte=category.gte, category_id__lt=category.lt)`
    ''',

    packages=[
        'bitcategory',
    ],

    author='Tomas Peterka',
    author_email='prestizni@gmail.com',
    license="GPL v3",
    url='http://pypi.python.org/pypi/{0}/'.format(APP_NAME),
    keywords="django category hierarchy",

    install_requires=[
        "django>=1.5",
    ],
)
