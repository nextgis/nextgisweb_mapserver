# -*- coding: utf-8 -*-
from nextgisweb.component import Component, require


@Component.registry.register
class MapserverStyleComponent(Component):
    identity = 'mapserver_style'

    @require('style', 'marker_library')
    def initialize(self):
        super(MapserverStyleComponent, self).initialize()

        from . import models
        models.initialize(self)

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
