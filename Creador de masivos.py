# source 'venv_informavet/bin/activate'
# https://github.com/JavierPerezManzanaro/Maquetacion-de-masivos-responsive-html-con-noticias

# ! CUIDADO
# todo Por hacer
# ? Aviso
# * Explicación



import errno
import locale
import logging
import os
import random
import re
import sqlite3
import json
import subprocess
import webbrowser
from datetime import datetime
from datetime import timedelta
import sys
import time
from pprint import pprint
import cv2 as cv2  # https://pypi.org/project/opencv-python/
import imutils  # https://pypi.org/project/imutils/
import requests
import html
import tkinter as tk
from tkinter import filedialog
from docx import Document
from colorama import Fore, Style, init # https://pypi.org/project/colorama/
from premailer import transform, Premailer # https://github.com/peterbe/premailer


# * librerías propias
import bloques
import datos_de_acceso
import banners

# * Importar modulos que gestionan los banner si es necesario
from banners_gestion import pb_ecuphar


def execution_time(func):
    """Función decorativa para medir tiempo de ejecución

    Args:
        func (función): Función a medir
    """
    def wrapper(*args, **kwargs):
        initial_time = datetime.now()
        func(*args, **kwargs)
        final_time = datetime.now()
        time_elapsed = final_time - initial_time
        print(f'La función tardo: {time_elapsed.total_seconds()} segundos')
    return wrapper


def strip_tags(value: str) -> str:
    """Elimina el código html <…> y […]

    Args:
        value (str): Cadena a limpiar

    Returns:
        (str): Cadena limpia
    """
    value = re.sub(r'<[^>]*?>', ' ', value)  # elimina <...>
    value = re.sub(r'\[[^>]*?\]', ' ', value)  # elimina [...]
    return value


# decorador @execution_time
def tabla_interior(tipo: str, imagen: str, titular: str, texto: str, url: str, nombre_imagen: int) -> str:
    """Genera la tabla html que contiene un trabajo o la noticia

    Args:
        tipo (str): el tipo que es: compania, común
        imagen (str): url local (bbdd, trabajos) o absoluta (noticias)
        titular (str)
        texto (str)
        url (srt)
        nombre_imagen (srt)

    Returns:
        (str): tabla en html con el trabajo o la noticia
    """
    tabla_interior = bloques.noticia_funcion_raw
    if tipo == 'compania':  # izq, compañía
        tabla_interior = tabla_interior.replace('##color##', '#881288')
        # * La posición se define en la función fusion_trabajos_y_banners
    elif tipo == 'comun':  # noticias genéricas, comunes
        tabla_interior = tabla_interior.replace('##color##', '#000000')
    else:
        logging.warning(
            '❌ Elemento no generado porque no coincide el tipo con ninguno de los predefinidos')
        os.system(ALERTA)
    # Analiza donde esta la imagen (en remoto o en local)
    if 'https' in imagen:
        imagen_local = descarga_imagen(imagen, nombre_imagen)
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


def descarga_imagen(url: str, nombre: int) -> str:
    """Descarga las imágenes y las ajusta al tamaño

    Args:
        url (str): es la url: axon[noticia]['imagen']
        nombre (int): número de la noticia/trabajo que sera el nombre del archivo
    Returns:
        imagen_local (str): ruta de la imagen
    """
    try:
        imagen_temp = nombre_archivo + '/' + str(nombre) + '_temp'
        imagen = requests.get(url).content
        with open(imagen_temp, 'wb') as handler:
            handler.write(imagen)
        imagen = cv2.imread(imagen_temp)
        imagen = imutils.resize(imagen, width=320)
        imagen_local = nombre_archivo + '/' + str(nombre) + '.jpg'
        cv2.imwrite(imagen_local, imagen)
        os.remove(imagen_temp)
    except:
        imagen_local = '/axon_news/imagenes/spacer.gif'
    return imagen_local


def creacion_banners(publicidad_horizontal: list) -> str:  # type: ignore
    """Va generando los banners horizontales. Elige uno al azar, lo crea y lo elimina de la lista hasta terminar con todos los banners

    Args:
        publicidad_horizontal (list): lista compuesta por los datos de la bbdd sqlite3

    Returns:
        str: código html del banner
    """
    if len(publicidad_horizontal) > 1:
        banner_seleccionado = publicidad_horizontal[0]
        logging.info(
            f'Banner {len(publicidad_horizontal)}, {banner_seleccionado[1]} -> colocado')
        banner_en_curso = bloques.banner_horizontal_raw
        banner_en_curso = banner_en_curso.replace(
            '##url##', str(banner_seleccionado[4]))
        banner_en_curso = banner_en_curso.replace(
            '##imagen##', str(banner_seleccionado[3]))
        banner_en_curso = banner_en_curso.replace(
            '##alt##', str(banner_seleccionado[6]))
        publicidad_horizontal = publicidad_horizontal.remove(
            banner_seleccionado)  # type: ignore
        return banner_en_curso
    elif len(publicidad_horizontal) == 1:
        logging.info(
            f'Banner {len(publicidad_horizontal)}, {publicidad_horizontal[0][1]} -> colocado')  # [0][1] porque es una lista que contiene una tupla
        banner_en_curso = bloques.banner_horizontal_raw
        banner_en_curso = banner_en_curso.replace(
            '##url##', str(publicidad_horizontal[0][4]))
        banner_en_curso = banner_en_curso.replace(
            '##imagen##', str(publicidad_horizontal[0][3]))
        banner_en_curso = banner_en_curso.replace(
            '##alt##', str(publicidad_horizontal[0][6]))
        publicidad_horizontal = publicidad_horizontal.clear()  # type: ignore
        return banner_en_curso
    elif len(publicidad_horizontal) == 0:
        banner_en_curso = ''
        return banner_en_curso


def input_trabajos_a_publicar(tipo: str) -> list:
    """Pregunta por los trabajos o noticias de cada una de las dos secciones.

    Args:
        tipo (str): Tipo de trabajo: 'compania' o 'produccion'.

    Returns:
        trabajos: Lista con los trabajo o noticias de cada función.
    """
    trabajos = ''
    if tipo == 'compania':
        trabajos = input('¿Trabajos de animales de compañía para publicar?   ')
    elif tipo == 'produccion':
        trabajos = input('¿Trabajos de animales de producción para publicar? ')
    trabajos = limpiar_input(trabajos)
    return trabajos


def limpiar_input(texto) -> list:
    """Deja la lista que el usuario introduce preparada: quita espacios antes y después, elimina espacios dobles y separa el resultado

    Args:
        texto (str): cadena que introduce el usuario

    Returns:
        list: lista con los trabajos/noticias
    """
    texto = texto.strip()
    texto = texto.replace('  ', ' ')
    texto = texto.split(' ')
    return texto


def trabajos_a_mostrar(tipo: str, trabajos: list, numero_registros: int) -> list:
    """Crea el código html con los trabajos o noticias de compañía y de producción

    Args:
        tipo (str): _description_
        trabajos (list): _description_

    Returns:
        list: lista de cada una de los trabajos en html
    """
    posicion_publicidad = 'right' if tipo == 'compania' else 'left'
    cerramos_bbdd = False
    trabajos_lista = []
    publicidad = bloques.publicidad.replace('##posicion##', posicion_publicidad)
    try:
        con = sqlite3.connect('bbdd.sqlite3')
        cursorObj = con.cursor()
        for trabajo_seleccionado in trabajos:
            if trabajo_seleccionado == '' or trabajo_seleccionado == ' ':
                continue
            trabajo_seleccionado = int(trabajo_seleccionado)
            if trabajo_seleccionado == 0:
                trabajos_lista.append(publicidad)
            if trabajo_seleccionado < numero_registros and trabajo_seleccionado != 0:
                # * entra si son trabajos de la bbdd
                logging.info(f'Trabajo en la bbdd: {trabajo_seleccionado}')
                cursorObj.execute(
                    'SELECT * FROM hemeroteca WHERE id=' + str(trabajo_seleccionado) + ';')
                trabajo_en_bbdd = cursorObj.fetchone()
                titular = trabajo_en_bbdd[1]
                url = trabajo_en_bbdd[2]
                imagen = trabajo_en_bbdd[3]
                texto = trabajo_en_bbdd[5]
                trabajos_lista.append(
                    tabla_interior(tipo, imagen, titular, texto, url, trabajo_seleccionado))
                cerramos_bbdd = True
            if trabajo_seleccionado >= numero_registros:
                # * entra si es una noticia de la web y es tratada como trabajo
                trabajo_web(tipo, trabajo_seleccionado, trabajos_lista)
        if cerramos_bbdd == True:
            cursorObj.close()
    except Exception as e:
        logging.warning('❌ Esta sección no se va a publicar')
        logging.warning('Exception occurred while code execution: ' + repr(e))
        os.system(ALERTA)
    return trabajos_lista


def getTextInput():
    """Función para la gestión de la ventana a la hora crear un trabajo en la bbdd
    """
    global resultado
    resultado = texto.get("1.0", "end-1c")
    ventana_principal.quit()
    ventana_principal.destroy()


def abrir_pagina_web(url: str):
    """Función que abre en el navegador una página web

    Args:
        url (str): URL a abrir
    """
    webbrowser.open(url, new=2)


def trabajo_web(tipo: str, trabajo_seleccionado: int, trabajos_lista: list)-> list:
    """Gestiona los trabajos que están en la web. Los inserta en la bbdd y los pone en la lista para publicar

    Args:
        tipo (str): si es de compañía o de producción
        trabajo_seleccionado (int): Trabajo a tratar
        trabajos_lista (list): Lista de trabajos a publicar

    Returns:
        list: Lista de trabajos a publicar
    """
    def criterio(axon): return axon["id"] == trabajo_seleccionado
    noticia_filtrada = list(filter(criterio, noticias_web))
    print()
    print(f'Noticia {trabajo_seleccionado} para publicar y meter en la bbdd:')
    print(f'        {noticia_filtrada[0]["url"]}')
    abrir_pagina_web(noticia_filtrada[0]["url"])
    ventana_para_noticia()
    # * preparamos los datos para meter en la bbdd
    noticia_filtrada[0]['contenido'] = resultado
    # * Cambiamos la variable tipo para la bbdd
    tipo = 'p' if tipo == 'compania' else 'g'
    imagen_bbdd = f'{boletin}c/{trabajo_seleccionado}.jpg'
    datos = (noticia_filtrada[0]['titulo'], noticia_filtrada[0]['url'],
             imagen_bbdd, tipo, noticia_filtrada[0]['contenido'])
    sql_insert(datos)  # type: ignore
    # * Cambiamos la variable tipo para el resto de la app
    tipo = 'compania' if tipo == 'p' else 'produccion'
    # * Incluimos la noticia en la lista para mostrar en el masivo
    trabajos_lista.append(tabla_interior(tipo,
                                         noticia_filtrada[0]['imagen'],
                                         noticia_filtrada[0]['titulo'],
                                         noticia_filtrada[0]['contenido'],
                                         noticia_filtrada[0]['url'],
                                         trabajo_seleccionado))
    return trabajos_lista


def sql_insert(datos: str):
    """Aplica el código SQL para incluir en la bbdd sqlite3

    Args:
        datos (str): Código SQL a ejecutar
    """
    con = sqlite3.connect('bbdd.sqlite3')
    cursorObj = con.cursor()
    cursorObj.execute(
        'INSERT INTO hemeroteca(titular, url, imagen, tipo, contenido) VALUES(?, ?, ?, ?, ?)', datos)
    con.commit()

    
'''def igualar_listas(trabajos_compania: list, trabajos_produccion: list) -> tuple:
    """Iguala las dos listas

    Args:
        trabajos_compania (list): trabajos de animales de compañía
        trabajos_produccion (list): trabajos de animales de producción

    Returns:
        trabajos_compania, trabajos_produccion: las dos listas con la misma longitud
    """
    while len(trabajos_compania) > len(trabajos_produccion):
        logging.info(
            'Se añade una publicidad a la lista de trabajos_produccion')
        publicidad = bloques.publicidad.replace('##posicion##', 'right')
        trabajos_produccion.append(publicidad)
    while len(trabajos_compania) < len(trabajos_produccion):
        logging.info('Se añade una publicidad a la lista de trabajos_compania')
        publicidad = bloques.publicidad.replace('##posicion##', 'left')
        trabajos_compania.append(publicidad)
    return trabajos_compania, trabajos_produccion'''


def recuperar_trabajos():
    """Recuperamos de la bbdd en sql3 los trabajos de animales de compañía (pequeños) y los de producción (grandes).
    El formato es: (id, 'titular', 'url', 'imagen, 'tipo: p o g', 'noticia')

    Returns:
        list:
            trabajos_en_bbdd_compania -> lista con todos los trabajos
            trabajos_en_bbdd_produccion -> lista con todos los trabajos
            ultimo_id: último registro 
    """
    trabajos_en_bbdd = []
    try:
        con = sqlite3.connect('bbdd.sqlite3')
        # trabajos de compañía
        cursorObj = con.cursor()
        cursorObj.execute(
            'SELECT * FROM hemeroteca WHERE tipo = "p" ORDER BY "titular";')
        trabajos_en_bbdd = cursorObj.fetchall()
        
        # obtenemos el registro mas alto
        cursorObj = con.cursor()
        cursorObj.execute(
            'SELECT max(id) FROM hemeroteca;')
        ultimo_id = cursorObj.fetchone()[0]
        cursorObj.close()
        return trabajos_en_bbdd, ultimo_id
    except Exception as e:
        logging.warning('❌ No se pudo acceder a la tabla de trabajos SQL3')
        logging.warning('Exception occurred while code execution: ' + repr(e))
        os.system(ALERTA)


def destacadas_a_mostar(noticias_a_usar: list, axon: list):
    """Gestión de las noticias destacadas. Esta programado para admitir varias

    Args:
        noticias_a_usar (list): Lista de noticias destacadas seleccionadas, solo las ID
        axon (list): Lista de noticias

    Returns:
        str: html con las noticias destacadas con banner entre medias
        existe_noticia_destacada: bool -> indica si hay o no noticia destacada
    """
    noticias_destacadas = ''
    try:
        for noticia in noticias_a_usar:
            noticia_destacada = bloques.noticia_destacada
            noticia = int(noticia)
            logging.info(f'Tratando la noticia destacada: {noticia}')
            def criterio(axon): return axon["id"] == noticia
            noticia_filtrada = list(filter(criterio, axon))
            imagen_local = descarga_imagen(
                noticia_filtrada[0]['imagen'], noticia)
            noticia_destacada = noticia_destacada.replace(
                '##imagen##', str(imagen_local))
            noticia_destacada = noticia_destacada.replace(
                '##ancho##', str(320))
            # noticia_destacada = noticia_destacada.replace('##alto##', str(alto))
            noticia_destacada = noticia_destacada.replace(
                '##noticia_titular##', noticia_filtrada[0]['titulo'])
            noticia_destacada = noticia_destacada.replace(
                '##contenido##', noticia_filtrada[0]['contenido'])
            noticia_destacada = noticia_destacada.replace(
                '##noticia_enlace##', noticia_filtrada[0]['url'])
            noticia_destacada = noticia_destacada + \
                creacion_banners(publicidad_horizontal)
            noticias_destacadas = noticias_destacadas + noticia_destacada
    except Exception as e:
        logging.warning('❌ Esta sección no se va a publicar')
        noticias_destacadas = ''
    return noticias_destacadas


def read_wordpress(api_url: str) -> list:
    """Lee los post en WordPress

    Returns:
        list: Lista en bruto con todos los post solicitados
    """
    # wordpress_credentials = datos_de_acceso.WORDPRESS_USER + \
    #     ":" + datos_de_acceso.WORDPRESS_PASSWORD
    # wordpress_token = base64.b64encode(wordpress_credentials.encode())
    # wordpress_header = {'Authorization': 'Basic ' + wordpress_token.decode('utf-8')}
    response = requests.get(api_url)
    response_json = response.json()
    return response_json


def creacion_lista_noticias(numero_registros: int, noticias: list) -> list:
    """Crea la lista que contiene el diccionario con cada noticia por separado. 
    El formato es: {'id': número, 'url': '…', 'imagen': '…', 'titulo': '…', 'contenido': '…'}

    Args:
        numero_registros (int): número por el que empieza la lista de noticias
        noticias (list): noticias

    Returns:
        list: Lista de noticias: axon[noticia]
    """
    axon = []
    longitud_de_noticia = 400
    numero_de_palabras = 70
    for noticia in noticias:
        titulo = noticia['title']['rendered'].strip()
        titulo = limpieza_de_titulares(titulo)
        contenido_tratado = ''
        contenido_tratado = noticia['content']['rendered']
        contenido_tratado = strip_tags(contenido_tratado)
        contenido_tratado = re.sub('&nbsp;', ' ', contenido_tratado)
        contenido_tratado = re.sub('  ', ' ', contenido_tratado)
        contenido_tratado = contenido_tratado.strip(' ')
        contenido_tratado = contenido_tratado.replace(
            noticia['title']['rendered'], '', 1)
        # si queremos extaer los "longitud_de_noticia" caracteres de la noticia
        # contenido_tratado = contenido_tratado[0:longitud_de_noticia] + '... '
        # si queremos extraer las "numero_de_palabras" primeras palabras
        contenido_tratado = " ".join(contenido_tratado.split()[:numero_de_palabras]) + ' ... '
        axon.append({'id': numero_registros,
                     'url': noticia['link'],
                     'imagen': noticia['yoast_head_json']['og_image'][0]['url'],
                     'titulo': titulo,
                     'contenido': contenido_tratado})
        numero_registros += 1
    return axon


def fusion_trabajos_y_banners(trabajos_compania: list, publicidad_horizontal: list) -> str:
    """Fusionamos los trabajos_compania y de trabajos_produccion y entre cada tabla horizontal colocamos un banner

    Args:
        trabajos_compania (list): lista de trabajos a publicar de animales de compañía
        publicidad_horizontal (list): Lista de banners a incluir

    Returns:
        str: el html de la parte de los trabajos
    """
    html_trabajos = ''
    # * Creamos los pares de trabajos que van enfrentados
    for enfrentadas in range(0, len(trabajos_compania), 2):
        html_trabajos = html_trabajos + bloques.bloque_exterior_funcion + \
            creacion_banners(publicidad_horizontal)  # type: ignore
        html_trabajos = html_trabajos.replace(
            '##bloque izq##', trabajos_compania[enfrentadas], 1)
        html_trabajos = html_trabajos.replace('##posicion##', 'left')
        # Verificar si existe el elemento derecho
        if enfrentadas + 1 < len(trabajos_compania):
            html_trabajos = html_trabajos.replace(
                '##bloque der##', trabajos_compania[enfrentadas+1], 1)
            html_trabajos = html_trabajos.replace('##posicion##', 'right')
        else:
            html_trabajos = html_trabajos.replace('##bloque der##', bloques.publicidad, 1)
            html_trabajos = html_trabajos.replace('##posicion##', 'right')
    return html_trabajos


def eliminar_noticias_duplicadas(bbdd_a_tratar: list) -> list:
    """Eliminamos las noticias y trabajos que están en la lista de noticias

    Args:
        bbdd_a_tratar (list): _description_

    Returns:
        list: _description_
    """
    lista_de_noticias_unicas = []
    for noticia in bbdd_a_tratar:
        if noticia not in lista_de_noticias_unicas:
            lista_de_noticias_unicas.append(noticia)
    return lista_de_noticias_unicas


def noticias_a_mostrar(noticias: list, axon: list, publicidad_horizontal: list) -> str:
    """Es función se encarga de toda la gestión de las noticias: desde su introducción hasta el final, cuando sale como html con los banners

    Args:
        noticias (list): lista de noticias a publicar
        axon (list): Lista de las noticias
        publicidad_horizontal (list): lista de los banners

    Returns:
        str: El html de las noticias con los banners
    """
    noticias_colocadas = []
    try:
        pase = 1
        for noticia in noticias:
            noticia = int(noticia)
            logging.info(f'Tratando la noticia: {noticia}')
            if noticia == 0:
                # * Si es 0 es un bloque de pb cuadrado
                if pase % 2 != 0:
                    publicidad = bloques.publicidad.replace(
                        '##posicion##', 'left')
                    noticias_colocadas.append(publicidad)
                else:
                    publicidad = bloques.publicidad.replace(
                        '##posicion##', 'right')
                    noticias_colocadas.append(publicidad)
            else:
                # * Si no es pb, es una noticia
                def criterio(axon): return axon["id"] == noticia
                noticia_filtrada = list(filter(criterio, axon))
                noticias_colocadas.append(
                    tabla_interior('comun',
                                   noticia_filtrada[0]['imagen'], noticia_filtrada[0]['titulo'],
                                   noticia_filtrada[0]['contenido'], noticia_filtrada[0]['url'],
                                   noticia_filtrada[0]['id']))
            pase += 1
    except Exception as e:
        logging.warning('❌ Esta sección no se va a publicar')
        logging.warning(
            '   Exception occurred while code execution: ' + repr(e))
        os.system(ALERTA)
        noticias_colocadas = ''
    longitud = len(noticias_colocadas)
    print(f"Noticias generadas: {longitud}")
    
    # * Vemos si son impares las noticias y si lo son mete en el segundo hueco el banner del Peq Ani Rev
    if longitud % 2 != 0:
        noticias_colocadas = noticias_impares(noticias_colocadas) # type: ignore
        longitud += 1
        publicidad_horizontal_temp = publicidad_horizontal
        for banner in publicidad_horizontal_temp:
            if banner[1] == 'Pequeños Animales (R)evolution':
                publicidad_horizontal_temp.remove(banner)
        publicidad_horizontal = publicidad_horizontal_temp
        print()
        
    # * Creamos el cuerpo sin las noticias: esqueleto de par de noticias y debajo un banner
    bloque_final_con_noticias = ''
    numero = 0
    for numero in range(0, (int(longitud/2))):
        bloque_final_con_noticias = bloque_final_con_noticias + bloques.bloque_exterior
        bloque_final_con_noticias = bloque_final_con_noticias + \
            creacion_banners(publicidad_horizontal)  # type: ignore
            
    # * Y metemos las noticias
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

    return bloque_final_con_noticias, publicidad_horizontal


def noticias_impares(noticias_colocadas: list) -> list:
    """Insertar en la segunda posición (índice 1)

    Args:
        noticias_colocadas (list): _description_

    Returns:
        list: _description_
    """
    noticias_colocadas.insert(1, banners.banner_kit_digital_cuadrado)
    return noticias_colocadas


def leer_preferencias():
    """Función para leer las preferencias. Se usa así: print(preferencias['key'])
    Estas preferencias hay que crearlas manualmente

    Returns:
        _type_: JSON de las preferencias
    """
    try:
        with open("preferencias.json", "r") as archivo_preferencias:
            preferencias = json.load(archivo_preferencias)
        return preferencias
    except Exception as e:
        logging.warning('❌ No se pudo acceder a las preferencias.json')
        logging.warning('Exception occurred while code execution: ' + repr(e))
        os.system(ALERTA)
    finally:
        pass


def banners_gestion(ahora) -> list:
    """Se conecta a la bbdd sqlite3 (tabla de "publicidad"), para recoger todos los banner que se publican ese día y los ordena según su prioridad.
    Después manda la lista a cada una de las funciones que gestionan los banners de las empresas que están en el archivo 'banners_gestion.py'. Estas funciones, si encuentran su banner en la lista, ejecutan su lógica para mostrarlos de forma aleatoria, por periodos, etc.

    Returns:
        list: Lista ordenada con los banners a publicar en el día.
    """
    DIA = str
    if ahora.isoweekday() == 1:
        DIA = 'l'
    elif ahora.isoweekday() == 2:
        DIA = 'm'
    elif ahora.isoweekday() == 3:
        DIA = 'x'
    elif ahora.isoweekday() == 4:
        DIA = 'j'
    elif ahora.isoweekday() == 5:
        DIA = 'v'
    elif ahora.isoweekday() == 6:
        DIA = 'l'
    elif ahora.isoweekday() == 7:
        DIA = 'l'
    try:
        con = sqlite3.connect('bbdd.sqlite3')
        cursorObj = con.cursor()
        cursorObj.execute(
            'SELECT * FROM publicidad WHERE ' + DIA + ' = "1" and exclusiva = "horizontal";')  # type: ignore
        publicidad_horizontal = cursorObj.fetchall()
        cursorObj.close()
        # * Desglosamos la lista en los 4 grupos
        # ? Se puede hacer por filter o por comprension
        # publicidad_final = [publicidad for publicidad in publicidad_horizontal if publicidad_horizontal[2] == 'final']
        # criterio = lambda prioridad: publicidad_horizontal[2] == 'final'
        # # Filtrar elementos utilizando la función lambda
        # publicidad_cliente = list(filter(criterio, publicidad_horizontal))
        destacado = []
        cliente = []
        cliente_final = []
        interno_destacado = []
        interno = []
        final = []
        for publicidad in publicidad_horizontal:
            if publicidad[2] == 'destacado':
                destacado.append(publicidad)
            elif publicidad[2] == 'cliente':
                cliente.append(publicidad)
            elif publicidad[2] == 'cliente final':
                cliente_final.append(publicidad)
            elif publicidad[2] == 'interno destacado':
                interno_destacado.append(publicidad)
            elif publicidad[2] == 'final':
                final.append(publicidad)
            else: # publicidad[2] == 'interno'
                interno.append(publicidad)
        # * Añadimos las funciones importadas que modifican los banners de algunas campañas publicitarias: aletorios, según fechas, etc
        #cliente = pb_talleres_del_sur(cliente, ahora)
        #cliente = pb_boehringer_combo_hasta_SEP(cliente, ahora)
        cliente = pb_ecuphar(cliente, ahora)
        random.shuffle(cliente)
        random.shuffle(interno)
        publicidad_horizontal = destacado + cliente + cliente_final + interno_destacado + interno + final
    except Exception as e:
        logging.warning('❌ Error en la función: gestion_publicidad')
        logging.warning('Exception occurred while code execution: ' + repr(e))
        os.system(ALERTA)
        publicidad_horizontal = []
    return publicidad_horizontal


def fecha_lanzamiento():
    """Gestionamos la fecha de salida del masivo. Podemos poner una fecha (aaa/mm/dd) o cualquiera de estas tres expresiones: 'mañana', 1 o +1

    Returns:
        fecha_salida (fecha): Fecha de publicación del masivo
    """
    fecha_salida = input(
        '¿Fecha de emisión? (nada o para otro día: aaaa/mm/dd ó +1): ')
    fecha_salida = fecha_salida.replace('-','/')
    if not fecha_salida:
        fecha_salida = datetime.now()
    else:
        try:
            if fecha_salida == '1' or fecha_salida == '+1' or fecha_salida.lower() == 'mañana':
                fecha_salida = datetime.now()
                fecha_salida = fecha_salida + timedelta(days=1)
            elif fecha_salida == '0':
                fecha_salida = datetime.now()
            else:
                fecha_salida = datetime.strptime(fecha_salida, '%Y/%m/%d')
        except:
            print()
            print('Fecha no valida')
            salir_app()
    return fecha_salida


def nombre_del_archivo():
    """Lee la carpeta donde se almacena los masivos y crea el nombre del siguiente documento.

    Returns:
        nombre_archivo (str)
        numero (int)
    """
    contenido = os.listdir(datos_de_acceso.RUTA_LOCAL)
    archivos_html = []
    for fichero in contenido:
        if os.path.isfile(os.path.join(datos_de_acceso.RUTA_LOCAL, fichero)) and fichero.endswith('.html'):
            fichero = fichero[:-6]
            if fichero.isdigit():
                archivos_html.append(int(fichero))
    archivos_html.sort()
    ultimo_publicado = archivos_html[-1]
    nombre_archivo = str(ultimo_publicado+1)+'c'
    nombre_carpeta = nombre_archivo
    try:
        os.mkdir(nombre_carpeta)
    except FileExistsError:
        if not os.listdir(nombre_carpeta):
            os.rmdir(nombre_carpeta)
            print(f"Carpeta '{nombre_carpeta}' estaba vacía y fue eliminada.")
            os.makedirs(nombre_carpeta)
        else:
            print(f"Carpeta '{nombre_carpeta}' ya existe y no está vacía.")
            salir_app()
    return nombre_archivo, ultimo_publicado+1


def crear_campaña_mailerlite(nombre: str, asunto: str, contenido: str, segmentos: str):
    """Crear una campaña programada en MailerLite
    https://developers.mailerlite.com/docs/campaigns.html#get-a-campaign
    
    Args:
        nombre: str, 
        asunto: str, 
        contenido: str, es html
        segmentos: str, 
    Returns:
        _type_: _description_
    """
    url = "https://connect.mailerlite.com/api/campaigns"
    headers = {
        "Authorization": f"Bearer {datos_de_acceso.MAILERLITE_API_KEY}",
        "Content-Type": "application/json"
    }
    # Estructura correcta para MailerLite
    data = {
        "name": nombre,
        "language_id": 8,
        "type": "regular",
        "emails": [
            {
                "subject": asunto,
                "from": "suscripciones@axoncomunicacion.net",
                "from_name": "Canal Veterinario",
                "content": contenido
            }
        ],
        "segments": segmentos
    }
        
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        print("Creando campaña en MailerLite")
        # print("Tipo de contenido:", type(contenido))
        # print("Datos enviados (corregidos):", json.dumps(data, indent=2, ensure_ascii=False))
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"Error HTTP {e.response.status_code}: {e.response.text}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error de conexión: {e}")
        return None


def salir_app():
    """Sale de la aplicación si ocurre un error grave y emite un sonido de alerta.
    """
    logging.warning(
        '❌ Cuidado: Hay un error grave. Se procede a salir de la aplicación.')
    os.system(ALERTA)
    sys.exit(1)


def print_response(response):
    """Chequeo del funcionamiento de la API de Acumbamail con su respuesta.

    Args:
        response (json): Respuesta de la API de Acumbamail.
    """
    print(f'{response.text=}')
    pprint(response.json())
    print(f'{response.status_code=}')
    print(f'{response.headers=}')


def obtener_asunto(html_content: str, existe_noticia_destacada: bool) -> str:
    """Obtiene del html es asunto de la campaña. El asunto sera por defecto el primer trabajo de animales de compañía.

    Args:
        html (str): html del archivo.
        existe_noticia_destacada (bool): indica si hay o no noticias destacadas.

    Returns:
        str: Asunto de la campaña si encuentra la etiqueta, si no, avista del error
    """
    numero = 0
    if existe_noticia_destacada == True:
        os.system(ALERTA)
        pregunta_asunto = input('Hay una noticia destacada: ¿Qué asunto quieres usar (0: destacada o 1: primer trabajo -por defecto-)?: ')
        if int(pregunta_asunto) == 0:
            numero = 0
        else:
            numero = 1
    pattern = r'<td\s[^>]*class="heading"[^>]*>(.*?)<\/td>'
    coincidencias = re.findall(pattern, html_content)
    if coincidencias:
        asunto = coincidencias[numero]
        asunto = html.unescape(asunto)
    else:
        print()
        logging.warning('❌ Cuidado: No hay asunto.')
        os.system(ALERTA)
        return ' '
    return asunto


def extraer_agenda(numero_anterior: int) -> str:
    """
    Extrae el contenido entre los comentarios HTML <!-- agenda --> y <!-- fin agenda -->
    
    Args:
        numero_anterior (int): Número anterior que contiene la agenda
        
    Returns:
        str: Contenido encontrado entre los comentarios, o '' si no se encuentra
    """
    nombre_numero_anterior =str(numero_anterior)+"c.html"
    try:
        with open(datos_de_acceso.RUTA_LOCAL+nombre_numero_anterior, 'r', encoding='utf-8') as file:
            content = file.read()
        pattern = r'<!--\s*agenda\s*-->(.*?)<!--\s*fin agenda\s*-->'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            return match.group(1).strip()
        else:
            logging.warning(f'❌ Cuidado: la agenda no se encontro en el archivo: {nombre_numero_anterior}')
            os.system(ALERTA)
            return ''
    except FileNotFoundError:
        logging.warning(f'❌ Cuidado: la agenda no se sale publicada. No encontro se encontró el archivo               {nombre_numero_anterior}')
        os.system(ALERTA)
        return ''
    except Exception as e:
        logging.warning(f'❌ Cuidado: la agenda no se sale publicada. Error al procesar el archivo: {str(e)}')
        os.system(ALERTA)
        return ''


def limpieza_de_titulares(titular: str) -> str:
    """Limpia una cadena de texto. Códigos sacados de: https://ascii.cl/es/codigos-html.htm#google_vignette

    Args:
        titular (str): Titular tal y como esta en el Word

    Returns:
        str: Titular limpio
    """
    # * Elementos unicode
    titular = titular.replace('\xa0', ' ')  # Reemplazar espacios raros (non-breaking space)
    titular = titular.replace('\u200b', '')  # Eliminar espacios invisibles
    titular = titular.replace('\u2002', ' ')  # Eliminar espacios invisibles
    # * Limpiamos elementos innecesarios 
    titular = titular.strip()  
    titular = re.sub(r"\s+", ' ', titular) # espacios en blanco o \xa0 y otras rarezas
    titular = titular.replace("&#8216;","\"") # comillas simples
    titular = titular.replace("&#8217;","\"") # comillas simples
    titular = titular.replace('ASUNTO','')
    titular = titular.replace('\'','\"')
    titular = re.sub(r'\.$', '', titular) # elimina el punto final, si lo hay
    titular = titular.replace('&#171;','«') # comillas anguladas de apertura
    titular = titular.replace('&#187;','»') # comillas anguladas de cierre
    titular = titular.replace('&#8220;','“') # comillas de citación - arriba izquierda
    titular = titular.replace('&#8221;','”') # comillas de citación - arriba derecha
    titular = titular.replace('&#8211;','–') # guión corto
    titular = re.sub(r'\s{2,}', ' ', titular) # espacios dobles
    titular = titular.replace('«','\"') # comillas anguladas a comillas dobles
    titular = titular.replace('»','\"') # comillas anguladas a comillas dobles
    titular = ' '.join(titular.split()) # Eliminar espacios múltiples
    titular = titular[:-2] if titular.endswith(" -") else titular
     
    return titular


def ventana_para_noticia():
    """Función para la gestión de la ventana a la hora crear un trabajo en la bbdd.
    """
    global ventana_principal
    global texto
    ventana_principal = tk.Tk()
    ventana_principal.geometry("600x400")
    ventana_principal.title("Introduce el cuerpo de la noticia como html")
    texto = tk.Text(ventana_principal, height=25)
    texto.pack()
    btnRead = tk.Button(ventana_principal, height=2, width=50,
                        text="Introducir datos", command=getTextInput)
    btnRead.pack()
    ventana_principal.mainloop()
    
    
def abrir_archivo() -> str:
    """Abre el cuadro de dialogo para seleccioanr el archivo de Word.

    Returns:
        str: ruta local del archivo.
    """
    root = tk.Tk()
    root.withdraw()  # Oculta la ventana principal de tkinter
    opciones = {
        'defaultextension': '.docx',
        'filetypes': [('Archivos de Word', '*.docx'), ('Todos los archivos', '*.*')],
        'title': 'Seleccionar un archivo'
    }
    ruta_archivo = filedialog.askopenfilename(**opciones)
    if not ruta_archivo:
        print()
        logging.warning(f'❌ No se selecciono ningún archivo, pasas a modo manual')
        os.system(ALERTA)
        modo_manual = True
    return ruta_archivo


def leer_docx(nombre_archivo) -> list:
    """Función que lee el archivo de Word.

    Args:
        nombre_archivo (str): archivo para leer.

    Returns:
        list: Lista con cada línea de texto.
    """
    doc = Document(nombre_archivo)
    contenido = []
    for paragraph in doc.paragraphs:
        contenido.append(paragraph.text)
    return contenido


def buscar_seccion(contenido: list, cadena: str) -> int:
    """Busca dentro del Word (que es una lista de líneas) la cadena que es la linea que contiene el titular de la sección

    Args:
        contenido (list): Archivo de Word
        cadena (str): Titular a buscar

    Returns:
        int: Línea en la que esta el titular
    """
    for indice, elemento in enumerate(contenido):
        if elemento.strip() == cadena.strip():
            break
    else:
        print()
        logging.warning(f'❌ La sección: "{cadena}" NO está en la lista.')
        os.system(ALERTA)
        print()
    return indice


def creacion_lista_titulares(lista: list) -> list:
    """Crea la lista de titulares sin líneas en blanco

    Args:
        lista (list): _description_

    Returns:
        list: _description_
    """
    contenido = []
    for elemento in lista:
        elemento = limpieza_de_titulares(elemento)
        if elemento != '':
            contenido.append(elemento)
        else:
            pass
    return contenido
      

def chequeo_de_titulares(seccion_word: list, seccion:list):
    """Resta los titulares que hay en el word con los que se han encontrado. Si son diferentes avisa y suena la alarma

    Args:
        seccion_word (list): Es la lista que esta en el word.
        seccion (list): Lista encontrada.
    """
    if len(seccion_word) != len(seccion):
        logging.warning(f'❌ {len(seccion_word)-len(seccion)} noticia(s) falta(n).')
        os.system(ALERTA)
        print()
    return


def comprobar_si_estan_todos(coincidencias: list, titulares: list, titlulares_encontrados: list) -> bool:
    """Revisa que todos los titulares del word esten encontrados. Si no, los muestra para su búsqueda manual

    Args:
        coincidencias (list): Lista de artículos encontrados
        titulares (list): Lista de artículos del Word
        titlulares_encontrados (list): Lista de titulares encontrados
    """
    if len(coincidencias) < len(titulares):
        # Todos los elementos no comunes en ambas listas
        no_encontradas = list(set(titulares) ^ set(titlulares_encontrados))  
        print(f'❌ Error: Hay noticias que no se encuantran: {no_encontradas}')
        os.system(ALERTA)
        estan_todas = False
    elif len(coincidencias) == len(titulares):
        print(f'✅ Todos los titulares se encontraron: {" ".join(map(str, coincidencias))}')
        estan_todas = True
    else:
        print(f'❌ Error: Hay noticias de más: {" ".join(map(str, coincidencias))}')
        os.system(ALERTA)
        estan_todas = False
    return estan_todas
      

def busqueda_de_titulares(titulares_del_word: list, trabajos_en_bbdd: list):
    """Función que busca dentro de los trabajos_en_bbdd y noticias_web cada trabajo del word.

    Args:
        titulares_del_word (list): _description_
        trabajos_en_bbdd (list): _description_
        
    Returns:
        _type_: _description_
    """
    coincidencias = []
    titulares_encontrados = []
    esta_ya = False
    for titular in titulares_del_word:
        if 'Opinión Antonio' in titular[0:18]:
            coincidencias.append(144)
            titulares_encontrados.append(titular)
            print(f'- 144 : {titular}')  
            esta_ya = True
        for trabajo in trabajos_en_bbdd:
            if titular in limpieza_de_titulares(trabajo[1]): 
                coincidencias.append(trabajo[0])
                titulares_encontrados.append(titular)
                print(f'- {trabajo[0]} : {titular}')  
                esta_ya = True
        for noticia in noticias_web:
            if titular in noticia['titulo'] and esta_ya == False:
                coincidencias.append(noticia['id'])
                titulares_encontrados.append(titular)
                print(f'- {noticia["id"]} : {titular}')  
                esta_ya = True
    return coincidencias, titulares_encontrados









if __name__ == '__main__':

    # * Inicializar colorama
    init()

    # * Configuración de logging
    logging.basicConfig(level=logging.INFO,
                        format='-%(levelname)-8s [Línea: %(lineno)-4s Función: %(funcName)-18s] %(message)s')
    # logging.debug('Mensaje de traza')
    # logging.info('Mensaje Informativo, algo funciona como se espera')
    # logging.warning('Peligro')
    # logging.error('Error')

    logging.debug('Comienzo')
    os.system('clear')
    locale.setlocale(locale.LC_ALL, "es_ES")

    # * Variables 
    imagen_local = ''
    ancho = 0
    alto = 0
    ALERTA = "afplay alerta.mp3"
    global modo_manual
    modo_manual = False


    print('------------------')
    print('Creador de masivos')
    print('------------------')
    print()
    print()

    print("0 = Dejar hueco relleno")
    print("Nº  | Título")
    print()

    # * Se recojen tres bbdd: la bbdd local; los trabajos de pequeños animales de la web; y las noticias de la web
    # * Recogemos los trabajos de animales de compañía de la bbdd local
    trabajos_en_bbdd, ultimo_id = recuperar_trabajos()
    print('Trabajos de animales de compañía:')
    print(f"-----|-{'-'*110}")
    for trabajo in trabajos_en_bbdd:
        print(f"{trabajo[0]:>4} | {trabajo[1][0:130]}")
    print()
    TRABAJOS_A_MOSTRAR = 100
    # * &offset=10") # con esta añadido nos saltamos los 10 primeros porque siempre hay un desfase. ¿Merece la pena usarlo?: Por ejemplo si no la encuentra a lo mejor si es buena idea añadirlo
    # Recogemos los últimos trabajos de pequeños animales de la web
    trabajos_web_peq = read_wordpress(
        f"https://axoncomunicacion.net/wp-json/wp/v2/posts?categories[]=477&page=1&per_page={TRABAJOS_A_MOSTRAR}")
    # Recogemos las noticias de la web
    NOTICIAS_MOSTRADAS = 100  # No puede ser mayor de 100
    noticias = read_wordpress(
        f'https://axoncomunicacion.net/wp-json/wp/v2/posts?page=1&per_page={NOTICIAS_MOSTRADAS}')

    # * Creamos el diccionario axon[noticia] y eliminamos duplicados
    numero_registros = ultimo_id + 1
    bbdd_a_tratar = trabajos_web_peq + noticias
    bbdd_a_tratar = eliminar_noticias_duplicadas(bbdd_a_tratar)
    noticias_web = creacion_lista_noticias(numero_registros, bbdd_a_tratar)
 
    print()
    print(
        f"Últimas {NOTICIAS_MOSTRADAS} noticias y {TRABAJOS_A_MOSTRAR} trabajos:")
    print(f"-----|-{'-'*104}")
    for noticia in noticias_web:
        print(f"{noticia['id']:>4} | {noticia['titulo'][0:130]}")

    print()
    print()
    ahora = fecha_lanzamiento()
    publicidad_horizontal = banners_gestion(ahora)
    print(f'Fecha del masivo: {ahora.strftime("%A, %d de %B de %Y")}') # type: ignore
    print()
    nombre_archivo, boletin = nombre_del_archivo()
    print(f'Se va a publicar: {nombre_archivo}')
    print()
    print(
        f'Hoy salen publicados {len(publicidad_horizontal)} banners (sin contar con los extras):')
    for banner in publicidad_horizontal:
        print(f'  -{banner[1]}')

    print()
      
    # * Leemos el archivo de Word del escritorio
    try:
        archivo_docx = leer_docx(datos_de_acceso.RUTA_AL_WORD_INFORMAVET)
        """Este código abre el cuadro de dialogo para leer el word con las noticias
        archivo_docx = abrir_archivo()
        archivo_docx = leer_docx(archivo_docx)"""
    except Exception as e:
        print()
        logging.warning('Exception occurred while code execution: ' + repr(e))    
        logging.warning(f'❌ El archivo no esta en el escritorio, o algo salio mal. Pasas a modo manual.')
        os.system(ALERTA)
        modo_manual = True
        existe_noticia_destacada = False
        estan_todas_compania = False
        estan_todas_produccion = False
    
    # * Analizamos el archivo de Word 
    if modo_manual == False:
        print('Se encontro el Word con el material. Entramos en el modo automático.')    
        titulares_destacados = buscar_seccion(archivo_docx, 'NOTICIAS DESTACADAS')
        titulares_compania = buscar_seccion(archivo_docx, 'TRABAJOS ANIMALES DE COMPAÑÍA')
        titulares_noticias = buscar_seccion(archivo_docx, 'NOTICIAS GENERALEs')
        """
        Esquemas de datos usados:
        -trabajos_en_bbdd: (id, 'titular', 'url', 'imagen, 'tipo: p o g', 'noticia')
        -noticias_web: {'id': número, 'url': '…', 'imagen': '…', 'titulo': '…', 'contenido': '…'}
        """

        # * Analizamos el archivo de Word: Noticias destacadas        
        titulares_destacados_word = archivo_docx[titulares_destacados+1:titulares_compania]
        titulares_destacados_word = creacion_lista_titulares(titulares_destacados_word)
        existe_noticia_destacada = False
        print()
        print(f'{Fore.GREEN}Hay {len(titulares_destacados_word)} noticia(s) destacada(s):{Style.RESET_ALL}')
        if len(titulares_destacados_word) != 0:
            coincidencias_destacados = []
            destacados_encontrados = []
            esta_ya = False
            for titular in titulares_destacados_word:
                for noticia in noticias_web:
                    if titular in noticia['titulo']: # and esta_ya == False:
                        coincidencias_destacados.append(noticia['id'])
                        destacados_encontrados.append(titular)
                        print(f'- {noticia["id"]} : {titular}')  
                        esta_ya = True
            estan_todas_destacadas = comprobar_si_estan_todos(coincidencias_destacados, titulares_destacados_word, destacados_encontrados) 
            existe_noticia_destacada = True
                
        # * Analizamos el archivo de Word: Animales de compañia        
        titulares_compania_word = archivo_docx[titulares_compania+1:titulares_noticias]
        titulares_compania_word = creacion_lista_titulares(titulares_compania_word)
        print()
        print(f'{Fore.GREEN}Hay {len(titulares_compania_word)} titulares de Animales de Compañia incorporados:{Style.RESET_ALL}')
        coincidencias_compania, titulares_encontrados_peq = busqueda_de_titulares(titulares_compania_word, trabajos_en_bbdd)
        estan_todas_compania = comprobar_si_estan_todos(coincidencias_compania, titulares_compania_word, titulares_encontrados_peq)                  

        # * Analizamos el archivo de Word: Noticias    
        titulares_noticias_word = archivo_docx[titulares_noticias+1:]
        titulares_noticias_word = creacion_lista_titulares(titulares_noticias_word)
        print()
        print(f'{Fore.GREEN}Hay {len(titulares_noticias_word)} titulares de Noticias incorporados:{Style.RESET_ALL}')      
        coincidencias_noticias = []
        noticias_encontradas = []
        esta_ya = False
        for titular in titulares_noticias_word:    
            for noticia in noticias_web:
                if titular[0:100] in noticia['titulo'][0:100]:
                    coincidencias_noticias.append(noticia['id'])
                    noticias_encontradas.append(titular)       
                    print(f'- {noticia["id"]} : {titular}')  
                    esta_ya = True   
        estan_todas_noticias = comprobar_si_estan_todos(coincidencias_noticias, titulares_noticias_word, noticias_encontradas)
        # * fin modo_manual = False
        
    # * En este bloque preguntamos por las noticias de cada sección
    # * En el caso de que esten localizadas se salta la pregunta y se generan solas
    print()
    print()
    print('Introducir, si son pedidos, los trabajos/noticias separadas por espacios.')
    print('Poner pb si es necesario.')
    print()
    # * Noticias destacadas
    if existe_noticia_destacada == True:
        if estan_todas_destacadas == False:
            coincidencias_destacados = input("¿Qué noticias son las destacadas?  ")
            coincidencias_destacados = limpiar_input(coincidencias_destacados)
        noticias_destacadas = destacadas_a_mostar(coincidencias_destacados, noticias_web)
    else:
        noticias_destacadas = ''
    
    # * Trabajos compañia
    if estan_todas_compania == False:
        coincidencias_compania = input_trabajos_a_publicar('compania')
    trabajos_compania = trabajos_a_mostrar(
            'compania', coincidencias_compania, numero_registros)
    print()
    
    # * Noticias
    if estan_todas_noticias == False:
        coincidencias_noticias = input("¿Qué noticias quieres publicar? ")
        coincidencias_noticias = limpiar_input(coincidencias_noticias)
    bloque_final_con_noticias, publicidad_horizontal = noticias_a_mostrar(coincidencias_noticias, noticias_web, publicidad_horizontal)
    
    #todo: meter la función que crea las noticias "noticias_a_mostrar" y trabajos_compania para que los bannernes se puedan poner de forma continua
    # * Si hay pocas noticias y trabajos metemos banners cuadrados
    print()
    editorial_suma = len(trabajos_compania)+len(coincidencias_noticias)
    if editorial_suma > 0:
        pb_porcentaje = (len(publicidad_horizontal) / editorial_suma) * 100
    else:
        pb_porcentaje = 0.0
    print(f'Porcentaje de banners sobre contenido editorial:')
    print(f'- Número de noticias de contenido editorial: {editorial_suma}')
    print(f'- Número de banners: {len(publicidad_horizontal)}, {pb_porcentaje:.2f}%')
    if pb_porcentaje < 50:
        print('-  Menos del 50% - Insertamos UN banner cuadrado')
        trabajos_compania.insert(1, bloques.publicidad)
    elif 50 <= pb_porcentaje < 53:
        print('- Entre 50% y 53% - Insertamos DOS banners cuadrado')
        trabajos_compania.insert(1, bloques.publicidad)
        trabajos_compania.insert(3, bloques.publicidad)
    elif 53 <= pb_porcentaje < 60:
        print('- Entre 53% y 60% - Insertamos TRES banners cuadrados')
        trabajos_compania.insert(1, bloques.publicidad)
        trabajos_compania.insert(3, bloques.publicidad)
        trabajos_compania.insert(5, bloques.publicidad) 
    elif 60 <= pb_porcentaje < 64:
        print('- Entre 60% y 64%" - Insertamos CUATRO banners cuadrados')
        trabajos_compania.insert(1, bloques.publicidad)
        trabajos_compania.insert(3, bloques.publicidad)
        trabajos_compania.insert(5, bloques.publicidad) 
        trabajos_compania.insert(7, bloques.publicidad) 
    else:
        print("Más del 64%")
        trabajos_compania.insert(1, bloques.publicidad)
        trabajos_compania.insert(3, bloques.publicidad)
        trabajos_compania.insert(5, bloques.publicidad) 
        trabajos_compania.insert(7, bloques.publicidad) 
        trabajos_compania.insert(9, bloques.publicidad) 
        trabajos_compania.insert(11, bloques.publicidad) 
    
    print()
    html_trabajos = fusion_trabajos_y_banners(trabajos_compania, publicidad_horizontal)
    print()  

    # * Gestionamos la cabecera
    comienzo_en_curso = bloques.comienzo
    comienzo_en_curso = comienzo_en_curso.replace(
        '##nombre_archivo##', nombre_archivo)
    comienzo_en_curso = comienzo_en_curso.replace('##numero##', str(boletin))
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
    comienzo_en_curso = comienzo_en_curso.replace(
        '##mes##', meses[str(ahora.month)])  # type: ignore

    # * Vamos uniendo las partes
    resultado = ''
    resultado += comienzo_en_curso + bloques.pb_primer_banner 
    resultado += '<!-- agenda -->' + extraer_agenda(boletin-1) + '<!-- fin agenda -->'
    resultado += noticias_destacadas + html_trabajos

    # * Chequea si todos los banner están publicados. Si no lo están se publican juntos y se avisa
    if len(publicidad_horizontal) >= 1:
        print()
        print()
        logging.warning(
            '❌ Cuidado: los banners horizontales no se han colocado bien')
        os.system(ALERTA)
        print()
        print()
        for n in range(len(publicidad_horizontal)):
            resultado += creacion_banners(publicidad_horizontal)

    # * Vamos uniendo las partes
    resultado += bloque_final_con_noticias
    resultado += bloques.fin

    # * Codificamos a html
    logging.debug('Codificamos a html')
    resultado = html.unescape(resultado)

    # * Creamos el archivo
    logging.debug('Creamos el archivo')
    archivo = str(boletin)+"c.html"
    with open(archivo, mode="w", encoding="utf-8") as fichero:
        print(resultado, file=fichero)

    # * Movemos el archivo y la carpeta de imágenes a la carpeta de destino y abrimos los archivos html en dreamwaver y en Safari
    os.replace(archivo, datos_de_acceso.RUTA_LOCAL+archivo)
    os.replace(str(boletin)+'c', datos_de_acceso.RUTA_LOCAL+str(boletin)+'c')
    comando = 'open ' + '"' + datos_de_acceso.REPOSITORIO + '"'
    subprocess.run(comando, shell=True)
    comando = 'open ' + '"' + datos_de_acceso.RUTA_LOCAL + archivo + '"'
    subprocess.run(comando, shell=True)
    subprocess.run(["open", "-a", "Safari", f'{datos_de_acceso.RUTA_LOCAL}{archivo}'])

    print()
    print('✅ Archivo generado con éxito: 👍')
    print()
    print('Edita el archivo abierto en Dreamweaver.')
    print()
    print()
    input('Pulsa RETORNO cuanto termines de editar y guardar el archivo en Dreamweaver. ')

    # * Creamos la campaña
    nombre_campaña = f'Informa-vet {boletin} - {ahora.strftime("%A")}'
    # Guardamos el archivo que esta en la web (después de su edición en Dreamweaver)
    contenido_html = requests.get(datos_de_acceso.RUTA_PLANTILAS + archivo)
    if contenido_html.status_code != 200:
        print('❌ Cuidado: Error al leer la plantilla de la web. Sigue de forma manual.')
        salir_app()
     
    # * Chequeamos mediante Premailer: no activado, no estoy seguro de las ventajas y me deja un margen que no se como quitar
    """
    p = Premailer(
        base_url= datos_de_acceso.RUTA_PLANTILAS,   # Para URLs absolutas
        preserve_internal_links=False,              # Para anchors internos
        strip_important=True,                       # Eliminar !important
        keep_style_tags=False,                      # Eliminar tags <style>
        remove_classes=True,                        # Limpiar atributos class
        allow_network=False,                        # Evitar descargas externas
        exclude_pseudoclasses=True,                 # Ignorar :hover, etc.
    )
    contenido_html : str = contenido_html.text
    contenido_html : str = p.transform(contenido_html)
    """
    
    contenido_html = contenido_html.text.replace(
         '<img src="', '<img src="https://axoncomunicacion.net/masivos/axon_news/')


    asunto = obtener_asunto(contenido_html, existe_noticia_destacada) 
    segmentos = ["158082924495766841"] # segmento de Informavet

    resultado = crear_campaña_mailerlite(
        nombre_campaña,
        asunto,
        contenido_html,
        segmentos
    )
    
    if resultado:
        print("✅ Campaña creada exitosamente!")
        #print(json.dumps(resultado, indent=2))
        print()
        print('Esperando a que Mailerlite cree la campaña')
        time.sleep(1)
        abrir_pagina_web("https://dashboard.mailerlite.com/campaigns/status/draft")
        print()
        print('✅ Fin de la aplicación: 👍')
        print()
    else:
        print("❌ Error al crear la campaña")


