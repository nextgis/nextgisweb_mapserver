from pkg_resources import resource_filename

from mapscript import MS_VERSION

from nextgisweb.env import Component
from nextgisweb.lib.config import Option

_default_fontset = resource_filename('nextgisweb_mapserver', 'fonts/fontset')


class MapserverComponent(Component):

    def setup_pyramid(self, config):
        from . import view
        view.setup_pyramid(self, config)

    def sys_info(self):
        return (
            ("MapServer", MS_VERSION),
        )

    option_annotations = ((
        Option('fontset', default=_default_fontset,
               doc="List of fonts in MAPFILE FONTSET format"),
    ))
