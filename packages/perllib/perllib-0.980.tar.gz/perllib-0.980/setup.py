#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [ ]

test_requirements = ['pytest>=3', ]

setup(
    author="Joe Cool",
    author_email='snoopyjc@gmail.com',
    python_requires='>=3.8',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Artistic License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    description="Library functions to support pythonizer",
    install_requires=requirements,
    license="Artistic License 2.0 - The Perl Foundation",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='perllib',
    name='perllib',
    packages=find_packages(include=['perllib', 'perllib.*', 'charnames', 'Config', 'Sys', 'Sys.*', 'Math', 'Math.*', 'File', 'File.*']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/snoopyjc/pythonizer',
    version='0.980',
    zip_safe=False,
)
