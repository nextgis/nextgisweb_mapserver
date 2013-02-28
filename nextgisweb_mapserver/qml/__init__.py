# -*- coding: utf-8 -*-
from copy import deepcopy
from lxml.builder import ElementMaker

E = ElementMaker()


def warn(e, t, msg):
    pass


def mm2px(mm):
    return str(int(round(float(mm) * (72.0 / 25.4))))


def color_property(e, tag, warn=warn):
    value = e.get("v")
    red, green, blue, alpha = map(int, value.split(','))

    result = E(tag)
    result.set('red', str(red))
    result.set('green', str(green))
    result.set('blue', str(blue))

    return result


_SIMPLE_MARKER = dict(
    rectangle=E.symbol(
        E.name('rectangle'),
        E.type('vector'),
        E.filled('true'),
        E.points('-1 1 1 1 1 -1 -1 -1 -1 1'),
    ),
    circle=E.symbol(
        E.name('circle'),
        E.type('ellipse'),
        E.filled('true'),
        E.points('1 1'),
    ),
    diamond=E.symbol(
        E.name('diamond'),
        E.type('vector'),
        E.filled('true'),
        E.points('0 1 1 0 0 -1 -1 0 0 1'),
    ),
    cross=E.symbol(
        E.name('cross'),
        E.type('vector'),
        E.filled('true'),
        E.points('-1 0 1 0 -99 -99 0 -1 0 1'),
    ),
    cross2=E.symbol(
        E.name('cross2'),
        E.type('vector'),
        E.filled('true'),
        E.points('-1 -1 1 1 -99 -99 -1 1 1 -1'),
    ),
    line=E.symbol(
        E.name('line'),
        E.type('vector'),
        E.filled('true'),
        E.points('0 -1 0 1'),
    )
)


def layer(e, root=None, opacity=100, warn=warn):
    result = E('style')

    if opacity != 100:
        result.append(E.opacity(str(opacity)))

    if e.get('pass', '0') != '0':
        warn(e, result, u"Порядок отрисовки символов не поддерживается")

    cls = e.attrib['class']

    if cls == "SimpleMarker":
        for p in e:
            if p.tag != 'prop':
                warn(p, result, u"Неопознанный тег %s" % p.tag)
                continue

            k = p.attrib['k']
            v = p.attrib['v']

            if k == 'name':
                mark = v
                if mark not in _SIMPLE_MARKER:
                    warn(p, result, u"Неизвестный тип маркера: %s" % mark)
                    mark = 'rectangle'

                result.append(E.symbol(mark))

                if root is not None:
                    existing = root.xpath('./symbol/name[text()="%s"]' % mark)
                    if len(existing) == 0:
                        root.append(deepcopy(_SIMPLE_MARKER[mark]))

            elif k == 'color':
                result.append(color_property(p, 'color', warn))

            elif k == 'color_border':
                result.append(color_property(p, 'outlinecolor', warn))

            elif k == 'angle':
                if v != '0':
                    result.append(E.angle(v))

            elif k == 'offset':
                if v != '0,0':
                    result.append(E.offset(
                        dict(zip(('x', 'y'), map(mm2px, v.split(','))))
                    ))

            elif k == 'size':
                result.append(E.size(mm2px(v)))

            elif k in ('scale_method', ):
                # А что это значит? Игнорируем без вопросов!
                pass

            else:
                warn(p, result, u"Неопознанный атрибут %s = %s" % (k, v))

    else:
        raise NotImplementedError(u"Неизвестный маркер: %s" % cls)

    return result


def symbol(src, dst=None, root=None, warn=warn):
    if dst is None:
        dst = E('class')

    alpha = float(src.get('alpha', '1'))
    opacity = int(alpha * 100)

    for l in src:
        if l.tag == 'layer':
            dst.append(layer(
                l,
                opacity=opacity,
                root=root,
                warn=warn,
            ))
        else:
            warn(l, dst, u"Неизвестный тег %s" % l.tag)

    return dst


def renderer_single_symbol(src, dst=None, root=None, warn=warn):
    if dst is None:
        dst = E('layer')

    assert src.get('type') == 'singleSymbol'

    cls = E('class')
    dst.append(cls)

    for smbl in src.iterfind('./symbols/symbol'):
        symbol(smbl, cls, root=root, warn=warn)

    return dst


def renderer_categorized_symbol(src, dst=None, root=None, warn=warn):
    if dst is None:
        dst = E('layer')

    assert src.get('type') == 'categorizedSymbol'

    dst.append(E.classitem(src.get('attr')))

    for cat in src.iterfind('./categories/category'):
        cls = E('class')
        dst.append(cls)

        if cat.get('value', '') != '':
            cls.append(E.expression(cat.get('value')))

        smbl = src.find('./symbols/symbol[@name=\'%s\']' % cat.get("symbol"))
        assert smbl is not None, "Symbol not found"

        symbol(smbl, cls, root=root, warn=warn)

    return dst


def transform(src, dst=None, warn=warn):
    if dst is None:
        dst = E.map()

    assert src.tag == 'qgis'

    renderer = src.find('./renderer-v2')
    assert renderer is not None

    stype = renderer.get('type')

    if stype == 'singleSymbol':
        proc = renderer_single_symbol

    elif stype == 'categorizedSymbol':
        proc = renderer_categorized_symbol

    else:
        raise NotImplementedError(u"Неизвестный тип: %s") % stype

    dst.append(proc(
        renderer,
        root=dst,
        warn=warn
    ))

    return dst
