# -*- coding: utf-8 -*-
from pkg_resources import resource_filename
from nextgisweb.component import Component, require

from .models import Base


@Component.registry.register
class MapserverStyleComponent(Component):
    identity = 'mapserver_style'
    metadata = Base.metadata

    @require('style', 'marker_library')
    def initialize(self):
        super(MapserverStyleComponent, self).initialize()

        # Настройки по-умолчанию для fontset
        if 'fontset' not in self.settings:
            self.settings['fontset'] = resource_filename(
                'nextgisweb_mapserver', 'fonts/fontset')

    def setup_pyramid(self, config):
        super(MapserverStyleComponent, self).setup_pyramid(config)

        from . import views
        views.setup_pyramid(self, config)

    settings_info = (
        dict(key='fontset', desc=u"Список шрифтов в формате MAPFILE FONTSET"),
    )


def amd_packages():
    return ((
        'mapserver_style', 'nextgisweb_mapserver:amd_packages/mapserver_style'
    ),)
