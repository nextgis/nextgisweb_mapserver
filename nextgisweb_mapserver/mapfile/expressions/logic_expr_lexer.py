import re

import ply.lex as lex


class CharNotRecognizedError(Exception):
    pass


tokens = (
    "NUMBER",
    "IDENTIFIER",
    "LOGIC_OPERATOR",
    "OPERATOR",
    "STRING_OPERATOR",
    "LBRAC",
    "RBRAC",
    "STRING",
)


t_NUMBER = r"[+-]?(\d+)?\.\d+([Ee][+-]?\d+)?|[+-]?\d+?\.([Ee][+-]?\d+)?|[+-]?\d+"
t_IDENTIFIER = r"\[[A-Z_]+[A-Z0-9_:-]*\]"
t_LOGIC_OPERATOR = r"(and)|(or)|(&&)|(\|)"
t_OPERATOR = r"(!=)|(>=)|(<=)|(<)|(>)|(=\*)|(=)|(lt)|(gt)|(ge)|(le)|(eq)|(ne)"
t_STRING_OPERATOR = r"(~\*)|(~)"
t_LBRAC = r"\("
t_RBRAC = r"\)"
t_STRING = r"('[^\']*')|(\"[^\"]*\")|(`[^\`]*`)"


t_ignore = " \t"


def t_error(t):
    msg = "Illegal character"
    raise CharNotRecognizedError(msg)


lexer = lex.lex(reflags=re.IGNORECASE + re.UNICODE)
