import ngwdocker

ngwdocker.require_version(">=2.0.0.dev7")

from ngwdocker import PackageBase
from ngwdocker.base import AppImage


class Package(PackageBase):
    pass


@AppImage.on_apt.handler
def on_apt(event):
    event.package(
        "cmake",
        "swig",
        "libfreetype6-dev",
        "libgeos-dev",
        "libproj-dev",
    )


@AppImage.on_virtualenv.handler
def on_virtualenv(event):
    version = "8.4.0"
    archive = "mapserver-{0}.tar.gz".format(version)
    event.before_install(
        "( : ",
        "    cd /tmp",
        "    curl -sSL https://download.osgeo.org/mapserver/{0} > {0}".format(archive),
        "    tar -zxf {0} && rm {0}".format(archive),
        "    mv mapserver-{0} mapserver && cd mapserver".format(version),
        "    mkdir build && cd build",
        "    cmake -DCMAKE_POSITION_INDEPENDENT_CODE=ON -DLINK_STATIC_LIBMAPSERVER=ON "
        + "-DWITH_PROTOBUFC=OFF -DWITH_FRIBIDI=OFF -DWITH_HARFBUZZ=OFF -DWITH_CAIRO=OFF "
        + "-DWITH_FCGI=OFF -DWITH_POSTGIS=OFF -DWITH_WFS=OFF -DWITH_WCS=OFF -DWITH_LIBXML2=OFF "
        + "-DWITH_PYTHON=ON -DPYTHON_EXECUTABLE={}/bin/python ../ ".format(event.path)
        + " > ../configure.out.txt && make",
        "    {}/bin/pip install --no-cache-dir src/mapscript/python".format(event.path),
        "    rm -rf /tmp/mapserver",
        ")",
    )
