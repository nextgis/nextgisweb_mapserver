# -*- coding: utf-8 -*-
from __future__ import division, absolute_import, print_function, unicode_literals

from pkg_resources import resource_filename
from nextgisweb.component import Component, require
from nextgisweb.lib.config import Option

from .model import Base

_default_fontset = resource_filename(
    'nextgisweb_mapserver', 'fonts/fontset')


class MapserverComponent(Component):
    identity = 'mapserver'
    metadata = Base.metadata

    def setup_pyramid(self, config):
        super(MapserverComponent, self).setup_pyramid(config)
        from . import view
        view.setup_pyramid(self, config)

    option_annotations = ((
        Option('fontset', default=_default_fontset, doc=
            "List of fonts in MAPFILE FONTSET format"),
    ))


def pkginfo():
    return dict(components=dict(mapserver="nextgisweb_mapserver"))


def amd_packages():
    return ((
        'ngw-mapserver', 'nextgisweb_mapserver:amd/ngw-mapserver'
    ),)
