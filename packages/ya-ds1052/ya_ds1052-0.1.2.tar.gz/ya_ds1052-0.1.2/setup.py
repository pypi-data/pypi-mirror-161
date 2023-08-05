#!/usr/bin/env python

from pathlib import Path
from setuptools import find_packages, setup

here = Path(__file__).parent.resolve()
readme = (here / 'README.md').read_text(encoding='utf-8')
changelog = (here / 'Changelog.md').read_text(encoding='utf-8')
long_description = readme + '\n' + changelog

setup(
    name='ya_ds1052',
    description='Remote control of Rigol DS1000E/D oscilloscopes',
    long_description=long_description,
    long_description_content_type="text/markdown",
    version='0.1.2',
    url='https://gitlab.com/adeuring/ya_ds1052',
    author='Abel Deuring',
    author_email='adeuring@gmx.net',
    license='GPL3',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU General Public License v3 or later '
            '(GPLv3+)',
        'Topic :: System :: Hardware :: Hardware Drivers',
        ],
    packages = find_packages(),
    package_data={'ds1052': ['Changelog.md']},
    test_suite='ds1052.tests',
    install_requires=[
        'aenum',
        'numpy',
    ],
    license_files=['LICENSE.txt'],
    )
