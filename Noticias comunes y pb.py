#!/usr/bin/env python
# -*- coding: utf-8 -*-
# /


#! CUIDADO
#todo por hacer
#? aviso
#* explicación


from datetime import datetime
from os import link
from wordpress_xmlrpc import Client
from wordpress_xmlrpc.methods import posts
import requests
import os
import re
from PIL import Image
from pprint import pprint
#import pyperclip as clipboard
import errno

# liberias propias
#import pb
import bloques

#todo: tratar bbdd como ORM



longitud_de_noticia = 400
noticias_mostradas = 30
imagen_local = ''
ancho = 0
alto = 0

noticias_colocadas = []
posicion = 1


def strip_tags(value):
    value = re.sub(r'<[^>]*?>', ' ', value) # elimina <...>
    value = re.sub(r'\[[^>]*?\]', ' ', value) # elimina [...]
    return value


def descarga_imagen(imagen_red, ancho_px):
    """Descarga las imagenes y las ajusta al tamaño

    Args:
        imagen_red (str): es la url: axon[noticia]['imagen']
        ancho_px (int): ancho a usar

    Returns:
        [type]: el nombre de la imagen, alto y ancho
    """
    #* extension del archivo
    try:
        imagen_red = str(axon[noticia]['imagen'])
        extension = imagen_red[len(imagen_red)-4:len(imagen_red)]
        if extension == "jpeg":
            extension = ".jpg"
        else:
            pass
        imagen_local = nombre_archivo+'/'+str(noticia)+extension
        #! abra que usar  str(boletin)+"c/"+
        #descargamos la imagen
        imagen = requests.get(imagen_red).content
        with open(imagen_local, 'wb') as handler:
            handler.write(imagen)
        # tratamos la imagen para Mostrar imagenes imagen.show()
        imagen = Image.open(imagen_local)
    except:
        #todo: no abria que poner este error PIL.UnidentifiedImageError:
        imagen_local = 'spacer.gif'
        imagen = Image.open(imagen_local)
    finally:
        imagen.convert("RGB")
        alto = int((int(imagen.size[1]) * ancho_px) / int(imagen.size[0]))
        imagen = imagen.resize((ancho_px, alto))
        ancho = ancho_px
        imagen.save(imagen_local)
        #print(f"Tamaño actual horizontal/vertical: {imagen.size[0]}px x {imagen.size[1]}px")
    return imagen_local, ancho, alto




os.system('clear')


boletin = int(input("¿Qué número de InformaVet es? "))
print()


#* creamos la carpeta
nombre_archivo = str(boletin)+'c'
try:
    os.mkdir(nombre_archivo)  # (nombre_archivo+'c')
except OSError as e:
    print("Borrando carpeta anterior.")
    if e.errno != errno.EEXIST:
        raise


#* noticias de axon
usuario = "Javier"
contrasena = "clave98745_li"
sitio = "https://axoncomunicacion.net/xmlrpc.php"
cliente = Client(sitio, usuario, contrasena)
axon_entradas = cliente.call(posts.GetPosts(
    {'number': noticias_mostradas, 'offset': 0,  'post_status': 'publish'}))  # 'orderby': 'title',
#todo: ordenar por nombre
print(f"Últimas {noticias_mostradas} noticias de Axón comunicación")
print("Nº | Título")
print("---|------------------------------------------------------------")
print(" 0 | Dejar hueco")
#* creados diccionario con la entrada 0, el hueco y mostramos la tabla
numero = 1
url = 'nulo'
axon = {}
axon[0] = {'id': 0, 'url': 'https://axoncomunicacion.net', 'imagen': 'https://axoncomunicacion.net/masivos/spacer.gif',
             'titulo': 'vacio', 'contenido': '&nbsp;'}
if len(axon_entradas) > 0:
    for entrada in axon_entradas:
        print(f"{numero:>2} | {entrada.title[0:120]}")
        # sacamos la url de la imagen
        imagen = re.findall('img .*?src="(.*?)"', entrada.content)
        imagen = imagen[0]
        # tratamos el contenido de la entrada
        #contenido_bruto = entrada.content
        contenido_bruto = strip_tags(entrada.content)
        contenido_bruto = contenido_bruto[0:longitud_de_noticia] + '... '
        # asignamos el array
        axon[numero] = {'id': entrada.id, 'url': entrada.link,
                        'imagen': imagen, 'titulo': entrada.title, 'contenido': contenido_bruto}
        numero += 1

        # print('''
        # ID: {}
        # Título: {}
        # Contenido: {}'''.format(entrada.id, entrada.title, entrada.content))
        # input("Presiona ENTER para ver la siguiente entrada")
else:
    print("No hay entradas para mostrar")


#* gestión de comienzo
meses = {
    "1": 'Enero',
    "2": 'Febrero',
    "3": 'Marzo',
    "4": 'Abril',
    "5": 'Mayo',
    "6": 'Junio',
    "7": 'Julio',
    "8": 'Agosto',
    "9": 'Septiembre',
    "10": 'Octubre',
    "11": 'Noviembre',
    "12": 'Diciembre'
}
ahora = datetime.now()
dia = ahora.day

print()
print()

#* gestionamos la cabecera
comienzo_en_curso = bloques.comienzo
comienzo_en_curso = comienzo_en_curso.replace('##nombre_archivo##', nombre_archivo)
comienzo_en_curso = comienzo_en_curso.replace('##numero##', str(boletin))
comienzo_en_curso = comienzo_en_curso.replace('##mes##', meses[str(ahora.month)])
#todo: añadir año


#* gestión de noticia destacada
noticia = int(input("¿Qué noticia es la destacada? "))
if noticia != 0:
    noticia_destacada = bloques.noticia_destacada
    imagen_local, ancho, alto = descarga_imagen(axon[noticia]['imagen'], 320)
    noticia_destacada = noticia_destacada.replace('##nombre_archivo##', nombre_archivo)
    noticia_destacada = noticia_destacada.replace('##imagen##', str(imagen_local))
    noticia_destacada = noticia_destacada.replace('##ancho##', str(ancho))
    noticia_destacada = noticia_destacada.replace('##alto##', str(alto))
    noticia_destacada = noticia_destacada.replace('##contenido##', axon[noticia]['contenido'])
    noticia_destacada = noticia_destacada.replace('##noticia_enlace##', axon[noticia]['url'])    # entrada.link)
    noticia_destacada = noticia_destacada.replace('##noticia_titular##', axon[noticia]['titulo'])    # entrada.title)
else:
    noticia_destacada = ''



#* gestión del resto de noticias
noticias = input("¿Qué noticias quieres publicar (separadas con espacios)? ")

noticias = noticias.split(' ')
izquierda = True
for noticia in noticias:
    noticia = int(noticia)
    imagen_local, ancho, alto = descarga_imagen(axon[noticia]['imagen'], 320)
    # tabla impar, a la izquierda = left
    # tabla par, a la derecha = right
    if izquierda == True:
        localizacion = 'left'
        izquierda = False
        #print(f'izq: {localizacion}')
    else:
        localizacion = 'right'
        izquierda = True
        #print(f'derc: {localizacion}')

    noticia_en_curso = bloques.noticia_raw
    noticia_en_curso = noticia_en_curso.replace('##posicion##', str(localizacion))
    noticia_en_curso = noticia_en_curso.replace('###numero##', str(boletin))
    noticia_en_curso = noticia_en_curso.replace('##imagen##', str(imagen_local))
    noticia_en_curso = noticia_en_curso.replace('##ancho##', str(ancho))
    noticia_en_curso = noticia_en_curso.replace('##alto##', str(alto))
    noticia_en_curso = noticia_en_curso.replace('##noticia_texto##', axon[noticia]['contenido'])
    noticia_en_curso = noticia_en_curso.replace('##noticia_enlace##', axon[noticia]['url'])    # entrada.link)
    noticia_en_curso = noticia_en_curso.replace('##noticia_titular##', axon[noticia]['titulo'])    # entrada.title)
    noticias_colocadas.append(noticia_en_curso) # es una lista


longitud = len(noticias_colocadas)
print(f"Noticias generadas: {longitud}")

#* generamos el bloque general de las noticias
numero = 0

# #* creamos el último si es impar
ultimo_si_es_impar = ''
if longitud % 2 != 0:
    ultimo_si_es_impar = bloques.bloque_exterior
    ultimo_si_es_impar = ultimo_si_es_impar.replace(
        '##bloque izq##', noticias_colocadas[-1], 1)  # usamos el último
    ultimo_si_es_impar = ultimo_si_es_impar.replace('##bloque izq##', '', 1)
    longitud = longitud - 1
    #print(ultimo_si_es_impar)

#* creamos el cuerpo sin las noticias
bloque_final = ''
bloque_final_con_noticias = ''
for numero in range(0, (int(longitud/2))):
    bloque_final_con_noticias = bloque_final_con_noticias + bloques.bloque_exterior

#* metemos las noticias menos la última
for numero in range(0, longitud):
    if numero % 2 != 0:    # numero impar
        #print('posición izq')
        bloque_final_con_noticias = bloque_final_con_noticias.replace(
            '##bloque der##', noticias_colocadas[numero], 1)
    else:   # numero par
        #print('posición der')
        bloque_final_con_noticias = bloque_final_con_noticias.replace(
            '##bloque izq##', noticias_colocadas[numero], 1)




#* unimos los dos bloques
bloque_final_con_noticias = bloque_final_con_noticias + ultimo_si_es_impar




#* unimos todas las partes
resultado =''
resultado = resultado + comienzo_en_curso
resultado = resultado + noticia_destacada
resultado = resultado + bloques.trabajos
resultado = resultado + bloque_final_con_noticias
resultado = resultado + bloques.fin


#* codificamos a html
resultado = re.sub("á", "&aacute;", resultado)
resultado = re.sub("é", "&eacute;", resultado)
resultado = re.sub("í", "&iacute;", resultado)
resultado = re.sub("ó", "&oacute;", resultado)
resultado = re.sub("ú", "&uacute;", resultado)
resultado = re.sub("Á", "&Aacute;", resultado)
resultado = re.sub("É", "&Eacute;", resultado)
resultado = re.sub("Í", "&Iacute;", resultado)
resultado = re.sub("Ó", "&Oacute;", resultado)
resultado = re.sub("Ú", "&Uacute;", resultado)
resultado = re.sub("ñ", "&ntilde;", resultado)
resultado = re.sub("Ñ", "&Ntilde;", resultado)
resultado = re.sub("¡", "&iexcl;", resultado)
resultado = re.sub("¿", "&iquest;", resultado)
resultado = re.sub("Â", "", resultado)
resultado = re.sub("â€œ", "&quot;", resultado)
resultado = re.sub("â€", "&quot;", resultado)



#* mostramos el resultado para copiar y pegar
# print("<!--código generado para bloque de foro sin texto-->")
# print()
# print(resultado)
# print()
# print("<!--código generado para bloque de foro sin texto-->")

#* pegamos al portapapeles el resultado
# clipboard.copy(resultado)

print()
print('Archivo generado')
print()


#* creamos el archivo
archivo = str(boletin)+"c.html"
with open(archivo, mode="w", encoding="utf-16") as fichero:
    print(resultado, file=fichero)




# f = open(archivo , 'w')
# f.write(resultado)
# f.close()


