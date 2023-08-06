import majiang
from setuptools import setup, find_packages

setup(
    name = 'python-majiang',
    version = majiang.__version__,
    author = majiang.__author__,
    author_email = majiang.__email__,
    description = 'A library for MCR(Mahjong Competition Rules) game log generation.',
    license = 'MIT',
    keywords = 'majiang mahjong mcr',
    url = 'https://github.com/otobear/python-majiang',
    packages = find_packages(),
)
