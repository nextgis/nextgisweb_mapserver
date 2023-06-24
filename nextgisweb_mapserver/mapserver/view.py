from nextgisweb.resource import Widget

from .model import MapserverStyle


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
    pass
