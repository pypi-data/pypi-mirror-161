#!/usr/bin/env python
from setuptools import setup, find_packages

import tahoe_sites

description = 'Site and organization multi-tenancy management for Appsembler Tahoe'

setup(
    name='tahoe-sites',
    version=tahoe_sites.__version__,
    description=description,
    long_description=description,
    long_description_content_type="text/markdown",
    author='Appsembler',
    url='https://github.com/appsembler/tahoe-sites',
    classifiers=[
        'Framework :: Django',
        'Framework :: Django :: 2.2',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.8',
    ],
    packages=find_packages(exclude=['tests']),
    python_requires=">=3.5",
    entry_points={
        "lms.djangoapp": [
            "tahoe_sites = tahoe_sites.apps:TahoeSitesConfig",
        ],
        "cms.djangoapp": [
            "tahoe_sites = tahoe_sites.apps:TahoeSitesConfig",
        ],
    },
)
