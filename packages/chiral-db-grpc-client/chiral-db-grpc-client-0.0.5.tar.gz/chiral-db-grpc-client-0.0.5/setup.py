# coding:utf8
from setuptools import setup, find_packages

from chiral_db_grpc_client import version

setup(
    name="chiral-db-grpc-client",
    version=version,
    description="ChiralDB gRPC Client in Python",
    long_description=open("README.md", encoding="utf8").read(),
    long_description_content_type="text/markdown",
    author="Qin Wan",
    author_email="rogerwq@gmail.com",
    url="https://github.com/chiral-data/chiral-db-grpc-client",
    packages=find_packages(),
    install_requires=[
    ],
    license="MIT",
    # https://pypi.org/classifiers/
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords=[],
)
