import io
from setuptools import setup, find_packages

with io.open('VERSION', 'r') as fd:
    VERSION = fd.read().rstrip()

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
    version=VERSION,
    python_requires="<3",
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
