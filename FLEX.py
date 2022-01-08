import ply.lex as lex
import re


class LexerClass:

    reserved = {
        'int': 'INT',
        'short': 'SHORT',
        'bool': 'BOOL',
        'set': 'SET',
        'sizeof': 'SIZEOF',
        'add': 'ADD',
        'sub': 'SUB',
        'or': 'OR',
        'and': 'AND',
        'not': 'NOT',
        'begin': 'BEGIN',
        'end': 'END',
        'do': 'DO',
        'while': 'WHILE',
        'if': 'IF',
        'then': 'THEN',
        'else': 'ELSE',
        'move': 'MOVE',
        'right': 'RIGHT',
        'left': 'LEFT',
        'lms': 'LMS',
        'function': 'FUNCTION',
        'return': 'RETURN',
        'first': 'FIRST',
        'second': 'SECOND',
        'smaller': 'SMALLER',
        'larger': 'LARGER',
        'true': 'TRUE',
        'false': 'FALSE',
        'undefined': 'UNDEFINED'
    }

    tokens = [
        'INTLIT', 'SHORTLIT', 'STRLIT',
        'OPBR', 'CLBR', 'OPSQBR', 'CLSQBR', 'OPCUBR', 'CLCUBR',
        'ENDSTR',
        'NL',
        'COMMA', 'VECTOROF'
    ] + list(reserved.values())

    t_ignore = ' \t'

    def __init__(self):
        self.lexer = lex.lex(module=self)

    def input(self, smth):
        return self.lexer.input(smth)

    def token(self):
        return self.lexer.token()

    def t_VECTOROF(self, t):
        r'vector[ ]+of'
        return t

    def t_INTLIT(self, t):
        r'\-?[0-9]+'
        return t

    def t_SHORTLIT(self, t):
        r'\-?s[0-9]+'
        return t

    def t_STRLIT(self, t):
        r'\_?[a-z][\w]*'
        t.type = self.reserved.get(t.value, 'STRLIT')
        return t

    def t_OPBR(self, t):
        r'\('
        return t

    def t_CLBR(self, t):
        r'\)'
        return t

    def t_OPSQBR(self, t):
        r'\['
        return t

    def t_CLSQBR(self, t):
        r'\]'
        return t

    def t_OPCUBR(self, t):
        r'\{'
        return t

    def t_CLCUBR(self, t):
        r'\}'
        return t

    def t_COMMA(self, t):
        r'\,'
        return t

    def t_ENDSTR(self, t):
        r'\;'
        return t

    def t_NL(self, t):
        r'\n+'
        t.lexer.lineno += t.value.count('\n')
        return t

    def t_ANY(self, t):
        r'.+'
        return t

    def t_error(self, t):
        print("Illegal character '%s' " % t.value[0])
        t.lexer.skip(1)
        return t



if __name__ == '__main__':
    f = open('Programs/power.txt')
    data = f.read().lower()
    f.close()
    l = LexerClass()
    l.input(data)
    while True:
        tok = l.token()
        if not tok:
            break
        print(tok)
