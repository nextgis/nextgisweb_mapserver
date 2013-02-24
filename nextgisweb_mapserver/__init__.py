# -*- coding: utf-8 -*-
from pkg_resources import resource_string
from lxml import etree

from nextgisweb.component import Component, require


@Component.registry.register
class MapserverStyleComponent(Component):
    identity = 'mapserver_style'

    @require('style', 'marker_library')
    def initialize(self):
        super(MapserverStyleComponent, self).initialize()

        from . import models
        models.initialize(self)

        self.rng = etree.fromstring(_resource('schema.rng'))

    def setup_pyramid(self, config):
        super(MapserverStyleComponent, self).setup_pyramid(config)

        from . import views
        views.setup_pyramid(self, config)

    settings_info = (
        dict(key='fontset', desc=u"Список шрифтов в формате MAPFILE FONTSET"),
    )


def amd_packages():
    return (
        ('mapserver_style', 'nextgisweb_mapserver:amd_packages/mapserver_style'),
    )


def _resource(path):
    return resource_string('nextgisweb_mapserver', path)
