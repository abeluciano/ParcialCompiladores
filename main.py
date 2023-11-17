import pandas as pd
import Analizador_Sintactico as ans
import sys


class NodeStack:

  def __init__(self, symbol, lexeme):
    global count
    self.symbol = symbol
    self.lexeme = lexeme
    self.id = count + 1
    count += 1


class NodeTree:

  def __init__(self, id, symbol, lexeme):
    self.id = id
    self.symbol = symbol
    self.lexeme = lexeme
    self.children = []
    self.father = None


def buscar_node(root_node, target_id):
  stack = [root_node]
  while stack:
    current_node = stack.pop()
    if current_node.id == target_id:
      return current_node
    stack.extend(current_node.children)
  return None


tabla = pd.read_csv("tabla.csv", index_col=0)
count = 0
stack = []
Xtack = []
# Inicializa la pila
symbol_K = NodeStack('K', None)
symbol_dollar = NodeStack('$', None)
stack.append(symbol_dollar)
stack.append(symbol_K)

# Inicializa el árbol
root = NodeTree(symbol_K.id, symbol_K.symbol, symbol_K.lexeme)

input = ans.lista_tokens

if (stack[-1].symbol not in tabla.index
    or input[0]["symbol"] not in tabla.columns):
  print("\nLa gramatica es incorrecta")
else:
  while len(stack) > 0:

    if stack[-1].symbol == '$' and input[0]["symbol"] == '$':
      print("\nLa gramatica es correcta\n")
      break

    if stack[-1].symbol == input[0]["symbol"]:

      node_actual = buscar_node(root, stack[-1].id)
      node_actual.lexeme = input[0]["lexeme"]

      input.pop(0)
      stack.pop()
      continue
    elif stack[-1].symbol not in tabla.index:
      print("Error sintactico en linea:", input[0]["nroline"])
      break

    production = tabla.loc[stack[-1].symbol, input[0]["symbol"]]

    if production != 'e':
      production_terms = production.split()
      node_p = stack.pop()
      for term in reversed(production_terms):

        if term == input[0]["symbol"]:
          #print(term , input[0]["symbol"] )
          new_node = NodeStack(term, input[0]["lexeme"])
          node_h = NodeTree(new_node.id, new_node.symbol, new_node.lexeme)
          node_father = buscar_node(root, node_p.id)
          node_father.children.append(node_h)
          node_h.father = node_father
          stack.append(new_node)
        else:
          new_node = NodeStack(term, " ")
          new_node_tree = NodeTree(new_node.id, new_node.symbol,
                                   new_node.lexeme)
          node_father = buscar_node(root, node_p.id)
          node_father.children.append(new_node_tree)
          new_node_tree.father = node_father
          stack.append(new_node)

    elif production == ' ':
      print("Error sintactico en linea:", input[0]["nroline"])

    elif production == 'e':
      node_p = stack.pop()
      new_node = NodeStack("e", "e")
      node_h = NodeTree(new_node.id, new_node.symbol, new_node.lexeme)
      node_father = buscar_node(root, node_p.id)
      node_father.children.append(node_h)
      node_h.father = node_father
      continue

# Define una lista para almacenar todos los nodos "ID" encontrados
id_nodes_list = []


# Función de recorrido del árbol para agregar todos los nodos "ID" a la lista
def traverse_tree(node, ambito=None, flag=None):
  if node.symbol == "ID":
    if node.father.symbol == "V" and node.father.father.symbol == "R":
      flag = "variable"
      ambito = node.father.father.children[8].lexeme
    elif node.father.symbol == "V" and node.father.father.symbol == "Ñ" and node.father.father.father.symbol == "V":
      temp_node = node
      while temp_node.symbol != "R":
        temp_node = temp_node.father
      ambito = temp_node.children[8].lexeme
      flag = "variable"
    elif node.father.symbol == "J" and node.father.father.symbol == "M" and node.father.father.father.symbol == "K" and node.father.father.father.father.symbol == "M":
      temp_node = node
      while temp_node.symbol != "R":
        temp_node = temp_node.father
        if temp_node.symbol == "M" and temp_node.father.symbol == "R":
          ambito = temp_node.father.children[8].lexeme
        if temp_node.symbol == "K" and temp_node.father.symbol == "R":
          ambito = "global"
      flag = "variable"
    elif node.father.symbol == "J" and node.father.father.symbol == "M" and node.father.father.father.symbol == "K":
      ambito = "global"
      flag = "variable"
    elif node.father.symbol == "J" and node.father.father.symbol == "M" and node.father.father.father.symbol == "R":
      ambito = node.father.father.father.children[8].lexeme
      flag = "variable"
    elif node.father.symbol == "V" and node.father.father.symbol == "Z":
      ambito = "funcion"
      flag = "variable"
    elif node.father.symbol == "R":
      return
    elif node.father.symbol == "M" and node.father.father.symbol == "R":
      return
    elif node.father.symbol == "F":
      if node.father.father.symbol == "T" and node.father.father.father.symbol == "E" and node.father.father.father.symbol == "A":
        ambito = "global"
        flag = "funcion"

      return
    id_nodes_list.append({
        "lexeme": node.lexeme,
        "ambito": ambito,
        "flag": flag
    })

  for child in reversed(node.children):
    traverse_tree(child, ambito, flag)


# Llama a la función de recorrido del árbol en el nodo raíz
traverse_tree(root)

# Define un diccionario para almacenar los nodos "ID" encontrados
id_nodes_dict = {}


def traverse_tree_dict(node):
  if node.symbol == "R":
    for child in node.children:
      if child.symbol == "ID":
        if child.lexeme in id_nodes_dict:
          print("Error semántico: Una funcion ya esta definida")
          exit(1)
        id_nodes_dict[child.lexeme] = {
            "lexeme": child.lexeme,
            "ambito": "global",
            "flag": "funcion"
        }
  for child in node.children:
    traverse_tree_dict(child)


traverse_tree_dict(root)

# Combina los nodos "ID" del diccionario en la lista
for lexeme, attributes in id_nodes_dict.items():
  id_nodes_list.append(attributes)

# Imprime la lista con todos los nodos "ID" encontrado
#for attributes in id_nodes_list:
#print(f"Lexeme: {attributes['lexeme']}")
#print(f"Ámbito: {attributes['ambito']}")
#print(f"Flag: {attributes['flag']}")
#print("----")


def definir_tipo(node, var_types=None):
  if var_types is None:
    var_types = {}
  var_type = None
  if node.symbol == "ID":
    if (node.father.symbol == "J" and node.father.children[2].symbol == "A"
        and node.father.children[2].children[0].symbol == "E"
        and node.father.children[2].children[0].children[0].children[0].symbol
        == "e"
        and node.father.children[2].children[0].children[1].symbol == "T" and
        node.father.children[2].children[0].children[-1].children[-1].symbol
        == "F" and node.father.children[2].children[0].children[-1].
        children[-1].children[0].symbol == "NUM"):
      var_type = 'int'
    elif (
        node.father.symbol == "J" and node.father.children[2].symbol == "A"
        and node.father.children[2].children[0].symbol == "E"
        and node.father.children[2].children[0].children[0].children[0].symbol
        == "e"
        and node.father.children[2].children[0].children[1].symbol == "T" and
        node.father.children[2].children[0].children[-1].children[-1].symbol
        == "F" and node.father.children[2].children[0].children[-1].
        children[-1].children[0].symbol == "CADENA"):
      var_type = 'string'
    elif (
        node.father.symbol == "J" and node.father.children[2].symbol == "A"
        and node.father.children[2].children[0].symbol == "E"
        and node.father.children[2].children[0].children[0].children[0].symbol
        == "e"
        and node.father.children[2].children[0].children[1].symbol == "T" and
        node.father.children[2].children[0].children[-1].children[-1].symbol
        == "F" and node.father.children[2].children[0].children[-1].
        children[-1].children[0].symbol == "REAL"):
      var_type = 'float'
    elif (
        node.father.symbol == "J" and node.father.children[2].symbol == "A"
        and node.father.children[2].children[0].symbol == "E"
        and node.father.children[2].children[0].children[0].children[0].symbol
        == "e"
        and node.father.children[2].children[0].children[1].symbol == "T" and
        node.father.children[2].children[0].children[-1].children[-1].symbol
        == "F" and node.father.children[2].children[0].children[-1].
        children[-1].children[0].symbol == "CARACTER"):
      var_type = 'char'
    elif (
        node.father.symbol == "J" and node.father.children[2].symbol == "A"
        and node.father.children[2].children[0].symbol == "E"
        and node.father.children[2].children[0].children[0].children[0].symbol
        == "e"
        and node.father.children[2].children[0].children[1].symbol == "T" and
        node.father.children[2].children[0].children[-1].children[-1].symbol
        == "F" and node.father.children[2].children[0].children[-1].
        children[-1].children[0].symbol == "BOOLEANO"):
      var_type = 'bool'
    elif (
        node.father.symbol == "J" and node.father.children[2].symbol == "A"
        and node.father.children[2].children[0].symbol == "E"
        and node.father.children[2].children[0].children[0].children[0].symbol
        == "e"
        and node.father.children[2].children[0].children[1].symbol == "T" and
        node.father.children[2].children[0].children[-1].children[-1].symbol
        == "F" and node.father.children[2].children[0].children[-1].
        children[-1].children[0].symbol == "ID"):

      node_comparado = node.father.children[2].children[0].children[
          -1].children[-1].children[0].lexeme
      if node_comparado in var_types:
        var_type = var_types[node_comparado]["var_type"]
      else:
        # Si el ID no existe en el diccionario, mostrar mensaje de error sintáctico
        print(
            f"Error sintáctico: Variable '{node_comparado}' no definida previamente."
        )
        exit(1)
    elif (
        node.father.symbol == "J" and node.father.children[2].symbol == "A"
        and node.father.children[2].children[0].symbol == "E"
        and node.father.children[2].children[0].children[0].children[0].symbol
        == "E'"):
      temp_node = node.father.children[2].children[0].children[0].children[0]
      while temp_node.symbol != "e":
        temp_node = temp_node.children[0]
      node_e = temp_node.father.father
      if (node_e.children[2].symbol == "OPER_SUM"
          or node_e.children[2].symbol == "OPER_MUL"
          or node_e.children[2].symbol == "OPER_REST"
          or node_e.children[2].symbol == "OPER_DIV"):
        var_subtype = None
        while node_e.father.symbol == "E'":
          var_subtype1 = var_subtype

          if node_e.children[1].children[1].children[0].symbol == "NUM":
            var_subtype = 'int'
          elif node_e.children[1].children[1].children[0].symbol == "REAL":
            var_subtype = 'float'
          elif (node_e.children[1].children[1].children[0].symbol == "CADENA"
                or node_e.children[1].children[1].children[0].symbol
                == "CARACTER"
                or node_e.children[1].children[1].children[0].symbol
                == "BOOLEANO"):
            print("Error sintáctico:")
            exit(1)
          if var_subtype1 == 'float' and var_subtype == 'int':
            var_subtype == 'float'
          node_e = node_e.father
        if (node.father.children[2].children[0].children[-1].children[-1].
            children[0].symbol == "NUM" and var_subtype == 'int'):
          var_type = 'int'
        elif (node.father.children[2].children[0].children[-1].children[-1].
              children[0].symbol == "NUM" and var_subtype == 'float'):
          var_type = 'float'
        elif (node.father.children[2].children[0].children[-1].children[-1].
              children[0].symbol == "REAL" and var_subtype == 'int'):
          var_type = 'float'
        elif (node.father.children[2].children[0].children[-1].children[-1].
              children[0].symbol == "REAL" and var_subtype == 'float'):
          var_type = 'float'
        elif (node.father.children[2].children[0].children[-1].children[-1].
              children[0].symbol == "CADENA"
              or node.father.children[2].children[0].children[-1].children[-1].
              children[0].symbol == "CARACTER"
              or node.father.children[2].children[0].children[-1].children[-1].
              children[0].symbol == "BOOLEANO"):
          print("Error sintáctico:")
          exit(1)
      else:
        print("Error sintáctico:")
        exit(1)
    else:
      return
    var_types[node.lexeme] = {
        #"lexeme": node.lexeme,
        "var_type": var_type
    }

  for child in reversed(node.children):
    definir_tipo(child, var_types)


var_types = {}
definir_tipo(root, var_types)
print(var_types)


def printfrom_tree(node, productions=[], gramar=[]):
  if node is None:
    return
  if node.father is not None:
    grama = f" \"{node.father.symbol}_{node.father.id}\"[label=\"{node.father.symbol}\\n{node.father.lexeme}\"][style=filled, fillcolor=yellow, label=\"{node.father.symbol}\"] \n \"{node.symbol}_{node.id}\"[label=\"{node.symbol}\\n{node.lexeme}\"]"
    gramar.append(grama)
    production = f" \"{node.father.symbol}_{node.father.id}\"  -> \"{node.symbol}_{node.id}\""
    productions.append(production)
  for child in node.children:
    printfrom_tree(child, productions, gramar)
  if not node.children:
    # Aplicar estilo solo a las hojas
    leaf_grama = f"\"{node.symbol}_{node.id}\" [style=filled, fillcolor=green, label=\"{node.symbol}\"]"
    gramar.append(leaf_grama)


def printto_file(node, filename):
  productions = []
  gramar = []
  printfrom_tree(node, productions, gramar)
  productions.reverse()
  gramar.reverse()

  with open(filename, "w") as file:
    for grama in gramar:
      file.write(grama + '\n')
    for production in productions:
      file.write(production + '\n')


output_filename = "graphviz.txt"
printto_file(root, output_filename)
