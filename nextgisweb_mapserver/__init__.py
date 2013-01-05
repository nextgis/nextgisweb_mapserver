# -*- coding: utf-8 -*-
from nextgisweb.component import Component, require


@Component.registry.register
class MapserverStyleComponent(Component):
    identity = 'mapserver_style'

    @require('style')
    def initialize(self):
        Component.initialize(self)

        from . import models
        models.include(self)

    def setup_pyramid(self, config):
        from . import views
        views.setup_pyramid(self, config)


def amd_packages():
    return (
        ('mapserver_style', 'nextgisweb_mapserver:amd_packages/mapserver_style'),
    )
