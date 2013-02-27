# -*- coding: utf-8 -*-
from lxml import etree

from nextgisweb.object_widget import ObjectWidget

from .mapfile import schema
from .extmapfile import Map


def setup_pyramid(comp, config):
    MapserverStyle = comp.MapserverStyle

    class MapserverStyleObjectWidget(ObjectWidget):
        def is_applicable(self):
            return self.operation in ('create', 'edit')

        def validate(self):
            result = super(MapserverStyleObjectWidget, self).validate()

            self.error = []

            def err(msg):
                self.error.append(dict(message=msg))
                return False

            try:
                layer = etree.fromstring(self.data['xml'])

                relaxng = schema(Map)
                relaxng.assertValid(layer)

            except etree.XMLSyntaxError as e:
                result = err(u"Синтаксическая ошибка XML: %s" % e.message)

            except etree.DocumentInvalid as e:
                result = err(u"Ошибка схемы XML: %s" % e.message)

            return result

        def populate_obj(self):
            super(MapserverStyleObjectWidget, self).populate_obj()
            self.obj.xml = self.data['xml']

        def widget_module(self):
            return 'mapserver_style/Widget'

        def widget_params(self):
            result = super(MapserverStyleObjectWidget, self).widget_params()

            if self.obj:
                result['value'] = dict(xml=self.obj.xml)
            else:
                result['value'] = dict(
                    xml=MapserverStyle.default_style_xml(self.options['layer'])
                )

            return result

    comp.MapserverStyle.object_widget = MapserverStyleObjectWidget
