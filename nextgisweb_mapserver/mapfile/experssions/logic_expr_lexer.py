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
    #'UNARY_OPERATOR',
    'LOGIC_OPERATOR',
    'NUMERIC_OPERATOR',
    'STRING_OPERATOR',
    'QUOTE',
    'LBRAC',
    'RBRAC',
    'STRING'
)

t_NUMBER = ur'[0-9]+'
t_IDENTIFIER = ur'\[[A-Z_]+[A-Z0-8]*\]'
# t_UNARY_OPERATOR = ur'length'
t_LOGIC_OPERATOR = ur'(and)|(or)'
t_NUMERIC_OPERATOR = ur'(>=)|(<=)|(<)|(>)|(=)'
t_STRING_OPERATOR = ur'(lt)|(gt)|(ge)|(le)|(eq)|(ne)'
t_QUOTE = ur"'"
t_LBRAC = ur'\('
t_RBRAC = ur'\)'
t_STRING = ur"'[A-Za-z_,./!@#$%^&*()]*'"


# Символы, которые будут игнорироваться
t_ignore = u' \t'


# Правило для обработки ошибок
def t_error(t):
    # err_char = t.value[0].decode('utf-8', 'replace')
    print t
    msg = u"Illegal character"
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

        return token

    def get_tokens(house_number):
        tokens = []
        lexer.input(house_number)

        # Tokenize
        while True:
            tok = lexer.token()
            if not tok:
                return tokens
            tokens.append(tok)

    def check_token_eq(token_list, expected_token_list):
        assert (len(token_list) == len(expected_token_list))

        expected_token_list = [
            _tuple_to_token(t) for t in expected_token_list
        ]
        for i in range(len(token_list)):
            token = token_list[i]
            expected = expected_token_list[i]
            assert (token.type == expected.type)
            assert (token.value == expected.value)
            assert (token.lexpos == expected.lexpos)

    #######################
    # Тесты
    #######################

    # data = {'входная строк    а': список ожидаемых токенов}
    data = {
        u"([POPULATION] > 50000 AND '[LANGUAGE]' eq 'FRENCH')":
            [
                ('LBRAC', u'(', 0),
                ('IDENTIFIER', u'[POPULATION]', 1),
                ('NUMERIC_OPERATOR', u'>', 14),
                ('NUMBER', u'50000', 16),
                ('LOGIC_OPERATOR', u'AND', 22),
                ('QUOTE', u"'", 26),
                ('IDENTIFIER', u'[LANGUAGE]', 27),
                ('QUOTE', u"'", 37),
                ('STRING_OPERATOR', u'eq', 39),
                ('STRING', u"'FRENCH'", 42),
                ('RBRAC', u')', 50)
            ],
        u"([SIZE] < 8)":
            [
                ('LBRAC', u'(', 0),
                ('IDENTIFIER', u'[SIZE]', 1),
                ('NUMERIC_OPERATOR', u'<', 8),
                ('NUMBER', u'8', 10),
                ('RBRAC', u')', 11)
            ]
    }

    # Give the lexer some input
    for line, expected in data.iteritems():
        print
        print 'line:', line
        lexer.input(line)

        recived_tokens = get_tokens(line)
        # print 'Tokens', recived_tokens
        check_token_eq(recived_tokens, expected)



