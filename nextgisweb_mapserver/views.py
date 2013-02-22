# -*- coding: utf-8 -*-

from nextgisweb.object_widget import ObjectWidget


def setup_pyramid(comp, config):

    class MapserverStyleObjectWidget(ObjectWidget):
        model_attributes = ('opacity', 'stroke_width', 'stroke_color', 'fill_color')

        def is_applicable(self):
            return self.operation in ('create', 'edit')

        def populate_obj(self):
            ObjectWidget.populate_obj(self)

            for k in self.model_attributes:
                setattr(self.obj, k, self.data[k])

        def widget_module(self):
            return 'mapserver_style/Widget'

        def widget_params(self):
            result = ObjectWidget.widget_params(self)

            if self.obj:
                result['value'] = dict([(k, getattr(self.obj, k)) for k in self.model_attributes])

            return result

    comp.MapserverStyle.object_widget = MapserverStyleObjectWidget
