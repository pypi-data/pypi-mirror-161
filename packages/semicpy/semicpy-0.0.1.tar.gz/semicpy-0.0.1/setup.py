import setuptools
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="semicpy",
    version="0.0.1",
    author="Nithin Kumar Santha Kumar",
    author_email="nxs169230@utdallas.edu",
    description="Semiconductor physics calculation and modeling",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nkskumar/semic",
    project_urls={
        "Bug Tracker": "https://github.com/nkskumar/semic/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    package_dir={'':"semicpy"},
    packages=find_packages("semicpy"),
    python_requires=">=3.5",
)