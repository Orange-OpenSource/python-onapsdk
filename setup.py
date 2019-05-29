#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0

from glob import glob
from os.path import basename
from os.path import splitext

from setuptools import find_packages
from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

version = {}
with open("src/onapsdk/version.py") as fp:
    exec(fp.read(), version)

setup(name='onapsdk',
      version=version['__version__'],
      description='SDK to use ONAP Programatically',
      long_description=readme(),
      url='https://gitlab.com/Orange-OpenSource/lfn/onap/python-onapsdk',
      author='Orange OpenSource',
      license='Apache 2.0',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
      include_package_data=True,
      install_requires=[
          'requests'
      ],
      setup_requires=["pytest-runner"],
      tests_require=[
        "mock",
        "pytest",
        "pytest-cov",
        "pytest-mock"],
      zip_safe=False)

