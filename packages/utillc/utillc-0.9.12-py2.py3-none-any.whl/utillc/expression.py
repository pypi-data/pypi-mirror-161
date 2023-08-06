

# -----------------------------------------------------------------------------
# calc.py
#
# A simple calculator with variables -- all in one file.
# -----------------------------------------------------------------------------

tokens = (
    'NAME','NUMBER',
    'PLUS','MINUS','TIMES','DIVIDE','EQUALS',
    'LPAREN','RPAREN', 'COMMA', 'EKON', 'STRING', 'RBRACKET', 'LBRACKET'
    )

# Tokens
t_EKON    = r'EKON'
t_COMMA    = r'\,'
t_PLUS    = r'\+'
t_MINUS   = r'-'
t_TIMES   = r'\*'
t_DIVIDE  = r'/'
t_EQUALS  = r'='
t_LPAREN  = r'\('
t_RPAREN  = r'\)'
t_LBRACKET  = r'\['
t_RBRACKET  = r'\]'
t_NAME    = r'[a-zA-Z_][a-zA-Z0-9_]*'

t_STRING  = r'\"([^\\\"]|\\.)*\"' + '|' +  r"\'([^\\\']|\\.)*\'" 

def t_NUMBER(t):
    r'\d+'
    try:
        t.value = int(t.value)
    except ValueError:
        print("Integer value too large %d", t.value)
        t.value = 0
    return t

# Ignored characters
t_ignore = " \t"

def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")
    
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)
    
# Build the lexer
import ply.lex as lex
lexer = lex.lex()

# Parsing rules

precedence = (
    ('left','PLUS','MINUS'),
    ('left','TIMES','DIVIDE'),
    ('right','UMINUS'),
    )

# dictionary of names
names = { }

def p_top(t) :
    'top : expressions'
    t[0] = t[1]

def p_expressions_1(t) :
    'expressions : expression'
    t[0] = t[1]

def p_expressions_2(t) :
    'expressions : expressions COMMA expression'
    t[0] =  ( ',', t[1], t[3])

def p_expression_binop(t):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression'''
    t[0] = (t[2], t[1], t[3])

def p_expression_uminus(t):
    'expression : MINUS expression %prec UMINUS'
    t[0] = ('-', "", t[2])

def p_expression_group(t):
    '''expression : LPAREN expressions RPAREN
                  | NAME LBRACKET expressions RBRACKET
                  | NAME LPAREN expressions RPAREN
    '''
    if t[1] == '(' :
        t[0] = ("", '(', t[2])
    elif t[2] == '[' :
        t[0] = (t[1], '[', t[3])
    else:
        t[0] = (t[1], '(', t[3])
def p_expression_number(t):
    'expression : NUMBER'
    t[0] = str(t[1])

def p_expression_name(t):
    'expression : NAME'
    t[0] = t[1]

def p_expression_string(t):
    'expression : STRING'
    t[0] = t[1]

def p_error(t):
    print("Syntax error at '%s'" % t.value)


def tostr(x) :
    if isinstance(x, str) :
        return x
    else :
        return x[0] + ','.join(map(tostr, x[1]))

inv = { '(' : ')',
        '[' : ']'}

__all__ = ('listp', 'dump', 'parse')

def listp(e) :
    if isinstance(e, tuple) and e[0] == ',' :
        return listp(e[1]) + [e[2]]
    else :
        return [e]
    

def dump(e) :
    if isinstance(e, str) :
        return e
    elif e[0] in [',', "+", "-", "*", "/"] :
        return dump(e[1]) + " " + e[0] + " " + dump(e[2])
    else :
        return e[0] + e[1] + dump(e[2]) + inv[e[1]]

import ply.yacc as yacc
parser = yacc.yacc()


def parse(s) :
    e = parser.parse(s)
    return e
