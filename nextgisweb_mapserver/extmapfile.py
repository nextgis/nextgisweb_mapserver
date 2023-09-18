from .mapfile import keyword


class Class(keyword.Class):
    members = filter(
        lambda m: m.name
        in (
            "EXPRESSION",
            "LABEL",
            "NAME",
            "STYLE",
            "MAXSCALEDENOM",
            "MINSCALEDENOM",
        ),
        keyword.Class.members,
    )


class Layer(keyword.Layer):
    members = filter(
        lambda m: m.name
        in (
            "CLASS",
            "CLASSITEM",
            "OPACITY",
            "SIZEUNITS",
            "UNITS",
            "LABELITEM",
        ),
        keyword.Layer.members,
    )


class Map(keyword.Map):
    members = (
        keyword.Symbol.subclass("SYMBOL", single=False),
        Layer.subclass("LAYER", single=True),
    )
