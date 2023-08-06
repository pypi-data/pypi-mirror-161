from setuptools import setup, find_packages


VERSION = "0.0.7"
DESCRIPTION = "A python library for the marketstack API"

def readme():
    with open("README.md") as f:
        return f.read()


setup(
    name="pymarketstack",
    version=VERSION,
    url="https://github.com/NoakPalander/pymarketstack",
    author="Noak Palander",
    author_email="noak.palander@protonmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=readme(),
    packages=find_packages(),
    install_requires=["aiohttp", "marshmallow", "dataclasses-json"],
    keywords=["python", "market", "stocks", "api", "marketstack"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: Apache Software License"
    ]
)
