# !/usr/bin/env python
# -*- coding: utf-8 -*-
# /


#! CUIDADO
#todo por hacer
#? aviso
#* explicación


import sqlite3
import tkinter as tk
from xml.dom.minidom import parseString
from gazpacho import Soup
import re
import os


def sql_insert(con, datos):
    cursorObj = con.cursor()
    cursorObj.execute(
        'INSERT INTO hemeroteca(titular, url, imagen, tipo, contenido) VALUES(?, ?, ?, ?, ?)', datos)
    con.commit()


#* creamos la ventana
def foo(root, texto):
    #print('con este texto "{}" hago lo que quiero'.format(texto))
    root.quit()
    root.destroy()

root = tk.Tk()
root.title("Introduce la noticia para ingresarla en la bbdd mysl")
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

os.system('clear')


#* analizamos la noticia
#resultado = resultado.replace("'", "**comilla simple**")
resultado = Soup(resultado)
resultado_raw = str(resultado)

#* tipo de noticia
if '#881288' in resultado_raw:
    tipo = 'p'
else:
    tipo = 'g'


#*sacamos el título
try:
    titulo = resultado.find('td', attrs={'class': 'heading'})
    titulo = titulo.text
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
    contenido = contenido.text
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
print('##Trabajo en la bbdd##')
print('')
print(titulo)
print(url[0])
print(imagen[0])
print(tipo)
print(contenido)
