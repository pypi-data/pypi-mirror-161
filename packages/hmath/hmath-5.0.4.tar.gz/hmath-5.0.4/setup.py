import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="hmath",
    version="5.0.4",
    author="caleb7023",
    description="hmath that can use advanced mathematical functions.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://caleb7023.hmath.pro/home",
    keywords=["hmath","math","python","caleb7023"],
    project_urls={
        "Bug Tracker": "https://github.com/caleb7023/hmath",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "hmath"},
    packages=setuptools.find_packages(where="hmath"),
    python_requires=">=3.0",
)

# Author: caleb7023
# Copyright (c)
# License: BSD 3 clause
