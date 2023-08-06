import setuptools
#import wget
from setuptools import setup

with open('README.md') as f:
    long_description = f.read()


setuptools.setup(
    name="pyviewfactor",
    version="0.0.4",
    author="Mateusz BOGDAN, Edouard WALTHER, Marc ALECIAN, Mina CHAPON",
    description="A python library to calculate numerically exact radiation view factors between planar faces.",
    packages=["pyviewfactor"],
    long_description=long_description,
    long_description_content_type='text/markdown',  # This is important!
    url='https://gitlab.com/arep-dev/pyViewFactor/',
)