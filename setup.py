from setuptools import setup, find_packages
import sys, os

version = '0.0'

requires = (
    'nextgisweb',
    'mapscript',
    'geojson',
)

entry_points = {
    'nextgisweb.component': ['nextgisweb_mapserver = nextgisweb_mapserver', ],
    'nextgisweb.amd_packages': [ 'nextgisweb_mapserver = nextgisweb_mapserver:amd_packages', ],
}

setup(
    name='nextgisweb_mapserver',
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
