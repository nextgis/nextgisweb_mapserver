from lxml import etree

from nextgisweb.resource import Widget
from nextgisweb.object_widget import ObjectWidget

from .mapfile import schema
from .extmapfile import Map

from .model import MapserverStyle

from .util import _


class StyleWidget(Widget):
    resource = MapserverStyle
    operation = ('create', 'update')
    amdmod = 'ngw-mapserver/StyleWidget'

    def config(self):
        res = super(StyleWidget, self).config()

        # TODO: Security
        if self.operation == 'create':
            res['defaultValue'] = MapserverStyle.default_style_xml(
                self.obj.parent)

        return res


def setup_pyramid(comp, config):

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
                result = err(_("XML syntax error: %(message)s") % dict(message=e.message))

            except etree.DocumentInvalid as e:
                result = err(_("XML schema error: %(message)s") % dict(message=e.message))

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
                    xml=MapserverStyle.default_style_xml(self.options['parent'])
                )

            return result

    MapserverStyle.object_widget = MapserverStyleObjectWidget
