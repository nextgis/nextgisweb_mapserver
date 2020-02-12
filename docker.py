from ngwdocker import PackageBase
from ngwdocker.base import AppImage

class Package(PackageBase):
    pass


@AppImage.on_apt.handler
def on_apt(event):
    event.package('python-mapscript')


@AppImage.on_package_files.handler
def on_package_files(event):
    if isinstance(event.package, Package):
        event.add(event.package.path / 'mapscript-to-env')


@AppImage.on_virtualenv.handler
def on_virtualenv(event):
    event.before_install(
        '$NGWROOT/package/nextgisweb_mapserver/mapscript-to-env ' +
        '$NGWROOT/env')
