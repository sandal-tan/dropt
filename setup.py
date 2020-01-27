"""Setup for Dr. Opt"""

from setuptools import find_packages, setup

VERSION: str = '0.0.1'

setup(
    name='dropt',
    version=VERSION,
    description='Dynamic and programmatic docopt generation',
    url='https://github.com/sandal-tan/dropt',
    packages=find_packages(),
)
