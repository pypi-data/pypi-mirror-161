"""
Copyright (c) 2020 by Philipp Scheer. All Rights Reserved.
"""


import os
import setuptools


_ = os.path.dirname(os.path.realpath(__file__))


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open(_ + "/requirements.txt", "r", encoding="utf-16") as fh:
    requirements = [ line.strip() for line in fh.readlines() if not line.startswith("#") and not line.startswith("-e") ]


setuptools.setup(
    name="billyng",
    version=os.environ["BILLY_VERSION"],
    author="Philipp Scheer",
    author_email="hi@fipsi.at",
    description="Python SDK for the Billy microservice",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/f1ps1",
    packages=setuptools.find_packages(),
    install_requires=requirements,
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Topic :: Office/Business :: Financial",
        "Topic :: Office/Business :: Financial :: Accounting",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
    ],
    python_requires='>=3.6',
)
