# -*- coding: utf-8 -*-

"""Синтаксический анализатор"""


import ply.yacc as yacc

from logic_expr_lexer import tokens, lexer # Не удалять импорт tokens
from logic_expr_lexer import CharNotRecognizedError

class TokenNotRecognizedError(Exception):
    pass

def p_expression(p):
    """expression : LBRAC subexpression RBRAC"""
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
              | QUOTE IDENTIFIER QUOTE
              | DOUBLEQUOTE IDENTIFIER DOUBLEQUOTE
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
                    | LBRAC subexpression RBRAC LOGIC_OPERATOR LBRAC subexpression RBRAC
    """
    pass


# Обработка ошибок
def p_error(p):
    print 'Error. Token:', p
    raise TokenNotRecognizedError("Syntax error")


# Парсер
parser = yacc.yacc()


if __name__ == "__main__":
    examples = [
        u"([POPULATION] > 50000 AND '[LANGUAGE]' eq 'FRENCH')", # Составной оператор без скобочек
        u'( ("[LANG4]" ~ "FRENCH2") AND ([attr] gt 30) )',  # Составной оператор со скобочками
        u"('[LANGUAGE]' lt '')",
        u"( 3 < 4)",
        u"([attr] gt 30)",
        u"('[LANGUAGE]' eq 'FRENCH2')",
        u'("[LANGUAGE]" eq "FRENCH2")',
        u'''("[LANGUAGE]" eq "FR 'w'2")''',
        u'("[LANG4]" ~ "FRENCH2")',
        u'("[LANG4]" ~ "<dsf\'!@$%^&*<>-:;,.?ыфва")',   # Много всяких символов внутри строки
    ]
    for s in examples:
        print 'PARSING:', s
        result = parser.parse(s)
        print 'Ok'

    errors = [
        u"(aslgjkl)",           # Абракадабра какая-то
        u"3 < 5",               # Нет скобок
        u"([POPULATION])",      # Отсутствует выражение
        u"([LANGUAGE] lt '')",  # Строки-операнды должны быть в кавычках: '[LANGUAGE]'
        u'("[L4]" ~ [L2])',     # ~ это строковый оператор, операнды должны быть в кавычках
        u'( ("[LANG4]" ~ "FRENCH2") AND [attr] gt 30) )',  # Несбалансированные скобки
    ]
    for s in errors:
        print'PARSING:', s
        try:
            result = parser.parse(s)
        except TokenNotRecognizedError:
            print 'Syntax error is Ok. We expected the error.'  # Ожидаем ошибку распознавания
        except CharNotRecognizedError:
            print 'Syntax error is Ok. We expected the error.'  # Ожидаем ошибку распознавания
        else:
            print 'ERROR!!!'    # Выражение не должно быть распарсено.
            raise Exception


