#!/usr/bin/env python

from setuptools import setup

setup(
    name='Rubra',
    version='0.1.0',
    author='Bernie Pope',
    author_email='bjpope@unimelb.edu.au',
    packages=['rubra'],
    package_data={'rubra': ['examples/*.py']},
    entry_points={
        'console_scripts': ['rubra = rubra.rubra:main']
    },
    url='https://github.com/bjpop/rubra',
    license='LICENSE.txt',
    description='Rubra is a pipeline system for bioinformatics workflows\
     with support for running pipeline stages on a distributed compute cluster.',
    long_description=open('README.txt').read(),
    install_requires=[
        "ruffus >= 2.0.0",
    ],
    classifiers=[
          'Development Status :: 4 - Beta',
          'License :: OSI Approved :: MIT',
          'Operating System :: POSIX',
          'Programming Language :: Python',
    ],

)
