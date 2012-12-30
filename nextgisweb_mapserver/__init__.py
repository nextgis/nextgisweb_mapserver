# -*- coding: utf-8 -*-
from nextgisweb.component import Component

from .models import MapserverStyle

@Component.registry.register
class MapserverStyleComponent(Component):
	identity = 'mapserver_style'

def amd_packages():
	return (
		('mapserver_style', 'nextgisweb_mapserver:amd_packages/mapserver_style'),
	)
