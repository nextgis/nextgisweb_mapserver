# -*- coding: utf-8 -*-
import json

from lxml import etree
from pyramid.response import Response

from nextgisweb.resource import Widget
from nextgisweb.env import env
from nextgisweb.object_widget import ObjectWidget

from .mapfile import schema
from .extmapfile import Map
from .qml import transform

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

    def qml(request):
        fileid = request.json_body['file']['upload_meta'][0]['id']
        filename, metadata = env.file_upload.get_filename(fileid)

        elem = etree.parse(filename).getroot()

        def warn(src, dst, msg):
            dst.append(etree.Comment(u" " + msg + u" "))

        dst = transform(elem, warn=warn)

        body = etree.tostring(dst, pretty_print=True, encoding=unicode)

        XML, JSON = 'text/xml', 'application/json'

        if request.accept.best_match([XML, JSON]) == XML:
            return Response(body, content_type=XML)
        else:
            return Response(json.dumps(body), content_type=JSON)

    config.add_route('mapserver.qml_transform', '/mapserver/qml-transform', client=()) \
        .add_view(qml, request_method='POST')
