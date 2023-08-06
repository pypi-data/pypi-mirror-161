#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open("README.rst") as readme_file:
    readme = readme_file.read()
with open("HISTORY.rst") as history_file:
    history = history_file.read()
requirements = [
    "numpy>=1.21.6",
    "scikit-learn>=1.0.2",
    "setuptools>=60.2.0",
]
test_require = ["pandas>=1.3.0"]

extras = {
    "test": test_require
}

setup(
    author="Aleksandr Grefenstein",
    author_email="alexander.grefenshteyn@quantori.com",
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9"
    ],
    description="Batch effects removal for microbiome data via conditional quantile regression on Python",
    install_requires=requirements,
    extras_require=extras,
    tests_require=test_require,
    license="MIT license",
    long_description=readme + "\n\n" + history,
    include_package_data=True,
    keywords="conqur",
    name="conqur",
    packages=find_packages(include=["conqur", "conqur.*"]),
    url="https://github.com/quantori/conqur",
    version="1.0.0",
    zip_safe=False
)
