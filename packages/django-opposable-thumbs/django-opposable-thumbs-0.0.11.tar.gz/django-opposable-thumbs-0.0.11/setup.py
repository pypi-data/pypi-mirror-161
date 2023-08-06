# -*- coding: utf-8 -*-
from distutils.core import setup
from setuptools import find_packages

setup(
    name="django-opposable-thumbs",
    version="0.0.11",
    author=u"Jon Combe",
    author_email="pypi@joncombe.net",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["requests", "pillow"],
    url="https://github.com/joncombe/django-opposable-thumbs",
    license="BSD licence, see LICENCE file",
    description="Easy image manipulation for Django",
    long_description="Easy image manipulation for Django",
    zip_safe=False,
)
