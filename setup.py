# -*- coding: utf-8 -*-
from __future__ import division, absolute_import, print_function, unicode_literals

import io
from setuptools import setup, find_packages

with io.open('VERSION', 'r') as fd:
    VERSION = fd.read().rstrip()

requires = (
    'nextgisweb>=3.8.0.dev7',
    'geojson',
    'ply',
    'six',
)

entry_points = {
    'nextgisweb.packages': [
        'nextgisweb_mapserver = nextgisweb_mapserver:pkginfo',
    ],

    'nextgisweb.amd_packages': [
        'nextgisweb_mapserver = nextgisweb_mapserver:amd_packages',
    ],

}

setup(
    name='nextgisweb_mapserver',
    version=VERSION,
    description="",
    long_description="",
    classifiers=[],
    keywords='',
    author='',
    author_email='',
    url='',
    license='',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    python_requires=">=2.7.6, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, !=3.5.*, <4",
    install_requires=requires,
    entry_points=entry_points,
)
