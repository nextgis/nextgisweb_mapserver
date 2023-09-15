import ply.lex as lex
import pytest

from ..expressions.logic_expr_lexer import CharNotRecognizedError, lexer
from ..expressions.logic_expr_syntax import TokenNotRecognizedError, parser


def _tuple_to_token(t):
    assert len(t) == 3

    token = lex.LexToken()
    token.type = t[0]
    token.value = t[1]
    token.lexpos = t[2]
    token.lineno = 1

    return token


def get_tokens(token):
    tokens = []
    lexer.input(token)

    while True:
        tok = lexer.token()

        if not tok:
            return tokens
        tokens.append(tok)


def check_token_eq(token_list, expected_token_list):
    assert len(token_list) == len(expected_token_list)

    expected_token_list = [_tuple_to_token(t) for t in expected_token_list]
    for i in range(len(token_list)):
        token = token_list[i]
        expected = expected_token_list[i]

        assert token.type == expected.type
        assert token.value == expected.value
        assert token.lexpos == expected.lexpos


data = {
    "numbers": [
        "-23 34.4 24 -4.5 +2.3E-1 -2. +.4E+3 .4E3",
        [
            ("NUMBER", "-23", 0),
            ("NUMBER", "34.4", 4),
            ("NUMBER", "24", 9),
            ("NUMBER", "-4.5", 12),
            ("NUMBER", "+2.3E-1", 17),
            ("NUMBER", "-2.", 25),
            ("NUMBER", "+.4E+3", 29),
            ("NUMBER", ".4E3", 36),
        ],
    ],
    "complex": [
        "([POPULATION] > 50000 AND '[LANGUAGE9]' eq 'FRENCH')",
        [
            ("LBRAC", "(", 0),
            ("IDENTIFIER", "[POPULATION]", 1),
            ("OPERATOR", ">", 14),
            ("NUMBER", "50000", 16),
            ("LOGIC_OPERATOR", "AND", 22),
            ("STRING", "'[LANGUAGE9]'", 26),
            ("OPERATOR", "eq", 40),
            ("STRING", "'FRENCH'", 43),
            ("RBRAC", ")", 51),
        ],
    ],
    "single-quotes": [
        "('[LANGUAGE]' eq 'FRENCH2')",
        [
            ("LBRAC", "(", 0),
            ("STRING", "'[LANGUAGE]'", 1),
            ("OPERATOR", "eq", 14),
            ("STRING", "'FRENCH2'", 17),
            ("RBRAC", ")", 26),
        ],
    ],
    "double-quotes": [
        '("[LANGUAGE]" eq "FRENCH2")',
        [
            ("LBRAC", "(", 0),
            ("STRING", '"[LANGUAGE]"', 1),
            ("OPERATOR", "eq", 14),
            ("STRING", '"FRENCH2"', 17),
            ("RBRAC", ")", 26),
        ],
    ],
    "more-quotes": [
        "(`[CREATE_DATE]` gt `2021-02-03T14:53:22`)",
        [
            ("LBRAC", "(", 0),
            ("STRING", "`[CREATE_DATE]`", 1),
            ("OPERATOR", "gt", 17),
            ("STRING", "`2021-02-03T14:53:22`", 20),
            ("RBRAC", ")", 41),
        ],
    ],
    "quotes-quotes": [
        """("[LANGUAGE]" eq "FR 'w'2")""",
        [
            ("LBRAC", "(", 0),
            ("STRING", '"[LANGUAGE]"', 1),
            ("OPERATOR", "eq", 14),
            ("STRING", "\"FR 'w'2\"", 17),
            ("RBRAC", ")", 26),
        ],
    ],
    "operator": [
        "('[attr]' =* 'aa=(a)')",
        [
            ("LBRAC", "(", 0),
            ("STRING", "'[attr]'", 1),
            ("OPERATOR", "=*", 10),
            ("STRING", "'aa=(a)'", 13),
            ("RBRAC", ")", 21),
        ],
    ],
    "spaces": ["'   '", [("STRING", "'   '", 0)]],
}


@pytest.mark.parametrize("line, expected", [pytest.param(*v, id=k) for k, v in data.items()])
def test_tokens(line, expected):
    lexer.input(line)
    recived_tokens = get_tokens(line)
    check_token_eq(recived_tokens, expected)


@pytest.mark.parametrize(
    "value",
    [
        '"plain string"',
        "''",
        '""',
        "'   '",
        '"  "',
        """' "sdf" '""",
        '''" 'sdf' "''',
        "([POPULATION] > 50000 AND '[LANGUAGE]' eq 'FRENCH')",
        '( ("[LANG4]" ~ "FRENCH2") AND ([attr] gt 30) )',
        '( ("[LANG4]" ~ "FRENCH2") AND ([attr] gt 30) or ([attr1] lt 30) OR ([attr2] = 30))',
        "('[LANGUAGE]' lt '')",
        "( 3 < 4)",
        "( 3.4 < -4.3e+12)",
        "([attr] gt 30)",
        "([attr] gt 1.30)",
        "('[LANGUAGE]' eq 'FRENCH2')",
        '("[LANGUAGE]" eq "FRENCH2")',
        """("[LANGUAGE]" eq "FR 'w'2")""",
        '("[LANG4]" ~ "FRENCH2")',
        '("[LANG4]" ~ "<dsf\'!@$%^&*<>-:;,.?")',
    ],
)
def test_valid(value):
    parser.parse(value)


@pytest.mark.parametrize(
    "value",
    [
        "(aslgjkl)",
        "4",
        '"unbalanced quotes',
        "3 < 5",
        "([POPULATION])",
        "([LANGUAGE] lt '')",
        '("[L4]" ~ [L2])',
        '( ("[LANG4]" ~ "FRENCH2") AND [attr] gt 30) )',
    ],
)
def test_invalid(value):
    with pytest.raises((TokenNotRecognizedError, CharNotRecognizedError)):
        parser.parse(value)
