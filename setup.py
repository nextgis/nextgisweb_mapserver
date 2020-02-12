from setuptools import setup, find_packages
import sys, os

version = '0.0'

requires = (
    'nextgisweb',
    'geojson',
    'ply',
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
    python_requires="<3",
    version=version,
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
    install_requires=requires,
    entry_points=entry_points,
)
