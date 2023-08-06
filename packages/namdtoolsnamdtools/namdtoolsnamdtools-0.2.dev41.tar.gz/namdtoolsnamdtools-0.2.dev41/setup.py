"""
setup.py
written in Python3
author: C. Lockhart <chris@lockhartlab.org>
"""

# from setuptools import setup
from Cython.Build import cythonize
import numpy as np
from numpy.distutils.core import Extension, setup
from numpy.distutils.misc_util import Configuration
import os.path


# Read version
with open('version.yml', 'r') as f:
    data = f.read().splitlines()
version_dict = dict([element.split(': ') for element in data])

# Convert the version_data to a string
version = '.'.join([str(version_dict[key]) for key in ['major', 'minor', 'micro']])

# Read in long description
with open('README.rst', 'r') as stream:
    long_description = stream.read()

# Read in requirements.txt
with open('requirements.txt', 'r') as stream:
    requirements = stream.read().splitlines()


# Create configuration
def configuration(parent_package='', top_path=None):
    config = Configuration('namdtools', parent_package, top_path)
    # config.add_data_dir(('_include', 'molecular/_include'))  # not sure why this wasn't working with manifest.in
    return config


# Setup
setup(
    name='namdtools',
    version=version,
    author='C. Lockhart',
    author_email='clockha2@gmu.edu',
    description='A Python interface to NAMD',
    long_description=long_description,
    # long_description_content_type='text/markdown',
    url="https://www.lockhartlab.org",
    packages=[
        'namdtools',
        'namdtools.analysis',
        'namdtools.core',
        'namdtools.io'
    ],
    install_requires=requirements,
    # install_requires=[
    #     'numpy',
    #     'pandas',
    # ],
    # include_package_data=True,
    configuration=configuration,
    zip_safe=True,
    ext_modules=cythonize([
        Extension(
            'namdtools.io._read_utils',
            sources=[os.path.join('namdtools', 'io', '_read_utils.pyx')],
            include_dirs=[np.get_include()]
        )
    ]),
)
