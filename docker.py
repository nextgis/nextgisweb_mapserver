# -*- coding: utf-8 -*-
from __future__ import division, absolute_import, print_function, unicode_literals

from ngwdocker import PackageBase
from ngwdocker.base import AppImage


class Package(PackageBase):
    pass


@AppImage.on_apt.handler
def on_apt(event):
    if event.image.context.python3:
        # FIXME: run commands before `add-apt-repository --yes "ppa:nextgis/ppa"`
        event.command(
            'echo "deb https://rm.nextgis.com/api/repo/11/deb $(lsb_release -cs) main" | ' +
            'tee -a /etc/apt/sources.list')
        event.add_key('https://rm.nextgis.com/api/repo/11/deb/key.gpg')

    event.package('python3-mapscript' if event.image.context.python3 else 'python-mapscript')


@AppImage.on_package_files.handler
def on_package_files(event):
    if isinstance(event.package, Package):
        event.add(event.package.path / 'mapscript-to-env')


@AppImage.on_virtualenv.handler
def on_virtualenv(event):
    event.before_install(
        '$NGWROOT/package/nextgisweb_mapserver/mapscript-to-env ' +
        '$NGWROOT/env/bin/python ' +
        '/usr/bin/python3' if event.image.context.python3 else '/usr/bin/python')
