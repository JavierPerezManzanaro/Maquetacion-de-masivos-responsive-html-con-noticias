# !/usr/bin/env python
# -*- coding: utf-8 -*-
# /

#! CUIDADO
# todo por hacer
# ? aviso
# * explicación


#! usar la versión de python MagicPython (Python 3.8.5)


import datetime
from os import close, link
#from numpy import empty
from wordpress_xmlrpc import Client
from wordpress_xmlrpc.methods import posts
import requests
import os
import re
from PIL import Image
from pprint import pprint
import errno
import random
import sqlite3
from playsound import playsound


# * librerias propias
import bloques
import datos_de_acceso
import banners


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

ahora = datetime.date.today()

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


# * *******************
# * Funciones de la app
# * *******************

def strip_tags(value: str) -> str:
    """Limpia del código html <…> y […].

    Args:
        value (str): Cadena a limpiar

    Returns:
        (str): Cadena limpia
    """
    value = re.sub(r'<[^>]*?>', ' ', value)  # elimina <...>
    value = re.sub(r'\[[^>]*?\]', ' ', value)  # elimina [...]
    return value


def tabla_interior(tipo: str, imagen: str, titular: str, texto: str, url: str, nombre: int) -> str:
    """Genera cada tabla de html que contiene un trabajo o la noticia.

    Args:
        tipo (str): el tipo que es: compania, produccion, comun
        imagen (str): url local (bbdd, trabajos) o absoluta (noticias)
        titular (str)
        texto (str)
        url (srt)

    Returns:
        (srt): tabla en html con el trabajo o la noticia
    """
    # todo: meter como tipo destacada
    tabla_interior = bloques.noticia_funcion_raw

    if tipo == 'compania':  # izq, compañia
        tabla_interior = tabla_interior.replace('##color##', '#881288')
        tabla_interior = tabla_interior.replace('##posicion##', 'left')
    elif tipo == 'produccion':  # der. producción
        tabla_interior = tabla_interior.replace('##color##', '#0F7888')
        tabla_interior = tabla_interior.replace('##posicion##', 'right')
    elif tipo == 'comun':  # noticias genericas, comunes
        tabla_interior = tabla_interior.replace('##color##', '#000000')
    else:
        print('❌ ❌ ¡¡¡Elemento no generado porque no coincide el tipo con ninguno de los predefinidos!!!')
        playsound('alerta.mp3')

    # Analiza donde esta la imagen (en remoto o en local)
    if 'https' in imagen:
        imagen_local, ancho, alto = descarga_imagen(imagen, nombre, 320)
        tabla_interior = tabla_interior.replace('##alto##', str(alto))
    else:
        imagen_local = imagen
        tabla_interior = tabla_interior.replace('height="##alto##"', '')

    tabla_interior = tabla_interior.replace('##noticia_titular##', titular)
    tabla_interior = tabla_interior.replace('##imagen##', str(imagen_local))
    tabla_interior = tabla_interior.replace('##ancho##', '320')
    tabla_interior = tabla_interior.replace('##noticia_texto##', texto)
    tabla_interior = tabla_interior.replace('##noticia_enlace##', url)

    return tabla_interior


def descarga_imagen(url: str, nombre: int, ancho_px: int):
    """Descarga las imagenes y las ajusta al tamaño

    Args:
        url (str): es la url: axon[noticia]['imagen']
        nombre (int): número de la noticia/trabajo que sera el nombre del archivo
        ancho_px (int): ancho a usar

    Returns:
        imagen_local (str): ruta de la imagen
        ancho (int): ancho de la imagen 320px
        alto (int): alto de la imágen
    """
    # todo: quitar el ancho porque ya sabemos que es 320 px
    try:
        extension = url[len(url)-4:len(url)]
        if extension == "jpeg":
            extension = ".jpg"
        else:
            pass
        imagen_local = nombre_archivo+'/'+str(nombre)+extension
        # descargamos la imagen
        imagen = requests.get(url).content
        with open(imagen_local, 'wb') as handler:
            handler.write(imagen)
        # tratamos la imagen para Mostrar imagenes imagen.show()
        imagen = Image.open(imagen_local)
    except:
        imagen_local = 'spacer.gif'
        imagen = Image.open(imagen_local)
    finally:
        imagen.convert("RGB")
        alto = int((int(imagen.size[1]) * ancho_px) / int(imagen.size[0]))
        imagen = imagen.resize((ancho_px, alto))
        #ancho = ancho_px
        imagen.save(imagen_local)

    return imagen_local, ancho_px, alto


def eliminar_elemento(tupla: tuple, elemento: str) -> tuple:
    """Elimina el elmento que de pasa de la tupla

    Args:
        tupla (tuple): Tupla de entrada
        elemento (str): Elemento que queremos eliminar

    Returns:
        tuple: tupla SIN el elemento
    """
    nueva = list()
    for c in list(tupla):
        if not c == elemento:
            nueva.append(c)

    return tuple(nueva)


def creacion_banners(publicidad_horizontal):
    """Va generando uno a uno cada uno de los banners horizontales periodicos.
    Elige uno al azar, lo crea y lo elimina.

    Args:
        publicidad_horizontal (list): lista compuesta por los datos de la bbdd sqlite3

    Returns:
        str: código html del banner
    """
    if len(publicidad_horizontal) >= 1:
        banner_seleccionado = random.choice(publicidad_horizontal)
        banner_en_curso = bloques.banner_horizontal_raw
        banner_en_curso = banner_en_curso.replace(
            '##url##', str(banner_seleccionado[3]))
        banner_en_curso = banner_en_curso.replace(
            '##imagen##', str(banner_seleccionado[2]))
        banner_en_curso = banner_en_curso.replace(
            '##alt##', str(banner_seleccionado[5]))
        publicidad_horizontal = publicidad_horizontal.remove(
            banner_seleccionado)
        return banner_en_curso
    elif len(publicidad_horizontal) < 1:
        banner_en_curso = ''
        return banner_en_curso


def trabajos_a_mostrar(tipo: str):
    """Pregunta por los trabajos o noticias de cada una de las dos secciones.

    Args:
        tipo (str): Tipo de trabajo: 'compania' o 'produccion'

    Returns:
        lista: Lista con los trabajo o noticias de cada función.
    """
    if tipo == 'compania':
        posicion_publicidad = 'right'
        trabajos = input('¿Trabajos de animales de compañía para publicar? ')
    elif tipo == 'produccion':
        posicion_publicidad = 'left'
        trabajos = input('¿Trabajos de animales de producción para publicar? ')
    try:
        cerramos_bbdd = 0
        trabajos_lista = []
        trabajos = trabajos.strip()
        trabajos = trabajos.split(' ')
        publicidad = bloques.publicidad.replace('##posicion##', posicion_publicidad)
        cursorObj = con.cursor()
        for trabajo_seleccionado in trabajos:
            trabajo_seleccionado = int(trabajo_seleccionado)
            if trabajo_seleccionado == 0:
                trabajos_lista.append(publicidad)
            if trabajo_seleccionado < (numero_registros - noticias_mostradas) and trabajo_seleccionado != 0:
                # * entra si son trabajos de la bbdd
                cursorObj.execute(
                    'SELECT * FROM hemeroteca WHERE id=' + str(trabajo_seleccionado) + ';')
                trabajo_en_bbdd = cursorObj.fetchone()
                titular = trabajo_en_bbdd[1]
                url = trabajo_en_bbdd[2]
                imagen = trabajo_en_bbdd[3]
                texto = trabajo_en_bbdd[5]
                trabajos_lista.append(
                    tabla_interior(tipo, imagen, titular, texto, url, trabajo_seleccionado))
                cerramos_bbdd = 1
            if trabajo_seleccionado >= (numero_registros - noticias_mostradas):
                # * entra si es una noticia de la web y es tratada como trabajo
                imagen_local, ancho, alto = descarga_imagen(
                    axon[trabajo_seleccionado]['imagen'], trabajo_seleccionado, 320)
                trabajos_lista.append(tabla_interior(
                    tipo,
                    imagen_local,
                    axon[trabajo_seleccionado]['titulo'],
                    axon[trabajo_seleccionado]['contenido'],
                    axon[trabajo_seleccionado]['url'],
                    trabajo_seleccionado))
                print('🟡 Noticia como trabajo: Recuerda editarla y meterla en la bbdd')
        if cerramos_bbdd == 1:
            cursorObj.close()
    except Exception as e:
        print('Exception occurred while code execution: ' + repr(e))
        print('❌ Esta sección no se va a publicar')
        playsound('alerta.mp3')

    if tipo == 'compania':
        trabajos_compania = trabajos_lista
        return trabajos_compania
    elif tipo == 'produccion':
        trabajos_produccion = trabajos_lista
        return trabajos_produccion


# * ****************
# * empezamos la app
# * ****************

os.system('clear')

boletin = int(input("¿Qué número del masivo vas a publicar? "))
print()
print("0 = Dejar hueco relleno")
print("Nº | Título")
print()


# * creamos la carpeta
nombre_archivo = str(boletin)+'c'
try:
    os.mkdir(nombre_archivo)
except OSError as e:
    print("Borrando carpeta anterior.")
    if e.errno != errno.EEXIST:
        raise


# * gestión de la publicidad
if ahora.today().isoweekday() == 1:
    dia = 'l'
elif ahora.today().isoweekday() == 2:
    dia = 'm'
elif ahora.today().isoweekday() == 3:
    dia = 'x'
elif ahora.today().isoweekday() == 4:
    dia = 'j'
elif ahora.today().isoweekday() == 5:
    dia = 'v'
elif ahora.today().isoweekday() == 6:  # solo esta por si programo un sábado
    dia = 'v'
elif ahora.today().isoweekday() == 7:  # solo esta por si programo un domingo
    dia = 'j'

con = sqlite3.connect('bbdd.sqlite3')
cursorObj = con.cursor()
cursorObj.execute(
    'SELECT * FROM publicidad WHERE ' + dia + ' = "1" and exclusiva = "horizontal";')
publicidad_horizontal = cursorObj.fetchall()
cursorObj.close()

# * Publicidad de Norel: distintos cada semana
semana = datetime.date.today().isocalendar()[1]
for banner in publicidad_horizontal:
    if banner[1] == 'Norel semana impar' and semana % 2 == 0:
        publicidad_horizontal.remove(banner)
    else:
        if banner[1] == 'Norel semana par':
            publicidad_horizontal.remove(banner)


# * Publicidad de purina: por meses
# todo hacer este bloque mas elegante
banner_Purina = ''
paso_purina = 0
# si le toca lo metemos en una variable nueva
for banner in publicidad_horizontal:
    if semana in range(1, 21) and banner[1] == 'Purina hasta final mayo':
        paso_purina = 1
        banner_Purina = banner
    if semana in range(22, 35) and banner[1] == 'Purina junio hasta final agosto':
        paso_purina = 1
        banner_Purina = banner
    if semana in range(36, 51) and banner[1] == 'Purina a partir septiembre':
        paso_purina = 1
        banner_Purina = banner
for banner in publicidad_horizontal:
    if banner[1] == 'Purina hasta final mayo':
        paso_purina = 1
        purina_borrar_1 = banner
    if banner[1] == 'Purina junio hasta final agosto':
        paso_purina = 1
        purina_borrar_2 = banner
    if banner[1] == 'Purina a partir septiembre':
        paso_purina = 1
        purina_borrar_3 = banner
if paso_purina == 1:
    publicidad_horizontal.remove(purina_borrar_1)
    publicidad_horizontal.remove(purina_borrar_2)
    publicidad_horizontal.remove(purina_borrar_3)
    # añadimos el banner
    publicidad_horizontal.append(banner_Purina)


# * Accedemos a la bbdd y mostramos los trabajos
con = sqlite3.connect('bbdd.sqlite3')
# trabajos de compañia
cursorObj = con.cursor()
cursorObj.execute(
    'SELECT * FROM hemeroteca WHERE tipo = "p" ORDER BY "titular";')
trabajos_en_bbdd_compania = cursorObj.fetchall()
# trabajos de producción
cursorObj = con.cursor()
cursorObj.execute(
    'SELECT * FROM hemeroteca WHERE tipo = "g" ORDER BY "titular";')
trabajos_en_bbdd_produccion = cursorObj.fetchall()
cursorObj.close()

print('Trabajos de compañía:')
print(f"----|-{'-'*104}")
for trabajo in trabajos_en_bbdd_compania:
    print(f"{trabajo[0]:>3} | {trabajo[1][0:100]}")

print()
print('Trabajos de producción:')
print(f"----|-{'-'*104}")
for trabajo in trabajos_en_bbdd_produccion:
    print(f"{trabajo[0]:>3} | {trabajo[1][0:100]}")

# * Recogemos las noticias de la web
cliente = Client(datos_de_acceso.sitio, datos_de_acceso.usuario,
                 datos_de_acceso.contrasena)
axon_entradas = cliente.call(posts.GetPosts(
    {'number': noticias_mostradas, 'offset': 0,  'post_status': 'publish'}))  # todo 'orderby': 'title',
print()
print(f"Últimas {noticias_mostradas} noticias:")
print(f"----|-{'-'*104}")
# creamos el diccionario axon[noticia] con la entrada 0, el hueco y mostramos la tabla
numero_registros = len(trabajos_en_bbdd_compania) + \
    len(trabajos_en_bbdd_produccion) + 1
url = 'nulo'
axon = {}
axon[0] = {'id': 0, 'url': datos_de_acceso.url_general, 'imagen': datos_de_acceso.imagen_en_blanco,
           'titulo': 'vacio', 'contenido': '&nbsp;'}
if len(axon_entradas) > 0:
    for entrada in axon_entradas:
        print(f"{numero_registros:>3} | {entrada.title[0:104]}")
        # sacamos la url de la imagen
        imagen = re.findall('img .*?src="(.*?)"', entrada.content)
        # trabajamos la entrada sin imagen
        try:
            imagen = imagen[0]
        except IndexError:
            imagen = datos_de_acceso.imagen_en_blanco
        # tratamos y limpiamos el contenido de la entrada
        contenido_bruto = strip_tags(entrada.content)
        contenido_bruto = re.sub('&nbsp;', ' ', contenido_bruto)
        contenido_bruto = re.sub('  ', ' ', contenido_bruto)
        contenido_bruto = contenido_bruto.strip(' ')
        contenido_bruto = contenido_bruto.replace(entrada.title, '', 1)
        contenido_bruto = contenido_bruto[0:longitud_de_noticia] + '... '
        # generalmos el diccionario
        axon[numero_registros] = {'id': entrada.id, 'url': entrada.link,
                                  'imagen': imagen, 'titulo': entrada.title, 'contenido': contenido_bruto}
        numero_registros += 1

else:
    print("No hay entradas para mostrar")

print()
print()
print('Los trabajos/noticias separadas con espacios.')
print()


# * Gestión de noticia destacada
try:
    noticia = int(input("¿Qué noticia es la destacada? "))
    noticia_destacada = bloques.noticia_destacada
    imagen_local, ancho, alto = descarga_imagen(
        axon[noticia]['imagen'], noticia, 320)
    noticia_destacada = noticia_destacada.replace(
        '##imagen##', str(imagen_local))
    noticia_destacada = noticia_destacada.replace('##ancho##', str(ancho))
    noticia_destacada = noticia_destacada.replace('##alto##', str(alto))
    noticia_destacada = noticia_destacada.replace(
        '##noticia_titular##', axon[noticia]['titulo'])    # entrada.title)
    noticia_destacada = noticia_destacada.replace(
        '##contenido##', axon[noticia]['contenido'])
    noticia_destacada = noticia_destacada.replace(
        '##noticia_enlace##', axon[noticia]['url'])    # entrada.link)
    noticia_destacada = noticia_destacada + \
        creacion_banners(publicidad_horizontal)
except:
    noticia_destacada = ''
    print('❌ Esta sección no se va a publicar')
    playsound('alerta.mp3')

print()


# * Trabajos de animales de compañia, se crea la lista trabajos_compania
trabajos_compania = trabajos_a_mostrar('compania')


# * Trabajos de animales de producción, se crea la lista trabajos_produccion
trabajos_produccion = trabajos_a_mostrar('produccion')


# * Fusión de trabajos_compania y de trabajos_produccion
longitud_campania = len(trabajos_compania)
longitud_produccion = len(trabajos_produccion)
mas_largo = longitud_campania if longitud_campania > longitud_produccion else longitud_produccion
mas_corto = longitud_campania if longitud_campania < longitud_produccion else longitud_produccion
html_trabajos = ''
# creamos las que van enfrentadas
for enfrentadas in range(mas_corto):
    html_trabajos = html_trabajos + bloques.bloque_exterior_funcion
    html_trabajos = html_trabajos.replace(
        '##bloque izq##', trabajos_compania[enfrentadas], 1)
    html_trabajos = html_trabajos.replace(
        '##bloque der##', trabajos_produccion[enfrentadas], 1)
    html_trabajos = html_trabajos + creacion_banners(publicidad_horizontal)
# creamos las que NO van enfrentadas
for sueltas in range(mas_largo-mas_corto):
    html_trabajos = html_trabajos + bloques.bloque_exterior_funcion
    sueltas = sueltas + mas_corto + 1
    html_trabajos = html_trabajos + creacion_banners(publicidad_horizontal)
    if longitud_campania > sueltas:
        html_trabajos = html_trabajos.replace(
            '##bloque izq##', trabajos_compania[sueltas], 1)
    else:
        # todo aqui va la pb vertical
        html_trabajos = html_trabajos.replace(
            '##bloque izq##', publicidad, 1)
    if longitud_produccion > sueltas:
        html_trabajos = html_trabajos.replace(
            '##bloque der##', trabajos_produccion[sueltas], 1)
    else:
        # todo aqui va la pb vertical
        html_trabajos = html_trabajos.replace(
            '##bloque der##', publicidad, 1)


# * Gestión de las noticias
print()
noticias = input("¿Qué noticias quieres publicar? ")
noticias = noticias.strip()
try:
    noticias = noticias.split(' ')
    pase = 1
    for noticia in noticias:
        noticia = int(noticia)
        if noticia == 0:
            if pase % 2 != 0:
                publicidad = bloques.publicidad.replace('##posicion##', 'left')
                noticias_colocadas.append(publicidad)
            else:
                publicidad = bloques.publicidad.replace(
                    '##posicion##', 'right')
                noticias_colocadas.append(publicidad)
        else:
            noticias_colocadas.append(tabla_interior(
                'comun', axon[noticia]['imagen'], axon[noticia]['titulo'], axon[noticia]['contenido'], axon[noticia]['url'], noticia))  # es una lista
        pase += 1
    longitud = len(noticias_colocadas)
    print(f"Noticias generadas: {longitud}")
except:
    noticias_colocadas = ''
    print('❌ Esta sección no se va a publicar')
    playsound('alerta.mp3')


# * Generamos el bloque general de las noticias
numero = 0


# * Creamos el último si es impar
ultimo_si_es_impar = ''
if longitud % 2 != 0:
    ultimo_si_es_impar = bloques.bloque_exterior
    ultimo_si_es_impar = ultimo_si_es_impar.replace(
        '##bloque izq##', noticias_colocadas[-1], 1)  # usamos el último
    ultimo_si_es_impar = ultimo_si_es_impar.replace('##bloque izq##', '', 1)
    ultimo_si_es_impar = ultimo_si_es_impar.replace('##posicion##', 'left')
    longitud -= 1


# * Creamos el cuerpo sin las noticias
bloque_final = ''
bloque_final_con_noticias = ''
for numero in range(0, (int(longitud/2))):
    bloque_final_con_noticias = bloque_final_con_noticias + bloques.bloque_exterior
    bloque_final_con_noticias = bloque_final_con_noticias + creacion_banners(publicidad_horizontal)


# * Metemos las noticias menos la última
for numero in range(0, longitud):
    if numero % 2 == 0:    # numero par DERECHA left
        bloque_final_con_noticias = bloque_final_con_noticias.replace(
            '##bloque der##', noticias_colocadas[numero], 1)
        bloque_final_con_noticias = bloque_final_con_noticias.replace(
            '##posicion##', 'left')
    else:   # numero impar: IZQUIERDA right
        bloque_final_con_noticias = bloque_final_con_noticias.replace(
            '##bloque izq##', noticias_colocadas[numero], 1)
        bloque_final_con_noticias = bloque_final_con_noticias.replace(
            '##posicion##', 'right')


# * Unimos los dos bloques (la noticias por pares y la última)
bloque_final_con_noticias = bloque_final_con_noticias + ultimo_si_es_impar


# * Gestionamos la cabecera
comienzo_en_curso = bloques.comienzo
comienzo_en_curso = comienzo_en_curso.replace(
    '##nombre_archivo##', nombre_archivo)
comienzo_en_curso = comienzo_en_curso.replace('##numero##', str(boletin))
comienzo_en_curso = comienzo_en_curso.replace(
    '##mes##', meses[str(ahora.month)])
# todo: añadir año


# * Vamos uniendo las partes
resultado = ''
resultado = resultado + comienzo_en_curso
resultado = resultado + noticia_destacada


# * Banners Horizontales de forma aislada. El formato de la fecha es aaaa-mm-dd
# banner de ifema, ya paso
# ifema_dias = ['2022-02-05', '2022-02-07', '2022-02-14',
#               '2022-02-21', '2022-02-04']
# if str(ahora) in ifema_dias:
#     print()
#     print('🟡 Hoy entra el banner de iberzoo, PONER EL PRIMERO')
#     playsound('alerta.mp3')
#     resultado = resultado + banners.iberzoo
# banner de geporc
geporc_dias = ['2022-05-13', '2022-06-01', '2022-06-15',
               '2022-06-30', '2022-07-15', '2022-09-01',
               '2022-09-15', '2022-09-30', '2022-10-14',
               '2022-10-31', '2022-11-15', '2022-11-30',
               '2022-12-15', '2022-12-30']
if str(ahora) in geporc_dias:
    print()
    print('🟡 Hoy entra el banner de geporc/centauto, PONER EL PRIMERO')
    playsound('alerta.mp3')
    resultado = resultado + banners.centauto
# banner de vetnova: solo los jueves
if dia == 'j':
    resultado = resultado + banners.vetnova


# * Vamos uniendo las partes
resultado = resultado + html_trabajos


# * Banners verticales, desactivados
# resultado = resultado + banners.laser_vertical
# banner de argentina desactivado
# argentina_banner_elegido = [banners.argentina_1,banners.argentina_2, banners.argentina_3, banners.argentina_4]
# argentina_banner_elegido = random.choice(argentina_banner_elegido)
# argentina_banner = banners.argentina_base.replace('**modulo_pb**', argentina_banner_elegido)
# resultado = resultado + argentina_banner


# * Chequea si todos los banner estan publicados. Si no lo estan se publican y avisa
if len(publicidad_horizontal) >= 1:
    print()
    print('❌ Cuidado: los banners horizontales no se han colocado bien')
    print()
    playsound('alerta.mp3')
    for n in range(len(publicidad_horizontal)):
        resultado = resultado + creacion_banners(publicidad_horizontal)


# * Vamos uniendo las partes
resultado = resultado + bloque_final_con_noticias
resultado = resultado + banners.setna  # pb de setna
resultado = resultado + bloques.fin


# * Codificamos a html
# ? para cuerpos de email charset=ISO-8859-1
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


# * Mostramos el resultado para copiar y pegar
# print("<!--COMIENZO código generado-->")
# print()
# print(resultado)
# print()
# print("<!--FIN código generado-->")


# * Pegamos al portapapeles el resultado
# import pyperclip as clipboard
# clipboard.copy(resultado)


# * Creamos el archivo
archivo = str(boletin)+"c.html"
with open(archivo, mode="w", encoding="utf-8") as fichero:
    print(resultado, file=fichero)


print()
print('Archivo generado: 👍')
print()
