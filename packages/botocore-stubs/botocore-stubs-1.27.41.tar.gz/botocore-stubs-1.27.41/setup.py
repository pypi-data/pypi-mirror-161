"""
Setup script for botocore-stubs.
"""
from os.path import abspath, dirname

from setuptools import setup

LONG_DESCRIPTION = open(dirname(abspath(__file__)) + "/README.md", "r").read()


setup(
    name="botocore-stubs",
    version="1.27.41",
    packages=["botocore-stubs"],
    url="https://github.com/youtype/mypy_boto3_builder",
    license="MIT License",
    author="Vlad Emelianov",
    author_email="vlad.emelianov.nz@gmail.com",
    description="Type annotations for botocore 1.27.41 generated with mypy-boto3-builder 7.10.2",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Environment :: Console",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: Implementation :: CPython",
        "Typing :: Stubs Only",
    ],
    keywords="boto3 type-annotations botocore-stubs mypy typeshed autocomplete",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    package_data={"": ["LICENSE"], "botocore-stubs": ["py.typed", "*.pyi", "*/*.pyi"]},
    python_requires=">=3.7",
    project_urls={
        "Documentation": "https://youtype.github.io/boto3_stubs_docs/",
        "Source": "https://github.com/youtype/mypy_boto3_builder",
        "Tracker": "https://github.com/youtype/mypy_boto3_builder/issues",
    },
    install_requires=[
        "typing-extensions>=4.1.0",
    ],
    zip_safe=False,
)
