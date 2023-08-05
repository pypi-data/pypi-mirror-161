#!/usr/bin/env python3


import setuptools

import net_contextdiff


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="net-contextdiff",
    version=net_contextdiff.__version__,
    author="Robert Franklin",
    author_email="rcf34@cam.ac.uk",
    description="Compare network device configuration files using contextual structures",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.developers.cam.ac.uk/uis/netsys/udn/net-contextdiff",
    packages=setuptools.find_packages(),
    install_requires=[
        "deepops>=1.7.1",
        "netaddr",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
