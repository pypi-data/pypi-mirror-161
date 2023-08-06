#! /usr/bin/env python

from setuptools import setup, find_packages

with open("README.md") as f:
    lines = f.read()
    first = lines.split('\n', 1)[0]
    vers = first.split(":")[1]

setup(name="xrequests",
      version=vers,
      description="A custom requesting module for projects made by vast",
      long_description_content_type="text/markdown",
      long_description=open("README.md", encoding="utf-8").read(),
      include_package_data=False,
      packages=find_packages(exclude=['tests']),
      author="vast#1337",
      url="http://pypi.python.org/pypi/xrequests",
      author_email="vastcord@proton.me",
      license="MIT",
      classifiers=[
          "Development Status :: 3 - Alpha",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: MIT License",
          "Natural Language :: English",
          "Programming Language :: Python",
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3.7",
          "Programming Language :: Python :: 3.8",
          "Programming Language :: Python :: 3.9",
          "Topic :: Scientific/Engineering",
          "Topic :: Scientific/Engineering :: Information Analysis",
          "Topic :: Scientific/Engineering :: Mathematics",
          "Topic :: Scientific/Engineering :: Visualization",
          "Topic :: Software Development :: Libraries",
          "Topic :: Utilities",
      ],

      python_requires="~=3.7",

      install_requires=[
          "platformdirs>=2.2.0",
          "dataclasses>=0.7;python_version<='3.7'",
          "typing_extensions>=4.0; python_version<'3.11'",
          "numpy>=1.6.0",
          "crypto>=1.4.1",
          "httpx>=0.23.0",
          "asyncio>=3.4.3",
          "datetime>=4.4",
          "confignation>=0.0.1"
      ]
)