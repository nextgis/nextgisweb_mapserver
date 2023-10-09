# MapServer renderer for NextGIS Web

## Installation

First of all, clone the repository:

```bash
$ cd package
$ git clone git@github.com:nextgis/nextgisweb_mapserver.git
```

Package `nextgisweb_mapserver` requires `mapscript` Python package from
MapServer and it can't be installed via `pip` from PyPi. Thus, you must install
`mapscript` into a virtualenv before `nextgisweb_mapserver` installation.

The simplest way to do this is to copy it from system-wide installation. At
first, install `mapscript` system-wide first with a package manager. For Ubuntu
you can use `python3-mapscript` (or `python-mapscript` for Python 2) package,
for example:

```bash
$ apt install python3-mapscript
```

Then check if it's available for **system** Python:

```bash
$ /usr/bin/python3 -c "import mapscript; print(mapscript)"
<module 'mapscript' from '/usr/lib/python3/dist-packages/mapscript/__init__.py'>
```

After that copy it into the virtualenv via `mapscript-to-env` script from this
repository and then install `nextgisweb_mapserver` into the virtualenv:

```bash
$ nextgisweb_mapserver/mapscript-to-env ../env/bin/python /usr/bin/python3
$ pip install -e nextgisweb_mapserver/
```

## License

This program is licensed under GNU GPL v2 or any later version.

## Commercial support

Need to fix a bug or add a feature to MapServer renderer for NextGIS Web? We
provide custom development and support for this software.
[Contact us](http://nextgis.ru/en/contact/) to discuss options!

[![http://nextgis.com](http://nextgis.ru/img/nextgis.png)](http://nextgis.com)
