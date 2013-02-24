# -*- coding: utf-8 -*-

_OBJ = dict(type='obj')
_KW = dict(type='keyword', quote=True)
_RAW = dict(type='keyword', quote=False)

_COLOR = dict(
    type="keyword",
    formatter=lambda (e): ' '.join((e.get('red'), e.get('green'), e.get('blue')))
)

_PROJECTION = dict(
    type="obj",
    formatter=lambda (e): '"init=epsg:%s"' % e.get('epsg')
)

_POINTS = dict(
    type="obj",
    formatter=lambda (e): e.text
)


_CONFIG = {
    'map': _OBJ,
    'outputformat': _OBJ,
    'web': _OBJ,
    'metadata': _OBJ,
    'layer': _OBJ,
    'class': _OBJ,
    'style': _OBJ,
    'label': _OBJ,
    'feature': _OBJ,

    'map/symbol': dict(
        type='obj',
        attrs=dict(name=_KW, type=_RAW),
    ),

    'layer/labelcache': _RAW,

    'label/type': _RAW,
    'label/force': _RAW,
    'label/position': _RAW,
    'label/mindistance': _RAW,

    'color': _COLOR,
    'imagecolor': _COLOR,
    'outlinecolor': _COLOR,

    'projection': _PROJECTION,
    'points': _POINTS,

    'map/size': _RAW,
    'map/maxsize': _RAW,
    'extent': _RAW,
    'opacity': _RAW,
    'width': _RAW,
    'size': _RAW,
    'symbol/type': _RAW,
    'symbol/filled': _RAW,
    'layer/connectiontype': _RAW,
    'layer/type': _RAW,
}


def element_to_mapfile(element, buf, root=None, indent=""):
    if not root:
        root = element

    def _kw(kw, value, quote=False, indent=""):
        if quote:
            value = value.replace(r"\\", r'\\\\')
            value = value.replace(r'"', r'\"')
            value = '"' + value + '"'

        buf.write('%s%s %s\n' % (indent, kw.upper(), value))

    c = element
    pcomp = []
    while True:
        pcomp.insert(0, c.tag.lower())
        c = c.getparent()

        if c is None:
            break

    config = dict(type='keyword', quote=True)

    for i in xrange(len(pcomp)):
        path = '/'.join(pcomp[i:])
        if path in _CONFIG:
            config = _CONFIG[path]
            break

    if config['type'] == 'obj':
        buf.write(indent + element.tag.upper() + '\n')

        formatter = config.get('formatter', None)
        
        if formatter:
            buf.write(indent + '  ' + formatter(element) + '\n')

        else:
            attrs = config.get('attrs', dict())
            for kw, kwcfg in attrs.iteritems():
                if kw in element.attrib:
                    _kw(
                        kw, element.get(kw),
                        quote=kwcfg.get('quote', False),
                        indent=indent + '  '
                    )

            for sub in element:
                element_to_mapfile(sub, buf, indent=indent + '  ')

        buf.write(indent + 'END' + '\n')

    elif config['type'] == 'keyword':
        buf.write(indent + element.tag.upper() + ' ')
        
        formatter = config.get('formatter', None)
        if formatter:
            value = formatter(element)

        else:
            value = element.text

            if config.get('quote', False):
                value = value.replace(r"\\", r'\\\\')
                value = value.replace(r'"', r'\"')
                value = '"' + value + '"'

        buf.write(value + '\n')
