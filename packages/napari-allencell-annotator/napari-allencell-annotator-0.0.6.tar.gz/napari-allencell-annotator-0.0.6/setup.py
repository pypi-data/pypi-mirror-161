#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import codecs
from setuptools import setup, find_packages


def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return codecs.open(file_path, encoding="utf-8").read()


requirements = [
    "napari>=0.4.9",
    "napari-plugin-engine>=0.1.4",
    "numpy",
    "aicssegmentation ~= 0.4.1",
    "magicgui >= 0.2.9",
    "aicsimageio >= 4.0.5",
    "PyQt5",
]

test_requirements = [
    "black>=19.10b0",
    "codecov>=2.0.22",
    "docutils>=0.10,<0.16",
    "flake8>=3.7.7",
    "psutil>=5.7.0",
    "pytest>=4.3.0",
    "pytest-cov==2.6.1",
    "pytest-raises>=0.10",
    "pytest-qt>=3.3.0",
    "quilt3>=3.1.12",
]

dev_requirements = [
    "black>=19.10b0",
    "bumpversion>=0.5.3",
    "docutils>=0.10,<0.16",
    "flake8>=3.7.7",
    "gitchangelog>=3.0.4",
    "ipython>=7.5.0",
    "m2r>=0.2.1",
    "pytest>=4.3.0",
    "pytest-cov==2.6.1",
    "pytest-raises>=0.10",
    "pytest-runner>=4.4",
    "pytest-qt>=3.3.0",
    "quilt3>=3.1.12",
    "Sphinx>=2.0.0b1,<3",
    "sphinx_rtd_theme>=0.1.2",
    "tox>=3.5.2",
    "twine>=1.13.0",
    "wheel>=0.33.1",
]

setup_requirements = [
    "pytest-runner",
]

extra_requirements = {
    "test": test_requirements,
    "dev": dev_requirements,
    "setup": setup_requirements,
    "all": [
        *requirements,
        *test_requirements,
        *setup_requirements,
        *dev_requirements,
    ],
}


# https://github.com/pypa/setuptools_scm
use_scm = {"write_to": "napari_allencell_annotator/_version.py"}

setup(
    name="napari-allencell-annotator",
    author="Allen Institute for Cell Science",
    url="https://github.com/aics-int/napari-allencell-annotator/",
    description="A plugin that enables annotations provided by Allen Institute for Cell Science",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=requirements,
    setup_requires=setup_requirements,
    test_suite="napari_allencell_annotator/_tests",
    tests_require=test_requirements,
    extras_require=extra_requirements,
    include_package_data=True,
    classifiers=[
        "Intended Audience :: Science/Research",
        "Framework :: napari",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: BSD License",
    ],
    # Do not edit this string manually, always use bumpversion
    # Details in CONTRIBUTING.rst
    version="0.0.6",
    zip_safe=False,
)
