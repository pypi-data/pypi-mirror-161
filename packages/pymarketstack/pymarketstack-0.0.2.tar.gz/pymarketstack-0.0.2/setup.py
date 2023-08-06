from setuptools import setup, find_packages
import codecs
import os

VERSION = "0.0.2"
DESCRIPTION = "A python library for the marketstack API"

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()


setup(
    name="pymarketstack",
    version=VERSION,
    author="Noak Palander",
    author_email="noak.palander@protonmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=["aiohttp", "marshmallow", "dataclasses-json"],
    keywords=["python", "market", "stocks", "api", "marketstack"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: Apache Software License"
    ]
)
