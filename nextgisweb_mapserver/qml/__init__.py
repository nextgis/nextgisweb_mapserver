# -*- coding: utf-8 -*-
from copy import deepcopy
from lxml.builder import ElementMaker

E = ElementMaker()


def warn(e, t, msg):
    pass


def mm2px(mm):
    return float(mm) * (72.0 / 25.4)


def color_property(value, tag, warn=warn):
    red, green, blue, alpha = map(int, value.split(','))

    result = E(tag)
    result.set('red', str(red))
    result.set('green', str(green))
    result.set('blue', str(blue))

    return result


def proplist(e):
    return dict([
        (p.attrib['k'], p.attrib['v'])
        for p in e.iterfind('./prop')
    ])


def layer(e, dst=None, root=None, opacity=100, warn=warn):
    if dst is None:
        dst = E.style()

    if opacity != 100:
        dst.append(E.opacity(str(opacity)))

    if e.get('pass', '0') != '0':
        warn(e, dst, u"Порядок отрисовки символов не поддерживается")

    cls = e.attrib['class']

    if cls == "SimpleMarker":
        layer_simple_marker(e, dst, root=root, warn=warn)

    elif cls == "SimpleLine":
        layer_simple_line(e, dst, root=root, warn=warn)

    elif cls == "MarkerLine":
        layer_marker_line(e, dst, root=root, warn=warn)

    elif cls == "SimpleFill":
        layer_simple_fill(e, dst, root=root, warn=warn)

    else:
        raise NotImplementedError(u"Неизвестный маркер: %s" % cls)

    return dst


def layer_simple_marker(src, dst=None, root=None, warn=warn):
    SIMPLE_MARKER = dict(
        rectangle='std:rectangle',
        circle='std:rectangle',
        diamond='std:diamond',
        triangle='std:triangle',
        equilateral_triangle='std:triangle-equilateral',
        star='std:star',
        pentagon='std:pentagon',
        arrow='std:arrow',
        regular_star='std:star',
        cross='std:cross',
        cross2='std:xcross',
        arrowhead='std:arrowhead',
        line='std:line',
    )

    if dst is None:
        dst = E.style()

    props = proplist(src)
    known = set()

    for k, v in props.iteritems():

        if k == 'name':
            mark = v
            if mark not in SIMPLE_MARKER:
                warn(src, dst, u"Неизвестный тип маркера: %s" % mark)
                mark = 'rectangle'

            dst.append(E.symbol(SIMPLE_MARKER[mark]))
            known.add(k)

        elif k == 'color':
            dst.append(color_property(v, 'color', warn))
            known.add(k)

        elif k == 'color_border':
            dst.append(color_property(v, 'outlinecolor', warn))
            known.add(k)

        elif k == 'angle':
            if v != '0':
                dst.append(E.angle(v))
            known.add(k)

        elif k == 'offset':
            if v != '0,0':
                dst.append(E.offset(dict(zip(
                    ('x', 'y'),
                    map(lambda s: str(mm2px(s)), v.split(','))
                ))))
            known.add(k)

        elif k == 'size':
            dst.append(E.size(str(mm2px(v))))
            known.add(k)

        elif k in ('scale_method', ):
            # А что это значит? Игнорируем без вопросов!
            known.add(k)

    unknown = set(props.keys()) - known
    if unknown != set():
        warn(
            src, dst,
            u"Остались необработанные атрибуты: %s" % (', '.join(unknown))
        )

    return dst


def layer_simple_line(src, dst=None, root=None, warn=warn):
    CAPSTYLE = dict(square='square', flat='butt', round='round')
    JOINSTYLE = ('bevel', 'milter', 'round')

    if dst is None:
        dst = E.style()

    props = proplist(src)
    known = set()

    for k, v in props.iteritems():
        if k == 'capstyle':
            if v in CAPSTYLE:
                dst.append(E.linecap(CAPSTYLE[v]))
                known.add(k)
            else:
                warn(src, dst, u"Неизвестный тип окончания: %s" % v)

        elif k == 'color':
            dst.append(color_property(v, 'color', warn))
            known.add(k)

        elif k == 'joinstyle':
            if v in JOINSTYLE:
                dst.append(E.linejoin(v))
                known.add(k)
            else:
                warn(src, dst, u"Неизвестный тип соединения: %s" % v)

        elif k == 'width':
            dst.append(E.width(str(mm2px(v))))
            known.add(k)

        elif k == 'penstyle':
            pattern = None

            if props.get('use_custom_dash', '0') != '0':
                pattern = map(float, props['customdash'].split(';'))
            elif v == 'solid':
                pattern = ()
            elif v == 'dash':
                pattern = (4, 2)
            elif v == 'dot':
                pattern = (1, 2)
            elif v == 'dash dot':
                pattern = (4, 2, 1, 2)
            elif v == 'dash dot dot':
                pattern = (4, 2, 1, 2, 1, 2)

            if pattern is not None:
                if len(pattern) != 0:
                    width = mm2px(props['width'])
                    pattern = map(lambda x: str(x * width), pattern)
                    dst.append(E.pattern(' '.join(pattern)))

                known.add('penstyle')
                known.add('use_custom_dash')
                known.add('customdash')

        elif k == 'offset':
            if v != '0':
                dst.append(E.offset(x=v, y='-99'))
            known.add(k)

    unknown = set(props.keys()) - known
    if unknown != set():
        warn(
            src, dst,
            u"Остались необработанные атрибуты: %s" % (', '.join(unknown))
        )

    return dst


def layer_marker_line(src, dst=None, root=None, warn=warn):
    if dst is None:
        dst = E.style()

    props = proplist(src)
    known = set()

    for k, v in props.iteritems():
        if k == 'interval':
            dst.append(E.gap(str(
                (-1 if props.get('rotate', '0') == '1' else 1) * mm2px(v)
            )))
            known.add(k)

        if k == 'rotate':
            if v == '0':
                known.add(k)
            if v == '1':
                dst.append(E.angle('auto'))
                known.add(k)

    unknown = set(props.keys()) - known
    if unknown != set():
        warn(
            src, dst,
            u"Остались необработанные атрибуты: %s" % (', '.join(unknown))
        )

    first = True
    for lr in src.iterfind('./symbol/layer'):
        if first:
            layer(lr, dst, root=root, warn=warn)
            first = False
        else:
            warn(
                lr, dst,
                u"Маркерные линии из нескольких маркеров не поддерживаются!"
            )

    return dst


def layer_simple_fill(src, dst=None, root=None, warn=warn):
    if dst is None:
        dst = E.style()

    props = proplist(src)
    known = set()

    for k, v in props.iteritems():
        if k == 'color':
            if props.get('style', None) != 'no':
                dst.append(color_property(v, 'color', warn))
            known.add(k)

        elif k == 'color_border':
            if props.get('style_border', None) != 'no':
                dst.append(color_property(v, 'outlinecolor', warn))
            known.add(k)

        elif k == 'offset':
            if v != '0,0':
                x, y = v.split(',')
                dst.append(E.offset(x=x, y=y))
            known.add(k)

        elif k == 'style':
            if v == 'solid' or v == 'no':
                known.add(k)

            elif v in ('horizontal', 'vertical', 'f_diagonal', 'b_diagonal'):
                if v == 'horizontal':
                    angle = 0
                elif v == 'vertical':
                    angle = 90
                elif v == 'b_diagonal':
                    angle = 45
                elif v == 'f_diagonal':
                    angle = 135

                dst.extend((
                    E.symbol('std:hatch'),
                    E.angle(str(angle)),
                    E.size('6'),
                ))
                known.add(k)

            elif v == 'diagonal_x':
                dst.extend((
                    E.symbol('std:xcross'),
                    E.size('8'),
                ))
                known.add(k)

        elif k == 'style_border':
            if v == 'solid' or v == 'no':
                known.add(k)

            elif props.get('style', None) == 'no':
                # PATTERN будет работать только если нет заливки,
                # в противном случае MS игнорирует PATTERN почему-то

                pattern = None
                if v == 'dash':
                    pattern = (4, 2)
                elif v == 'dot':
                    pattern = (1, 2)
                elif v == 'dash dot':
                    pattern = (4, 2, 1, 2)
                elif v == 'dash dot dot':
                    pattern = (4, 2, 1, 2, 1, 2)

                if pattern is not None:
                    width = mm2px(props.get('width_border', 0))
                    pattern = map(lambda x: str(x * width), pattern)
                    dst.append(E.pattern(' '.join(pattern)))
                    known.add(k)

            else:
                warn(
                    src, dst,
                    u"Совместное использование заливки и стиля невозможно!"
                )
                warn(
                    src, dst,
                    u"Используйте составной символ QuantumGIS.            "
                )

        elif k == 'width_border':
            if props.get('style_border', None) != 'no':
                dst.append(E.width(str(mm2px(v))))
            known.add(k)

    unknown = set(props.keys()) - known
    if unknown != set():
        warn(
            src, dst,
            u"Остались необработанные атрибуты: %s" % (', '.join(unknown))
        )

    return dst


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


def label(src, mapelem, warn=warn):
    layer = mapelem.find('./layer')

    def apply_label(label):
        for cls in layer.iterfind('./class'):
            cls.append(deepcopy(label))

    if  src.xpath(
        './customproperties/property'
        '[@key="labeling/enabled" and @value="true"]'
    ):
        # Это "новые" (1.9) подписи
        custp = dict()
        for p in src.iterfind('./customproperties/property[@key]'):
            custp[p.get('key')] = p.get('value')

        layer.insert(0, E.labelitem(custp.get('labeling/fieldName', '')))

        fstyle = custp.get('labeling/namedStyle', 'Regular') \
            .lower().replace(' ', '-')

        # Перевод русских названий очертаний из qml
        fstyle = {
            u'жирный': 'bold',
            u'курсив': 'italic',
            u'жирный-курсив': 'bold-italic',
        }.get(fstyle, fstyle)

        if fstyle not in (
            'regular', 'bold', 'oblique',
            'italic', 'bold-oblique', 'bold-italic',
        ):
            fstyle = 'regular'

        elem = E.label(
            E.type('truetype'),
            E.font(fstyle),
            E.size(custp.get('labeling/fontSize', '0')),
            E.color(
                red=custp.get('labeling/textColorR', '0'),
                green=custp.get('labeling/textColorG', '0'),
                blue=custp.get('labeling/textColorB', '0'),
            )
        )

        bufv = custp.get('labeling/bufferSize', '0')
        if bufv != '0':
            elem.extend((
                E.outlinewidth(str(int(round(mm2px(bufv))))),
                E.outlinecolor(
                    red=custp.get('labeling/bufferColorR', '0'),
                    green=custp.get('labeling/bufferColorG', '0'),
                    blue=custp.get('labeling/bufferColorB', '0')
                )
            ))

        # Offset from point
        if custp.get('labeling/placement', None) == '1':
            x = {'-1': 'l', '0': 'c', '1': 'r'}[custp.get('labeling/xQuadOffset')]
            y = {'-1': 'l', '0': 'c', '1': 'u'}[custp.get('labeling/yQuadOffset')]
            elem.append(E.position(y + x))

        # Parallel
        elif custp.get('labeling/placement', None) == '2':
            elem.append(E.angle('auto'))

        # Curved
        elif custp.get('labeling/placement', None) == '3':
            elem.append(E.angle('follow'))
            angle = (
                abs(float(custp['labeling/maxCurvedCharAngleIn']))
                + abs(float(custp['labeling/maxCurvedCharAngleOut']))
            ) / 2
            elem.append(E.maxoverlapangle(str(angle)))

        # Horizontal
        elif custp.get('labeling/placement', None) == '4':
            pass

        apply_label(elem)


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

    label(src, dst, warn)

    return dst
