## Установка

### Подготовка

Для работы модуля нужен MapScript, который в виртуальное окружение стандартным способом не ставится, поэтому установим его вручную.

Устанавливаем необходимый пакет в систему:

    $ sudo apt-get install python-mapscript

После чего копируем необходимые файлы в директорию виртуального окружения, используемого для работы NextGIS Web. На этом шаге возможны как минимум 2 варианта в зависимости от того, в каком виде устанвливается пакет python-mapscript в систему. Это зависит от используемого дистрибутива.

Если вы используете FreeBSD, то для копирования системного MapScript в виртуальное окружение (директория `env`) можно воспользоваться следующими командами:

    $ cp -r `python -c "import mapscript, os.path; print os.path.split(mapscript.__file__)[0]"` env/lib/python2.7/site-packages/mapscript.egg
    $ echo "./mapscript.egg" > env/lib/python2.7/site-packages/mapscript.pth

Если вы используете Ubuntu, то процесс будет несколько отличаться:

    $ mkdir env/lib/python2.7/site-packages/mapscript.egg
    $ cp /usr/lib/python2.7/dist-packages/*mapscript* env/lib/python2.7/site-packages/mapscript.egg
    $ echo "./mapscript.egg" > env/lib/python2.7/site-packages/mapscript.pth

Если сейчас выполнить команду:

    $ env/bin/pip freeze

то вы получите сообщение об ошибке:

    "Missing 'Version:' header and/or PKG-INFO file", mapscript [unknown version]

Для её исправления создаем файл `PKG0-INFO`:

    $ mkdir env/lib/python2.7/site-packages/mapscript.egg/EGG-INFO
    $ touch env/lib/python2.7/site-packages/mapscript.egg/EGG-INFO/PKG-INFO

И указываем в нём используемую версию MapScript:

    $ echo `python -c "import mapscript; print 'Version: %s' % mapscript.MS_VERSION"` > env/lib/python2.7/site-packages/mapscript.egg/EGG-INFO/PKG-INFO

### Установка

Клонируем репозиторий:

    $ git clone git@github.com:nextgis/nextgisweb_mapserver.git

Устанавливаем пакет в режиме разработки:

    $ env/bin/pip install -e ./nextgisweb_mapserver
