# -*- coding: utf-8 -*-
import os

from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, "README.rst")).read()

setup(
    name="kahn",
    version="0.0.1",
    author="Andreas Motl",
    author_email="andreas.motl@panodata.org",
    url="https://github.com/maritime-labs/kahn",
    description="A light-weight and energy-efficient NMEA message broker",
    long_description=README,
    download_url="https://pypi.org/project/kahn/",
    packages=find_packages(),
    include_package_data=True,
    package_data={},
    license="AGPL-3.0, EUPL-1.2",
    keywords=[
        "message",
        "broker",
        "opencpn",
        "signalk",
        "openplotter",
        "nmea",
        "nmea-0183",
        "sailing",
        "sensor",
    ],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "License :: OSI Approved :: European Union Public Licence 1.2 (EUPL 1.2)",
        "Development Status :: 2 - Pre-Alpha",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Natural Language :: English",
        "Intended Audience :: Customer Service",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Manufacturing",
        "Intended Audience :: Science/Research",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Telecommunications Industry",
        "Topic :: Communications",
        "Topic :: Education :: Testing",
        "Topic :: Software Development :: Libraries",
        "Topic :: Scientific/Engineering",
        "Topic :: System :: Emulators",
        "Topic :: System :: Networking",
        "Topic :: Utilities",
    ],
    entry_points={
        "console_scripts": [
            "kahn = kahn.cli:cli",
        ],
    },
    install_requires=[
        "pyserial<4",
        "pynmea2>1,<2",
        "click<9",
        "importlib_metadata;python_version<='3.7'",
    ],
    extras_require={
        "test": [
            "pytest<8",
            "pytest-cov<4",
            "mock-serial<1",
        ],
    },
)
