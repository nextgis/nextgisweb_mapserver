# -*- coding: utf-8 -*-

'''Лексический анализатор
'''

import re
import ply.lex as lex


class CharNotRecognizedError(Exception):
    pass


tokens = (
    'NUMBER',
    'IDENTIFIER',
    'LOGIC_OPERATOR',
    'OPERATOR',
    'STRING_OPERATOR',
    #'QUOTE',
    #'DOUBLEQUOTE',
    'LBRAC',
    'RBRAC',
    'STRING'
)


t_NUMBER = r'[+-]?(\d+)?\.\d+([Ee][+-]?\d+)?|[+-]?\d+?\.([Ee][+-]?\d+)?|[+-]?\d+'
t_IDENTIFIER = r'\[[A-Z_]+[A-Z0-9_:-]*\]'
t_LOGIC_OPERATOR = r'(and)|(or)|(&&)|(\|)'
t_OPERATOR = r'(!=)|(>=)|(<=)|(<)|(>)|(=\*)|(=)|(lt)|(gt)|(ge)|(le)|(eq)|(ne)'
t_STRING_OPERATOR = r'(~\*)|(~)'
# t_QUOTE = ur"'"
# t_DOUBLEQUOTE = ur'"'
t_LBRAC = r'\('
t_RBRAC = r'\)'
t_STRING = r"('[^\']*')|(\"[^\"]*\")"


# Символы, которые будут игнорироваться
t_ignore = ' \t'


# Правило для обработки ошибок
def t_error(t):
    # err_char = t.value[0].decode('utf-8', 'replace')
    msg = "Illegal character"
    raise CharNotRecognizedError(msg)


# Лексический анализатор
lexer = lex.lex(reflags=re.IGNORECASE+re.UNICODE)


if __name__ == "__main__":
    # Тестирование

    ##########################
    # Вспомогательные функции
    ##########################
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

        # Tokenize
        while True:
            tok = lexer.token()
            # print tok
            if not tok:
                return tokens
            tokens.append(tok)

    def check_token_eq(token_list, expected_token_list):
        # print 'list:', token_list
        # print 'expd:', expected_token_list
        assert (len(token_list) == len(expected_token_list))

        expected_token_list = [
            _tuple_to_token(t) for t in expected_token_list
        ]
        for i in range(len(token_list)):
            token = token_list[i]
            expected = expected_token_list[i]
            # print 'recived ', token
            # print 'expected', expected
            assert (token.type == expected.type)
            assert (token.value == expected.value)
            assert (token.lexpos == expected.lexpos)

    #######################
    # Тесты
    #######################

    # data = {'входная строка': список ожидаемых токенов}
    data = {
		# Число:
		"-23 34.4 24 -4.5 +2.3E-1 -2. +.4E+3 .4E3":
		#u"-23 34.4":
			[
				('NUMBER', '-23', 0),
				('NUMBER', '34.4', 4),
				('NUMBER', '24', 9),
				('NUMBER', '-4.5', 12),
				('NUMBER', '+2.3E-1', 17),
				('NUMBER', '-2.', 25),
				('NUMBER', '+.4E+3', 29),
				('NUMBER', '.4E3', 36),
			],
        # Много разных токенов в одной строке
        "([POPULATION] > 50000 AND '[LANGUAGE9]' eq 'FRENCH')":
            [
                ('LBRAC', '(', 0),
                ('IDENTIFIER', '[POPULATION]', 1),
                ('OPERATOR', '>', 14),
                ('NUMBER', '50000', 16),
                ('LOGIC_OPERATOR', 'AND', 22),
                ('STRING', "'[LANGUAGE9]'", 26),
                ('OPERATOR', 'eq', 40),
                ('STRING', "'FRENCH'", 43),
                ('RBRAC', ')', 51)
            ],
        # Кавычки
        "('[LANGUAGE]' eq 'FRENCH2')":
            [
                ('LBRAC', '(', 0),
                ('STRING', "'[LANGUAGE]'", 1),
                ('OPERATOR', 'eq', 14),
                ('STRING', "'FRENCH2'", 17),
                ('RBRAC', ')', 26)
            ],
        # Двойные кавычки
        '("[LANGUAGE]" eq "FRENCH2")':
            [
                ('LBRAC', '(', 0),
                ('STRING', '"[LANGUAGE]"', 1),
                ('OPERATOR', 'eq', 14),
                ('STRING', '"FRENCH2"', 17),
                ('RBRAC', ')', 26)
            ],
        # Кавычки внутри строки
        '''("[LANGUAGE]" eq "FR 'w'2")''':
            [
                ('LBRAC', '(', 0),
                ('STRING', '"[LANGUAGE]"', 1),
                ('OPERATOR', 'eq', 14),
                ('STRING', '"FR \'w\'2"', 17),
                ('RBRAC', ')', 26)
            ],
        # Строковый оператор
        "('[attr]' =* 'aa=(a)')":
            [
                ('LBRAC', '(', 0),
                ('STRING', "'[attr]'", 1),
                ('OPERATOR', '=*', 10),
                ('STRING', "'aa=(a)'", 13),
                ('RBRAC', ')', 21)
            ],
        # Просто строка с пробелами
        "'   '":
            [
                ('STRING', "'   '", 0)
            ]
    }

    # Give the lexer some input
    for line, expected in data.items():
        print()
        print('line:', line)
        lexer.input(line)

        recived_tokens = get_tokens(line)
        # print 'Tokens', recived_tokens
        check_token_eq(recived_tokens, expected)
