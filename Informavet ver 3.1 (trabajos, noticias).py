# !/usr/bin/env python
# -*- coding: utf-8 -*-
# /

# Versión 3.1

#! CUIDADO
#todo por hacer
#? aviso
#* explicación


from datetime import datetime
from os import close, link
from wordpress_xmlrpc import Client
from wordpress_xmlrpc.methods import posts
import requests
import os
import re
from PIL import Image
from pprint import pprint
import pyperclip as clipboard
import errno
import random
import sqlite3

#* liberias propias
#import pb
import Bloques
import Datos_de_acceso
#todo: sacar los datos personales a unas preferencias que no suben a la red

longitud_de_noticia = 400
noticias_mostradas = 20
imagen_local = ''
ancho = 0
alto = 0

noticias_colocadas = []
trabajos_compania = []
trabajos_produccion = []

posicion = 1
longitud = 0


def strip_tags(value):
    """Limpia del código html <…> y […]

    Args:
        value ([str]): [description]

    Returns:
        [str]: [description]
    """
    value = re.sub(r'<[^>]*?>', ' ', value)  # elimina <...>
    value = re.sub(r'\[[^>]*?\]', ' ', value)  # elimina [...]
    return value


def tabla_interior(tipo, imagen, titular, texto, url):
    """Genera cada tabla de html que contiene un trabajo o la noticia.

    Args:
        tipo (str): el tipo que es: peq, gra, comun
        imagen (str): url local (bbdd, trabajos) o absoluta (noticias)
        titular (str)
        texto (str)
        url (srt)

    Returns:
        [type]: tabla en html con el trabajo o la noticia
    """
    #todo: meter como tipo destacada

    tabla_interior = Bloques.noticia_funcion_raw
    tabla_interior = tabla_interior.replace(
        '##noticia_titular##', titular)

    if tipo == 'peq':  # izq, pequeños
        tabla_interior = tabla_interior.replace(
            '##color##', '#881288')
        tabla_interior = tabla_interior.replace(
            '##posicion##', 'left')
        tabla_interior = tabla_interior.replace(
            '##imagen##', str(imagen))
    elif tipo == 'gra':  # der. producción
        tabla_interior = tabla_interior.replace(
            '##color##', '#0F7888')
        tabla_interior = tabla_interior.replace(
            '##posicion##', 'right')
        tabla_interior = tabla_interior.replace(
            '##imagen##', str(imagen))
    elif tipo == 'comun':  # noticias genericas, comunes
        tabla_interior = tabla_interior.replace(
            '##color##', '#000000')
        imagen_local, ancho, alto = descarga_imagen(imagen, 320)
        tabla_interior = tabla_interior.replace(
            '##alto##', str(alto))
        tabla_interior = tabla_interior.replace(
            '##imagen##', str(imagen_local))
    else:
        print('Elemento no generado porque no coincide el tipo con ninguno de los predefinidos!!!')

    tabla_interior = tabla_interior.replace(
        '##ancho##', '320')
    tabla_interior = tabla_interior.replace(
        'height="##alto##"', '')
    tabla_interior = tabla_interior.replace(
        '##noticia_texto##', texto)
    tabla_interior = tabla_interior.replace(
        '##noticia_enlace##', url)

    return tabla_interior


def descarga_imagen(imagen_red, ancho_px):
    """Descarga las imagenes y las ajusta al tamaño

    Args:
        imagen_red (str): es la url: axon[noticia]['imagen']
        ancho_px (int): ancho a usar

    Returns:
        [type]: el nombre de la imagen, alto y ancho
    """
    #todo: quitar el ancho porque ya sabemos que es 320 px
    #* extensión del archivo
    try:
        extension = imagen_red[len(imagen_red)-4:len(imagen_red)]
        if extension == "jpeg":
            extension = ".jpg"
        else:
            pass
        imagen_local = nombre_archivo+'/'+str(noticia)+extension
        # descargamos la imagen
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



#* empezamos con la app
os.system('clear')

boletin = int(input("¿Qué número de InformaVet es? "))
print()
print("0 = Dejar hueco relleno")
print("Nº | Título")
print()


#* creamos la carpeta
nombre_archivo = str(boletin)+'c'
try:
    os.mkdir(nombre_archivo)  # (nombre_archivo+'c')
except OSError as e:
    print("Borrando carpeta anterior.")
    if e.errno != errno.EEXIST:
        raise
    #todo: borrar tambien la carpeta


#* accedemos y mostramos los trabajos
con = sqlite3.connect('bbdd.sqlite3')
# gestionamos la lista de trabajos completa
cursorObj = con.cursor()
cursorObj.execute('SELECT * FROM hemeroteca ORDER BY "tipo", "titular";')
trabajos_en_bbdd = cursorObj.fetchall()
# trabajos de pequeño
cursorObj = con.cursor()
cursorObj.execute(
    'SELECT * FROM hemeroteca WHERE tipo = "p" ORDER BY "titular";')
trabajos_en_bbdd_peq = cursorObj.fetchall()
# trabajos de grandes
cursorObj = con.cursor()
cursorObj.execute(
    'SELECT * FROM hemeroteca WHERE tipo = "g" ORDER BY "titular";')
trabajos_en_bbdd_gra = cursorObj.fetchall()
# cerramos connexión con la bbdd
cursorObj.close()

print('Tabajos de pequeños:')
print(f"---|-{'-'*104}")
for trabajo in trabajos_en_bbdd_peq:
    print(f"{trabajo[0]:>2} | {trabajo[1][0:100]}")

print()
print('Tabajos de grandes:')
print(f"---|-{'-'*104}")
for trabajo in trabajos_en_bbdd_gra:
    print(f"{trabajo[0]:>2} | {trabajo[1][0:100]}")

numero = len(trabajos_en_bbdd)

#! código original
# print("Tabajos:")
# print("Nº | Título")
# print(f"---|-{'-'*104}")
# for trabajo in trabajos_en_bbdd:
#     print(f"{trabajo[0]:>2} | {trabajo[4]} - {trabajo[1][0:100]}")
#! código original fin

#* recogemos las noticias de la web de axon
sitio = "https://axoncomunicacion.net/xmlrpc.php"
cliente = Client(sitio, Datos_de_acceso.usuario, Datos_de_acceso.contrasena)
axon_entradas = cliente.call(posts.GetPosts(
    {'number': noticias_mostradas, 'offset': 0,  'post_status': 'publish'}))  #todo 'orderby': 'title',
print()
print(f"Últimas {noticias_mostradas} noticias de Axón comunicación:")
print(f"---|-{'-'*104}")
#? creados diccionario axon[noticia] con la entrada 0, el hueco y mostramos la tabla
url = 'nulo'
axon = {}
axon[0] = {'id': 0, 'url': 'https://axoncomunicacion.net', 'imagen': 'https://axoncomunicacion.net/masivos/spacer.gif',
           'titulo': 'vacio', 'contenido': '&nbsp;'}
if len(axon_entradas) > 0:
    for entrada in axon_entradas:
        print(f"{numero:>2} | {entrada.title[0:104]}")
        # sacamos la url de la imagen
        imagen = re.findall('img .*?src="(.*?)"', entrada.content)
        imagen = imagen[0]
        # tratamos y limpiamos el contenido de la entrada
        contenido_bruto = strip_tags(entrada.content)
        contenido_bruto = re.sub('&nbsp;', ' ', contenido_bruto)
        contenido_bruto = re.sub('  ', ' ', contenido_bruto)
        contenido_bruto = contenido_bruto.strip(' ')
        #todo contenido_bruto = contenido_bruto.rstrip('\n')
        contenido_bruto = contenido_bruto.replace(entrada.title, '', 1)
        contenido_bruto = contenido_bruto[0:longitud_de_noticia] + '... '
        # print(contenido_bruto)
        # print('--------')
        # asignamos el array
        axon[numero] = {'id': entrada.id, 'url': entrada.link,
                        'imagen': imagen, 'titulo': entrada.title, 'contenido': contenido_bruto}
        numero += 1
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
comienzo_en_curso = Bloques.comienzo
comienzo_en_curso = comienzo_en_curso.replace(
    '##nombre_archivo##', nombre_archivo)
comienzo_en_curso = comienzo_en_curso.replace('##numero##', str(boletin))
comienzo_en_curso = comienzo_en_curso.replace(
    '##mes##', meses[str(ahora.month)])
#todo: añadir año


#* gestión de noticia destacada
noticia = int(input("¿Qué noticia es la destacada? "))
if noticia != 0:
    noticia_destacada = Bloques.noticia_destacada
    imagen_local, ancho, alto = descarga_imagen(axon[noticia]['imagen'], 320)
    noticia_destacada = noticia_destacada.replace(
        '##imagen##', str(imagen_local))
    noticia_destacada = noticia_destacada.replace('##ancho##', str(ancho))
    noticia_destacada = noticia_destacada.replace('##alto##', str(alto))
    noticia_destacada = noticia_destacada.replace(
        '##contenido##', axon[noticia]['contenido'])
    noticia_destacada = noticia_destacada.replace(
        '##noticia_enlace##', axon[noticia]['url'])    # entrada.link)
    noticia_destacada = noticia_destacada.replace(
        '##noticia_titular##', axon[noticia]['titulo'])    # entrada.title)
else:
    noticia_destacada = ''


print('')
print('Los trabajos/noticias separadas con espacios.')
print('')

#todo: y si pongo 0 me deja el hueco, hacer la prueba
#* trabajos de animales de compañia
trabajos = input('¿Qué trabajos de animales de compañía? ')
trabajos = trabajos.split(' ')
cursorObj = con.cursor()
for trabajo_seleccionado in trabajos:
    if trabajo_seleccionado == '0':
        trabajos_compania.append('##publicidad##')
    else:
        cursorObj.execute('SELECT * FROM hemeroteca WHERE id=' + trabajo_seleccionado + ';')
        trabajo_en_bbdd = cursorObj.fetchone()
        #pprint(trabajo_en_bbdd)
        titular = trabajo_en_bbdd[1]
        url = trabajo_en_bbdd[2]
        imagen = trabajo_en_bbdd[3]
        texto = trabajo_en_bbdd[5]
        #*creamos la lista trabajos_compania que contiene todos los trabajos de peq
        trabajos_compania.append(
            tabla_interior('peq', imagen, titular, texto, url))
cursorObj.close()

html_trabajos_peq = ''
html_trabajos_peq = Bloques.bloque_exterior_funcion * len(trabajos_compania)

for trabajo in trabajos_compania:
    html_trabajos_peq = html_trabajos_peq.replace(
        '##bloque izq##', trabajo, 1)
    html_trabajos_peq = html_trabajos_peq.replace(
        '##bloque der##', '##publicidad##')



#* trabajos de animales de producción
trabajos = input(
    '¿Qué trabajos de animales de producción? ')
trabajos = trabajos.split(' ')
cursorObj = con.cursor()
for trabajo_seleccionado in trabajos:
    if trabajo_seleccionado == '0':
        trabajos_compania.append('##publicidad##')
    else:
        #trabajo_seleccionado = int(trabajo_seleccionado)
        cursorObj.execute('SELECT * FROM hemeroteca WHERE id=' +
                        trabajo_seleccionado + ';')
        trabajo_en_bbdd = cursorObj.fetchone()
        #pprint(trabajo_en_bbdd)
        titular = trabajo_en_bbdd[1]
        url = trabajo_en_bbdd[2]
        imagen = trabajo_en_bbdd[3]
        texto = trabajo_en_bbdd[5]
        #*creamos la lista trabajos_produccion que contiene todos los trabajos de gra
        trabajos_produccion.append(
            tabla_interior('gra', imagen, titular, texto, url))
cursorObj.close()

html_trabajos_gra = ''
html_trabajos_gra = Bloques.bloque_exterior_funcion * len(trabajos_produccion)

for trabajo in trabajos_produccion:
    html_trabajos_gra = html_trabajos_gra.replace(
        '##bloque izq##', '##publicidad##')
    html_trabajos_gra = html_trabajos_gra.replace(
        '##bloque der##', trabajo, 1)


#* gestión de las noticias
print('')
noticias = input("¿Qué noticias quieres publicar? ")

noticias = noticias.split(' ')
for noticia in noticias:
    noticia = int(noticia)
    if noticia == 0:
        noticias_colocadas.append('##publicidad##')
    else:
        noticias_colocadas.append(tabla_interior(
        'comun', axon[noticia]['imagen'], axon[noticia]['titulo'], axon[noticia]['contenido'], axon[noticia]['url']))  # es una lista

longitud = len(noticias_colocadas)
print(f"Noticias generadas: {longitud}")
#pprint(noticias_colocadas)

#* generamos el bloque general de las noticias
numero = 0


#* creamos el último si es impar
ultimo_si_es_impar = ''
if longitud % 2 != 0:
    ultimo_si_es_impar = Bloques.bloque_exterior
    ultimo_si_es_impar = ultimo_si_es_impar.replace(
        '##bloque izq##', noticias_colocadas[-1], 1)  # usamos el último
    ultimo_si_es_impar = ultimo_si_es_impar.replace('##bloque izq##', '', 1)
    ultimo_si_es_impar = ultimo_si_es_impar.replace('##posicion##', 'left')
    longitud = longitud - 1


#* creamos el cuerpo sin las noticias
bloque_final = ''
bloque_final_con_noticias = ''
for numero in range(0, (int(longitud/2))):
    bloque_final_con_noticias = bloque_final_con_noticias + Bloques.bloque_exterior
#!!bloque_final_con_noticias = Bloques.bloque_exterior * len(int(longitud/2))


#* metemos las noticias menos la última
for numero in range(0, longitud):
    if numero % 2 == 0:    # numero par- DERECHA left
        bloque_final_con_noticias = bloque_final_con_noticias.replace(
            '##bloque der##', noticias_colocadas[numero], 1)
        bloque_final_con_noticias = bloque_final_con_noticias.replace(
            '##posicion##', 'left')
    else:   # numero impar: IZQUIERDA right
        bloque_final_con_noticias = bloque_final_con_noticias.replace(
            '##bloque izq##', noticias_colocadas[numero], 1)
        bloque_final_con_noticias = bloque_final_con_noticias.replace(
            '##posicion##', 'right')


#* unimos los dos bloques (la noticias por pares y la última)
bloque_final_con_noticias = bloque_final_con_noticias + ultimo_si_es_impar



'''
A la hora de colocar nos tiene que llegar tres listas:
-trab de peq
-trab de grandes
-noticias_colocadas

En un futuro también llegara la de la pb

'''


# #* gestión de los trabajos
# longitud = len(trabajos_compania)+len(trabajos_produccion)
# print(f"Trabajos generados: {longitud}")
# # longitud pasa a ser la mas larga
# if len(trabajos_compania) >= len(trabajos_produccion):
#     print('Compañia es mayor o igual que Producción')
#     longitud = len(trabajos_compania)
# else:
#     print('Compañia es menos que Producción')
#     longitud = len(trabajos_produccion)

# #* embebemos los trabajos y las pb
# # nombramos la pb con un True
# caso_1 = [False, False]
# caso_2 = [True, False]
# caso_3 = [False, True]
# casos = [caso_1, caso_2, caso_3]
# bloque_en_curso = Bloques.bloque_exterior_funcion
# bloque_final_con_trabajos = ''
# for i in range(longitud):
#     caso = random.choice(casos)
#     print(f'casos antes = {casos}')
#     print(f'caso seleccionado = {caso}')
#     if caso[0] == False and caso[1] == False:
#         # caso 1 sin pb
#         print('caso 1')
#         bloque_en_curso = bloque_en_curso.replace(
#             '##bloque##', trabajos_compania[i], 1)
#         bloque_en_curso = bloque_en_curso.replace(
#             '##bloque##', trabajos_produccion[i], 1)
#     elif caso[0] == True and caso[1] == False:
#         # caso 2: pb y grandes
#         print('caso 2')
#         bloque_en_curso = bloque_en_curso.replace(
#             '##bloque##', Bloques.pb_320, 1)
#         bloque_en_curso = bloque_en_curso.replace(
#             '##bloque##', trabajos_produccion[i], 1)
#     elif caso[0] == False and caso[1] == True:
#         # caso 3: peq y pb
#         print('caso 3')
#         bloque_en_curso = bloque_en_curso.replace(
#             '##bloque##', trabajos_compania[i], 1)
#         bloque_en_curso = bloque_en_curso.replace(
#             '##bloque##', Bloques.pb_320, 1)

#     # eliminamos de la lista de caso el caso que ha salido
#     casos = casos.remove(caso)
#     print(f'casos despues = {casos}')
#     # añadimos el bloque que acabamos de crear a la lista
#     bloque_final_con_trabajos = bloque_en_curso + bloque_final_con_trabajos



#* unimos todas las partes
resultado = ''
resultado = resultado + comienzo_en_curso
resultado = resultado + noticia_destacada

resultado = resultado + html_trabajos_peq
resultado = resultado + html_trabajos_gra

resultado = resultado + bloque_final_con_noticias
resultado = resultado + Bloques.fin


#* codificamos a html
#? para cuerpos de email charset=ISO-8859-1
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

#todo: añadir comillas simples y comillas dobles


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
with open(archivo, mode="w", encoding="utf-8") as fichero:
    print(resultado, file=fichero)
