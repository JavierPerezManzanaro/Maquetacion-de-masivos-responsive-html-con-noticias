# !/usr/bin/env python
# -*- coding: utf-8 -*-
# /


#! CUIDADO
#todo por hacer
#? aviso
#* explicación


import sqlite3
import tkinter as tk
from gazpacho import Soup
# https://github.com/maxhumber/gazpacho
# https://pypi.org/project/gazpacho/
import re
import os
os.system('clear')


def sql_insert(con, datos):
    cursorObj = con.cursor()
    cursorObj.execute(
        'INSERT INTO hemeroteca(titular, url, imagen, tipo, contenido) VALUES(?, ?, ?, ?, ?)', datos)
    con.commit()


def limpiar_html(cadena):
    """Limpia el html obtenido de retornos y espacios

    Args:
        cadena ([str]): html raw

    Returns:
        [str]: cadena str limpia
    """
    cadena = str(cadena)
    cadena = cadena.replace("<p>", "")
    cadena = cadena.replace("</p>", "")
    cadena = cadena.replace("\n", "")
    cadena = cadena.replace("\r", "")
    cadena = cadena.replace("  ", "")
    cadena = cadena.strip()
    return cadena


#* creamos la ventana
def foo(root, texto):
    root.quit()
    root.destroy()

root = tk.Tk()
root.title("Introduce la noticia para ingresarla en la bbdd sqlite3")
root.geometry("600x400")


def getTextInput():
   global resultado
   resultado = ventana.get("1.0", tk.END+"-1c")
   foo(root, resultado)


ventana = tk.Text(root, height=25)
ventana.pack()
btnRead = tk.Button(root, height=2, width=50, text="Introducir en la bbdd", command=getTextInput)
btnRead.pack()
root.mainloop()


#* analizamos la noticia
resultado = Soup(resultado)
resultado_raw = str(resultado)

#* tipo de noticia
# if '#881288' in resultado_raw:
#     tipo = 'p'
# else:
#     tipo = 'g'
# formato ternario: <bloque_true> if <condición> else <bloque_false>
tipo = 'p' if ('#881288' in resultado_raw) else 'g'

#*sacamos el título
try:
    titulo = resultado.find('td', attrs={'class': 'heading'})
    titulo = titulo.html
    titulo = titulo[(titulo.find('>')+1):-5]
    titulo = limpiar_html(titulo)


except:
    titulo = input("¿Introduce el título ? ")


#*sacamos la url
try:
    url = re.findall(
        'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', resultado_raw)
except:
    url = input("¿Introduce la url de destino? ")

#*sacamos el contenido
try:
    contenido = resultado.find('td', attrs={'class': 'MsoNormal'})
    contenido = contenido.html
    contenido = contenido[(contenido.find('>')+1):-5]
    contenido = limpiar_html(contenido)
except:
    contenido = input("¿Introduce el contenido de la noticia? ")

#*sacamos la url de la imagen
try:
    patron = "< *[img][^>]*[src] *= *[\"\']{0,1}([^\"\' >]*)"
    imagen = re.findall(patron, resultado_raw)
except:
    imagen = input("¿Introduce la url de la imagen? ")

#* conexión bbdd y metemos noticia
con = sqlite3.connect('bbdd.sqlite3')
datos = (titulo, url[0], imagen[0], tipo, contenido)
sql_insert(con, datos)

#* mostramos la información
print('## Trabajo en la bbdd ##')
print()
print(f'{titulo=}')
print(f'{url[0]=}')
print(f'{imagen[0]=}')
print(f'{tipo=}')
print(f'{contenido=}')
print()
print()
