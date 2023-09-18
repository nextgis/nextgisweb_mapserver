import ply.yacc as yacc

from .logic_expr_lexer import CharNotRecognizedError, lexer, tokens  # NOQA: F401


class TokenNotRecognizedError(Exception):
    pass


# fmt: off

def p_expression(p):
    """expression : LBRAC subexpression RBRAC
                  | string
    """


def p_subexpression(p):
    """subexpression : string_expression
                     | binary_expression
                     | concatenation
    """


def p_string_expression(p):
    """string_expression : string OPERATOR string
                         | string STRING_OPERATOR string
    """


def p_string(p):
    """string : STRING"""


def p_binary_expression(p):
    """binary_expression : number OPERATOR number"""


def p_number(p):
    """number : NUMBER
              | IDENTIFIER
    """


def p_concatenation(p):
    """concatenation : subexpression LOGIC_OPERATOR subexpression
                     | LBRAC subexpression RBRAC
    """


def p_error(p):
    raise TokenNotRecognizedError("Syntax error")

# fmt: on


parser = yacc.yacc(debug=False, write_tables=False)
