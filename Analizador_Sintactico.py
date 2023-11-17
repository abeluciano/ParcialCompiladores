# ------------------------------------------------------------
# calclex.py
#
# tokenizer for a simple expression evaluator for
# numbers and +,-,*,/
# ------------------------------------------------------------
import ply.lex as lex

# r'atring' -> r significa que la cadena es tradada sin caracteres de escape,
# es decir r'\n' seria un \ seguido de n (no se interpretaria como salto de linea)

# List of token names.   This is always required
reserved = {
    'wl': 'WHILE',
    'for': 'FOR',
    'if': 'IF',
    'els': 'ELSE',
    'rt': 'RETURN',
    'func': 'FUNCION',
    'in': 'ENTRADA',
    'out': 'SALIDA',
    'of': 'OF',
    'do': 'DO',
    'elif': 'ILSE'
}

tokens = [
    'NUM', 'REAL', 'OPER_SUM', 'OPER_REST', 'OPER_MUL', 'OPER_DIV',
    'OPER_ASIG', 'PAR_INICIO', 'PAR_FIN', 'OPER_MODULO', 'ID', 'CARACTER',
    'CADENA', 'OPER_IGUAL', 'OPER_DIFERENT', 'OPER_MENOR', 'OPER_MAYOR',
    'OPER_MEN_IGUAL', 'OPER_MAY_IGUAL', 'OPER_AND', 'OPER_OR', 'KEY_INICIO',
    'KEY_FIN', 'DOSP', 'COMA', 'COMENTARIO', 'BOOLEANO', 'PCOMA'
] + list(reserved.values())

# Regular expression rules for simple tokens
t_OPER_SUM = r'\+'
t_OPER_REST = r'-'
t_OPER_MUL = r'\*'
t_OPER_DIV = r'/'
t_OPER_ASIG = r'\='
t_PAR_INICIO = r'\('
t_PAR_FIN = r'\)'
t_OPER_MODULO = r'\%'
t_OPER_IGUAL = r'\=='
t_OPER_DIFERENT = r'\!='
t_OPER_MENOR = r'\<'
t_OPER_MAYOR = r'\>'
t_OPER_MEN_IGUAL = r'\<='
t_OPER_MAY_IGUAL = r'\>='
t_OPER_AND = r'\&\&'
t_OPER_OR = r'\|\|'
t_KEY_INICIO = r'\{'
t_KEY_FIN = r'\}'
t_DOSP = r':'
t_COMA = r','
t_PCOMA = r';'

#/////////////////////////////////////////////////////////////


def t_REAL(t):
  r'\d+(\.\d+)'
  t.value = float(t.value)
  return t


def t_BOOLEANO(t):
  r'True|False'
  t.value = bool(t.value)
  return t


def t_ID(t):
  r'[a-zA-Z]+ ( [a-zA-Z0-9]* )'
  t.type = reserved.get(t.value, 'ID')
  return t


def t_COMENTARIO(t):
  r'\/\/.*|\/\*[\s\S]*\*\/'
  return t


def t_CADENA(t):
  r'".*"'
  t.value = str(t.value)
  return t


def t_NUM(t):
  r'\d+'
  t.value = int(t.value)
  return t


def t_CARACTER(t):
  r'\'.\''
  t.value = str(t.value)
  return t


def t_newline(t):
  r'\n+'
  t.lexer.lineno += len(t.value)


t_ignore = ' \t'


def t_error(t):
  print("Illegal character '%s'" % t.value[0])
  t.lexer.skip(1)


lexer = lex.lex()

archivo = open("ejemplo2.txt", "r")
data = archivo.read()
archivo.close()

lexer.input(data)

lista_tokens = []

while True:
  tok = lexer.token()
  if not tok:
    break
  info_token = {
      "symbol": tok.type,
      "lexeme": tok.value,
      "nroline": tok.lineno,
      "col": tok.lexpos
  }
  lista_tokens.append(info_token)
nuevo_token = {"symbol": "$", "lexeme": "$", "nroline": 0, "col": 0}
lista_tokens.append(nuevo_token)