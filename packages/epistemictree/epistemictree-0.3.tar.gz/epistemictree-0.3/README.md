# Epistemic tree
## Índice
* [Introducción](#introducción)
* [Lenguaje](#lenguaje)
* [Interfaz](#Interfaz)

## Introducción
Este proyecto es el resultado del trabajo fin de máster realizado por Carlos
Agiulera Ventura.

## Lenguaje
| Símbolo | Fórmula      | Ejemplo |
|---------|--------------|---------|
| &&      | Conjunción   | p&&q    |
| ||      | Disyunción   | p||q    |
| =>      | Implicación  | p=>q    |
| Ka      | Conocimiento | Kap     |

El conjunto de átomos se define como [p-z] y el conjunto de átomos a1,a2,...,an.

## Interfaz
### Consola
El programa se ejecuta como modulo python. Para utilizarla se introduce un
conjunto de premisas, que puede ser vacío, y la conclusión. Una vez ejecutamos
el programa, se crea la imagen del árbol generado y, en caso de que sea posible,
construye un contramodelo.

<p align="center">
  <img src="lib/img/tree.png" alt="Tree">
</p>

### Vim
También puede utilizarse dentro de editores de texto para LaTeX. En este caso,
se muestra un ejemplo del funcionamiento para Neovim. 

<p align="center">
  <img src="lib/img/vim.gif" alt="vim">
</p>

