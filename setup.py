import io
from setuptools import setup, find_packages

with io.open('VERSION', 'r') as fd:
    VERSION = fd.read().rstrip()

requires = (
    'nextgisweb>=4.4.0.dev6',
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
    version=VERSION,
    description='MapServer renderer for NextGIS Web',
    author='NextGIS',
    author_email='info@nextgis.com',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.8,<4",
    install_requires=requires,
    entry_points=entry_points,
)
