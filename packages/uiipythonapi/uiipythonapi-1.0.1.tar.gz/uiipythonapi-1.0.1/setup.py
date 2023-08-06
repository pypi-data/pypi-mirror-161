"""
Configuration for building the pip package
"""

import os
from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


def get_version(default :str ):
    """ retrieve version number from environment variable """
    version = os.getenv('RELEASE_TAG')
    if version is None:
        print("no version passed")
        return default

    print(version)
    version = version.replace("v", "")
    return version


setup(
    name='uiipythonapi',
    version=get_version("1.0.0"),
    url='https://github.com/virtomize/uii-python-api',
    author='Virtomize GmbH',
    author_email='api@virtomize.com',
    description="A client implementation for Virtomize Unattended Install Images API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='BSD 2-clause',
    packages=['uiipythonapi'],
    package_dir={'uiipythonapi': './uiipythonapi'},
    install_requires=[
        'requests'
    ],

    classifiers=[
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.8',
    ],
)
