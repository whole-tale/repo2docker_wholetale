#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

requirements = []

setup_requirements = ["pytest-runner"]

test_requirements = ["pytest"]

setup(
    author="Kacper Kowalik",
    author_email="xarthisius.kk@gmail.com",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    description="repo2docker plugin for WholeTale project.",
    install_requires=requirements,
    license="BSD license",
    long_description=readme + "\n\n" + history,
    include_package_data=True,
    keywords="repo2docker_wholetale",
    name="repo2docker_wholetale",
    packages=find_packages(),
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    url='https://github.com/whole-tale/repo2docker_wholetale',
    version='1.3.dev0',
    zip_safe=False,
    entry_points={
        "repo2docker.engines": [
            "dockercli = repo2docker_wholetale.dockercli:DockerCLIEngine"
        ]
    },
)
