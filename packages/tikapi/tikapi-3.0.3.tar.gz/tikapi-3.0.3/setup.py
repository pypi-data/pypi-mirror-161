#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

INSTALL_REQUIRES = [
   'requests',
]

setup(
    name='tikapi',
    version='3.0.3',
    description='TikAPI | TikTok Unofficial API',
    long_description_content_type="text/markdown",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    license='TikAPI',
    author='TikAPI',
    author_email='contact@tikapi.io',
    url='https://www.tikapi.io',
    keywords='tikapi, tiktok api, tiktok scraper, tiktok, TikTokApi',
    install_requires=INSTALL_REQUIRES,
    include_package_data=True,
    zip_safe=False,
	packages=find_packages(),
    py_modules=['tikapi'],
)