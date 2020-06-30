# -*- coding: utf-8 -*-
from __future__ import division, absolute_import, print_function, unicode_literals

from pkg_resources import resource_filename
from nextgisweb.component import Component, require

from .model import Base


class MapserverComponent(Component):
    identity = 'mapserver'
    metadata = Base.metadata

    @require('render', 'marker_library')
    def initialize(self):
        super(MapserverComponent, self).initialize()

        # Default settings for fontset
        if 'fontset' not in self.settings:
            self.settings['fontset'] = resource_filename(
                'nextgisweb_mapserver', 'fonts/fontset')

    def setup_pyramid(self, config):
        super(MapserverComponent, self).setup_pyramid(config)
        from . import view
        view.setup_pyramid(self, config)

    settings_info = (
        dict(key='fontset', desc=u"List of fonts in MAPFILE FONTSET format"),
    )


def pkginfo():
    return dict(components=dict(mapserver="nextgisweb_mapserver"))


def amd_packages():
    return ((
        'ngw-mapserver', 'nextgisweb_mapserver:amd/ngw-mapserver'
    ),)
