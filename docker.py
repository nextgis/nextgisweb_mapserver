# -*- coding: utf-8 -*-
from ngwdocker import PackageBase
from ngwdocker.base import AppImage


class Package(PackageBase):
    pass


@AppImage.on_apt.handler
def on_apt(event):
    image = event.image

    event.package('cmake', 'swig', 'libfreetype6-dev', 'libgeos-dev')
    python = '/usr/bin/python3' if image.context.python3 else '/usr/bin/python2'
    msver = '7.6.1'

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
            '-DWITH_PYTHON=ON -DPYTHON_EXECUTABLE={} ../ '.format(python) +
            ' > ../configure.out.txt',
        'make && make install',
        'cd / && rm -rf /tmp/mapserver',
    )



@AppImage.on_package_files.handler
def on_package_files(event):
    if isinstance(event.package, Package):
        event.add(event.package.path / 'mapscript-to-env')


@AppImage.on_virtualenv.handler
def on_virtualenv(event):
    python_bin = '/usr/bin/python3' if event.image.context.python3 else '/usr/bin/python'
    event.before_install(
        '$NGWROOT/package/nextgisweb_mapserver/mapscript-to-env ' +
        '$NGWROOT/env/bin/python ' + python_bin)
