import sys

from ngwdocker import PackageBase

class Package(PackageBase):

    def debpackages(self):
        return (
            'python-mapscript',
        )

    def envsetup(self):
        self.dockerfile.write(
            'COPY package/nextgisweb_mapserver/mapscript-to-env /opt/ngw/build/nextgisweb_mapserver-mapscript-to-env',
            'RUN /opt/ngw/build/nextgisweb_mapserver-mapscript-to-env /opt/ngw/env',
)
