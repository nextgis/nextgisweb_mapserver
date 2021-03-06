# -*- coding: utf-8 -*-
from __future__ import division, absolute_import, print_function, unicode_literals

from six import text_type

from nose.tools import eq_

from .primitive import (
    Integer,
    Double,
    Boolean,
)


def test_integer_isvalid():
    for t in ('', '1.0', '1 000'):
        eq_(Integer.isvalid(t), False)


def test_integer_from_string():
    for v in (-1, 0, 1, -100, 100):
        eq_(Integer.from_string(text_type(v)).value, v)


def test_double_isvalid():
    for t in ('', '0,0', '1 000'):
        eq_(Double.isvalid(t), False)


def test_double_from_string():
    for v in (-1, 0, 1, -1.1, -100, 100):
        eq_(Double.from_string(text_type(v)).value, v)


def test_boolean_isvalid():
    for t in ('FALSE', 'True'):
        eq_(Boolean.isvalid(t), False)


def test_boolean_from_string():
    eq_(Boolean.from_string('true').value, True)
    eq_(Boolean.from_string('false').value, False)

