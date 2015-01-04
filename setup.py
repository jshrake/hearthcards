#!/usr/bin/env python3

from setuptools import setup, find_packages
import os

setup(
    name='hearthcards',
    packages=['hearthcards'],
    entry_points={
        'console_scripts': ['hson=hearthcards.hson:main']
    },
    package_data={'hearthcards': [os.path.join('data', '*')]},
    include_package_data=True,
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
