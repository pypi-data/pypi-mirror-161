# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


__author__ = "Yu"
__version__ = "0.0.1"

setup(
      name='teem',
      version=__version__,
      description='teem: a powerful tensorizing toolkit based on Pytorch',
      author=__author__,
      maintainer=__author__,
      url='https://github.com/tnbar/teem',
      packages=find_packages(),
      py_modules=[],
      long_description="A powerful tensorizing toolkit based on Pytorch.",
      license="MIT",
      platforms=["any"],
      install_requires = []
)
