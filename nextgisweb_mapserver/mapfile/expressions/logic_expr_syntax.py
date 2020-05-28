# -*- coding: utf-8 -*-

"""Синтаксический анализатор"""

import sys
import os

import ply.yacc as yacc

from .logic_expr_lexer import tokens, lexer # Не удалять импорт tokens # NOQA
from .logic_expr_lexer import CharNotRecognizedError


class TokenNotRecognizedError(Exception):
    pass


def p_expression(p):
    """expression : LBRAC subexpression RBRAC
                   | string
    """
    pass


def p_subexpression(p):
    """subexpression : string_expression
             | binary_expression
             | concatenation
    """
    pass


def p_string_expression(p):
    """string_expression : string OPERATOR string
                         | string STRING_OPERATOR string
    """
    pass


def p_string(p):
    """string : STRING
    """
    pass


def p_binary_expression(p):
    """binary_expression : number OPERATOR number
    """
    pass


def p_number(p):
    """number : NUMBER
              | IDENTIFIER
    """
    pass


def p_concatenation(p):
    """concatenation : subexpression LOGIC_OPERATOR subexpression
                    | LBRAC subexpression RBRAC
    """
    pass


# Обработка ошибок
def p_error(p):
    raise TokenNotRecognizedError("Syntax error")


# Временное перенаправление stderr > /dev/null иначе мусов в консоли
_stderr_original = sys.stderr
try:
    with open(os.devnull, 'w') as fd:
        sys.stderr = fd
        parser = yacc.yacc(debug=False, write_tables=0)  # Парсер

finally:
    sys.stderr = _stderr_original

if __name__ == "__main__":
    examples = [
        u'"просто строка -- это тоже валидное выражение"',
        u"''",          # Пустая строка
        u'""',          # Пустая строка
        u"'   '",       # Строка с пробелами
        u'"  "',
        u"""' "sdf" '""",   # Строка содержащая кавычки
        u'''" 'sdf' "''',   # Строка содержащая кавычки
        u"([POPULATION] > 50000 AND '[LANGUAGE]' eq 'FRENCH')", # Составной оператор без скобочек
        u'( ("[LANG4]" ~ "FRENCH2") AND ([attr] gt 30) )',  # Составной оператор со скобочками
        u'( ("[LANG4]" ~ "FRENCH2") AND ([attr] gt 30) or ([attr1] lt 30) OR ([attr2] = 30))',  # Много скобочек
        u"('[LANGUAGE]' lt '')",
        u"( 3 < 4)",
        u"( 3.4 < -4.3e+12)",
        u"([attr] gt 30)",
        u"([attr] gt 1.30)",
        u"('[LANGUAGE]' eq 'FRENCH2')",
        u'("[LANGUAGE]" eq "FRENCH2")',
        u'''("[LANGUAGE]" eq "FR 'w'2")''',
        u'("[LANG4]" ~ "FRENCH2")',
        u'("[LANG4]" ~ "<dsf\'!@$%^&*<>-:;,.?ыфва")',   # Много всяких символов внутри строки
    ]
    for s in examples:
        print('PARSING:', s)
        result = parser.parse(s)
        # print 'Ok'

    errors = [
        u"(aslgjkl)",           # Абракадабра какая-то
        u"4",                   # Просто число
        u'"просто строка, но несбалансированные кавычки',
        u"3 < 5",               # Нет скобок
        u"([POPULATION])",      # Отсутствует выражение
        u"([LANGUAGE] lt '')",  # Строки-операнды должны быть в кавычках: '[LANGUAGE]'
        u'("[L4]" ~ [L2])',     # ~ это строковый оператор, операнды должны быть в кавычках
        u'( ("[LANG4]" ~ "FRENCH2") AND [attr] gt 30) )',  # Несбалансированные скобки
    ]
    for s in errors:
        print('PARSING:', s)
        try:
            result = parser.parse(s)
        except TokenNotRecognizedError:
            print('Ok. The syntax error is found')
            # print 'Syntax error is Ok. We expected the error.'  # Ожидаем ошибку распознавания
        except CharNotRecognizedError:
            print('Ok. The syntax error is found')
            # print 'Syntax error is Ok. We expected the error.'  # Ожидаем ошибку распознавания
        else:
            print('ERROR!!!')  # Выражение не должно быть распарсено.
            raise Exception
