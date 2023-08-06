"""
setup.py
written in Python3
author: C. Lockhart <chris@lockhartlab.org>
"""

# import setuptools  # noqa
import numpy as np
from numpy.distutils.core import Extension, setup
from numpy.distutils.misc_util import Configuration
import os.path

# Read version
with open('version.yml', 'r') as f:
    data = f.read().splitlines()
version_dict = dict([element.split(': ') for element in data])

# Convert the version_data to a string
version = '.'.join([str(version_dict[key]) for key in ['major', 'minor']])
if version_dict['micro'] != 0:
    version += '.' + version_dict['micro']
print(version)

# Read in requirements.txt
with open('requirements.txt', 'r') as buffer:
    requirements = buffer.read().splitlines()

# Long description
with open('README.rst', 'r') as buffer:
    long_description = buffer.read()


# First make sure numpy is installed
# _setup(install_requires=['numpy'])

# Create configuration
def configuration(parent_package='', top_path=None):
    config = Configuration('iox', parent_package, top_path)
    # config.add_data_dir(('_include', 'pathetic/_include'))  # not sure why this wasn't working with manifest.in
    return config


# Then, install molecular
setup(
    # name='iox',
    version=version,
    author='C. Lockhart',
    author_email='chris@lockhartlab.org',
    description='a package for IO connections',
    long_description=long_description,
    url="https://www.lockhartlab.org",
    packages=[
        'iox',
    ],
    install_requires=requirements,
    # include_package_data=True,
    configuration=configuration,
    zip_safe=True,
)
