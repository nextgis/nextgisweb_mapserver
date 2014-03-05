# -*- coding: utf-8 -*-
from pkg_resources import resource_filename
from nextgisweb.component import Component, require

from .model import Base


@Component.registry.register
class MapserverComponent(Component):
    identity = 'mapserver'
    metadata = Base.metadata

    @require('style', 'marker_library')
    def initialize(self):
        super(MapserverComponent, self).initialize()

        # Настройки по-умолчанию для fontset
        if 'fontset' not in self.settings:
            self.settings['fontset'] = resource_filename(
                'nextgisweb_mapserver', 'fonts/fontset')

    def setup_pyramid(self, config):
        super(MapserverComponent, self).setup_pyramid(config)
        from . import view
        view.setup_pyramid(self, config)

    settings_info = (
        dict(key='fontset', desc=u"Список шрифтов в формате MAPFILE FONTSET"),
    )


def pkginfo():
    return dict(components=dict(mapserver_style="nextgisweb_mapserver"))


def amd_packages():
    return ((
        'ngw-mapserver', 'nextgisweb_mapserver:amd/ngw-mapserver'
    ),)
