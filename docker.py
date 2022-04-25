import ngwdocker
ngwdocker.require_version('>=2.0.0.dev7')

from ngwdocker import PackageBase
from ngwdocker.base import AppImage


python_bin = '/usr/bin/python3'


class Package(PackageBase):
    pass


@AppImage.on_apt.handler
def on_apt(event):
    event.package('cmake', 'swig', 'libfreetype6-dev', 'libgeos-dev', 'libproj-dev')
    msver = '7.6.4'

    event.pop()
    event.command(
        'cd /tmp',
        'curl -sSL https://download.osgeo.org/mapserver/mapserver-{0}.tar.gz > mapserver-{0}.tar.gz'.format(msver),
        'tar -zxf mapserver-{0}.tar.gz && rm mapserver-{0}.tar.gz'.format(msver),
        'mv mapserver-{0} mapserver && cd mapserver'.format(msver),
        'mkdir build && cd build',
        'cmake -DCMAKE_INSTALL_PREFIX=/usr/local ' +
            # Workaround: with dynamic linking _mapserver.so extension gets linked to build directory
            '-DCMAKE_POSITION_INDEPENDENT_CODE=ON -DLINK_STATIC_LIBMAPSERVER=ON ' + 
            '-DWITH_PROTOBUFC=OFF -DWITH_FRIBIDI=OFF -DWITH_HARFBUZZ=OFF -DWITH_CAIRO=OFF ' + 
            '-DWITH_FCGI=OFF -DWITH_POSTGIS=OFF -DWITH_WFS=OFF -DWITH_WCS=OFF -DWITH_LIBXML2=OFF ' +
            '-DWITH_PYTHON=ON -DPYTHON_EXECUTABLE={} ../ '.format(python_bin) +
            ' > ../configure.out.txt',
        'make && make install',
        '{} -m pip install mapscript/python'.format(python_bin),
        'cd / && rm -rf /tmp/mapserver',
    )


@AppImage.on_package_files.handler
def on_package_files(event):
    if isinstance(event.package, Package):
        event.add(event.package.path / 'mapscript-to-env')


@AppImage.on_virtualenv.handler
def on_virtualenv(event):
    event.before_install(
        '$NGWROOT/package/nextgisweb_mapserver/mapscript-to-env ' +
        '$NGWROOT/env/bin/python ' + python_bin)
