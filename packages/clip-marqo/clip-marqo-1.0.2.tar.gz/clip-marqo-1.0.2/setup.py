import os

import pkg_resources
from setuptools import setup, find_packages

setup(
    name="clip-marqo",
    py_modules=["clip"],
    version="1.0.2",
    description="",
    author="OpenAI",
    packages=find_packages(exclude=["tests*"]),
    install_requires=[
        'ftfy',
        'regex',
        'tqdm',
        'torch',
        'torchvision',
        ],
    include_package_data=True,
    extras_require={'dev': ['pytest']},
)
