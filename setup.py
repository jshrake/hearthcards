#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
    name="hearthcards",
    packages=find_packages(),
    scripts=['bin/hson'],
    package_data={'hearthcards': ['hearthcards/data/*']},
    version="0.0.1",
    description="Hearthstone card API",
    author="Justin Shrake",
    author_email="justinshrake@gmail.com",
    url="https://github.com/jshrake/hearthcards",
    download_url="https://github.com/jshrake/hearthcards",
    keywords=["hearthstone", "json", "simulation"],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ]
)
