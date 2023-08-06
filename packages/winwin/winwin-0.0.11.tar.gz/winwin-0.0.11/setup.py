# -*- coding: utf-8 -*-
# @Time    : 2021-07-30 20:14
# @Author  : zbmain
import os

import setuptools

here = os.path.dirname(__file__)

with open("README.md", "r") as fh:
    long_description = fh.read()


def parse_requirements(fname):
    with open(file=fname, mode='r', encoding="utf-8-sig") as f:
        requirements = f.readlines()
    return requirements


here and os.chdir(here)

setuptools.setup(
    name='winwin',
    version='0.0.11',
    packages=setuptools.find_packages(
        where='.',
        exclude=('.cache', 'tests*', 'build*', '*.egg*', 'dist*')
    ),
    package_dir={'winwin': 'winwin'},
    url='https://pypi.org/project/winwin/',
    license='Apache 2.0',
    author='zhaobin',
    author_email='zhaobin@banmahui.cn',
    description='',
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=['python-dotenv', 'oss2', 'redis', 'pymysql', 'openpyxl', 'pyodps', 'psycopg2-binary'],
    python_requires='>=3.7',
    classifiers=[
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
    ],
    # .egg
    zip_safe=True
)
