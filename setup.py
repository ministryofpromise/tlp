import os
from setuptools import setup, find_packages
from pkg_resources import resource_filename, Requirement

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    with open(fname) as f:
        return f.read()

setup(
    name = "tlp",
    version = "0.1.1",
    author = "{ ministry of promise }",
    author_email = "adam.j.nichols@gmail.com",
    description = ("tlp is a python library that parses a body of text for indicators of compromise (iocs) "
                                   "using natural language processing modules to derive their context."),
    license = "MIT",
    keywords = "tlp threat language parser ioc nlp textblob nltk",
    url = "http://github.com/ministryofpromise/tlp",
    packages=find_packages(),
    package_dir={'tlp': 'tlp'},
    package_data={'tlp': ['lib/effective_tld_names.dat']},
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
    ],
    install_requires=[
        'nltk', 
        'textblob', 
        'python-Levenshtein',
        'numpy'
    ]
)
