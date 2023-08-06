# -*- coding: ascii -*-
 
 
"""setup.py: setuptools control."""
 
 
import re
from setuptools import setup
 
 
version = re.search(
    '^__version__\s*=\s*"(.*)"',
    open('Pragmatic/Pragmatic.py').read(),
    re.M
    ).group(1)
 
 
with open("README.md", "rb") as f:
    long_descr = f.read().decode("utf-8")
 
 
setup(
    name = "Pragmatic",
    packages = ["Pragmatic"],
    entry_points =
	{
        "console_scripts": ['Pragmatic = Pragmatic.Pragmatic:Main']
    },
    version = version,
    description = "Python command line application bare bones template.",
    long_description = long_descr,
    author = "Szoke Balazs",
    author_email = "bala.szoke@gmail.com",
    url = "https://github.com/QEDengine",
    )