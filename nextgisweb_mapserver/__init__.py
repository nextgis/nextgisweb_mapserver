# -*- coding: utf-8 -*-
from nextgisweb.component import Component


@Component.registry.register
class MapserverStyleComponent(Component):
    identity = 'mapserver_style'

    def initialize(self):
        Component.initialize(self)

        from . import models
        models.include(self)


def amd_packages():
    return (
        ('mapserver_style', 'nextgisweb_mapserver:amd_packages/mapserver_style'),
    )
