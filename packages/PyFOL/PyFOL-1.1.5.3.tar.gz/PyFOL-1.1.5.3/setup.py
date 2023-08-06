
import codecs
import os
import sys

try:
    from setuptools import setup
except:
    from distutils.core import setup

def read(fname):
    return codecs.open(os.path.join(os.path.dirname(__file__), fname)).read()



NAME = "PyFOL"

PACKAGES = ['pyfol']

DESCRIPTION = "A library that optimizes Python functions"

LONG_DESCRIPTION = read("README.rst")

KEYWORDS = "PyFOL python3 python py FOL"

AUTHOR = "AndyPomeloMars"

AUTHOR_EMAIL = "andypomelomars@163.com"

URL = "https://pypi.python.org/pypi/PyFOL"

VERSION = "1.1.5.3"

LICENSE = "GPL"

setup(
    name = NAME,
    version = VERSION,
    description = DESCRIPTION,
    long_description = LONG_DESCRIPTION,
    classifiers = [
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
    ],
    keywords = KEYWORDS,
    author = AUTHOR,
    author_email = AUTHOR_EMAIL,
    url = URL,
    license = LICENSE,
    packages = PACKAGES,
    python_requires='>=3.4',
    install_requires = [],
    include_package_data=True,
    zip_safe=True,
)
