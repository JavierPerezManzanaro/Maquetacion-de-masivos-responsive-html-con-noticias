# source 'venv_informavet/bin/activate'

#! CUIDADO
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


# * librerías propias
import bloques
import datos_de_acceso
import banners

# * Importar modulos que gestionan los banner si es necesario
# from banners_gestion import 


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
        tipo (str): el tipo que es: compania, produccion, común
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
        tabla_interior = tabla_interior.replace('##posicion##', 'left')
    elif tipo == 'produccion':  # der. producción
        tabla_interior = tabla_interior.replace('##color##', '#0F7888')
        tabla_interior = tabla_interior.replace('##posicion##', 'right')
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


def descarga_imagen(url: str, nombre: int):
    """Descarga las imágenes y las ajusta al tamaño

    Args:
        url (str): es la url: axon[noticia]['imagen']
        nombre (int): número de la noticia/trabajo que sera el nombre del archivo
        ancho (int): ancho a usar

    Returns:
        imagen_local (str): ruta de la imagen
        ancho (int): ancho de la imagen 320px
        alto (int): alto de la imagen
    """
    try:
        extension = url[len(url)-4:len(url)]
        if extension == "webp":
            extension = ".webp"
        if extension == "jpeg":
            extension = ".jpg"
        imagen_local_generica = nombre_archivo+'/'+str(nombre)+extension
        imagen = requests.get(url).content
        with open(imagen_local_generica, 'wb') as handler:
            handler.write(imagen)
        imagen = cv2.imread(imagen_local_generica)
        imagen = imutils.resize(imagen, width=320)
        imagen_local = nombre_archivo+'/'+str(nombre)+'.jpg'
        cv2.imwrite(imagen_local, imagen)
        if extension == ".webp":
            os.remove(imagen_local_generica)          
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
    publicidad = bloques.publicidad.replace(
        '##posicion##', posicion_publicidad)
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
    tipo_bbdd = 'p' if 'compania' else 'g'
    extension_imagen = ''
    if noticia_filtrada[0]['imagen'][-5:] == '.jepg':
        extension_imagen = 'jpg'
    if noticia_filtrada[0]['imagen'][-4:] == '.jpg':
        extension_imagen = 'jpg'
    if noticia_filtrada[0]['imagen'][-4:] == '.png':
        extension_imagen = 'png'
    imagen_bbdd = f'{boletin}c/{trabajo_seleccionado}.{extension_imagen}'
    datos = (noticia_filtrada[0]['titulo'], noticia_filtrada[0]['url'],
             imagen_bbdd, tipo_bbdd, noticia_filtrada[0]['contenido'])
    sql_insert(datos)  # type: ignore
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


def igualar_listas(trabajos_compania: list, trabajos_produccion: list) -> tuple:
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
    return trabajos_compania, trabajos_produccion


def recuperar_trabajos():
    """Recuperamos de la bbdd en sql3 los trabajos de animales de compañía (pequeños) y los de producción (grandes)

    Returns:
        list:
            trabajos_en_bbdd_compania -> lista con todos los trabajos
            trabajos_en_bbdd_produccion -> lista con todos los trabajos
            ultimo_id: último registro 
    """
    trabajos_en_bbdd_compania = []
    trabajos_en_bbdd_produccion = []
    try:
        con = sqlite3.connect('bbdd.sqlite3')
        # trabajos de compañía
        cursorObj = con.cursor()
        cursorObj.execute(
            'SELECT * FROM hemeroteca WHERE tipo = "p" ORDER BY "titular";')
        trabajos_en_bbdd_compania = cursorObj.fetchall()
        # trabajos de producción
        cursorObj = con.cursor()
        cursorObj.execute(
            'SELECT * FROM hemeroteca WHERE tipo = "g" ORDER BY "titular";')
        trabajos_en_bbdd_produccion = cursorObj.fetchall()
        # obtenemos el registro mas alto
        cursorObj = con.cursor()
        cursorObj.execute(
            'SELECT max(id) FROM hemeroteca;')
        ultimo_id = cursorObj.fetchone()[0]
        cursorObj.close()
        return trabajos_en_bbdd_compania, trabajos_en_bbdd_produccion, ultimo_id
    except Exception as e:
        logging.warning('❌ No se pudo acceder a la tabla de trabajos SQL3')
        logging.warning('Exception occurred while code execution: ' + repr(e))
        os.system(ALERTA)


def noticias_destacadas(axon: list):
    """Gestión de las noticias destacadas. Esta programado para admitir varias

    Args:
        axon (list): Lista de noticias

    Returns:
        str: html con las noticias destacadas con banner entre medias
        hay_noticia_destacada: bool -> indica si hay o no noticia destacada
    """
    noticias_destacadas = ''
    print()
    noticias = input("¿Qué noticias son las destacadas?  ")
    noticias = limpiar_input(noticias)
    hay_noticia_destacada = False
    try:
        for noticia in noticias:
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
        hay_noticia_destacada = True
    except Exception as e:
        logging.warning('❌ Esta sección no se va a publicar')
        noticias_destacadas = ''
    return noticias_destacadas, hay_noticia_destacada


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
    for noticia in noticias:
        titulo = noticia['title']['rendered'].strip()
        titulo = limpieza_de_tituares(titulo)
        contenido_tratado = ''
        contenido_tratado = noticia['content']['rendered']
        contenido_tratado = strip_tags(contenido_tratado)
        contenido_tratado = re.sub('&nbsp;', ' ', contenido_tratado)
        contenido_tratado = re.sub('  ', ' ', contenido_tratado)
        contenido_tratado = contenido_tratado.strip(' ')
        contenido_tratado = contenido_tratado.replace(
            noticia['title']['rendered'], '', 1)
        contenido_tratado = contenido_tratado[0:longitud_de_noticia] + '... '
        axon.append({'id': numero_registros,
                     'url': noticia['link'],
                     'imagen': noticia['yoast_head_json']['og_image'][0]['url'],
                     'titulo': titulo,
                     'contenido': contenido_tratado})
        numero_registros += 1
    return axon


def fusion_trabajos_y_banners(trabajos_compania: list, trabajos_produccion: list, publicidad_horizontal: list) -> str:
    """Fusionamos los trabajos_compania y de trabajos_produccion y entre cada tabla horizontal colocamos un banner

    Args:
        trabajos_compania (list): lista de trabajos a publicar de animales de compañía
        trabajos_produccion (list): lista de trabajos a publicar de animales de produccion
        publicidad_horizontal (list): Lista de banners a incluir

    Returns:
        str: el html de la parte de los trabajos
    """
    html_trabajos = ''
    # creamos las que van enfrentadas
    for enfrentadas in range(0, len(trabajos_compania)):
        html_trabajos = html_trabajos + bloques.bloque_exterior_funcion + \
            creacion_banners(publicidad_horizontal)  # type: ignore
        html_trabajos = html_trabajos.replace(
            '##bloque izq##', trabajos_compania[enfrentadas], 1)
        html_trabajos = html_trabajos.replace(
            '##bloque der##', trabajos_produccion[enfrentadas], 1)
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


def gestion_noticias(axon: list) -> str:
    """Es función se encarga de toda la gestión de las noticias: desde su introducción hasta el final, cuando sale como html con los banners

    Args:
        axon (list): Lista de las noticias

    Returns:
        str: El html de las noticias con los banners
    """
    print()
    noticias = input("¿Qué noticias quieres publicar? ")
    noticias = limpiar_input(noticias)
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
    
    # * Vemos si son impares las noticias y si lo son mete en el segundo hueco el banner del laser
    if longitud % 2 != 0:
        noticias_colocadas = noticias_impares(noticias_colocadas) # type: ignore
        longitud += 1
        print()
        logging.warning(
            'Eliminar el banner de "Peq Ani Rev" porque usamos el banner cuadrado')
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

    return bloque_final_con_noticias


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
        # todo: que hacer al final


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
        # * desglosamos la lista en los 4 grupos
        # ? se puede hacer por filter o por comprension
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
        # * Añadimos las funciones importadas que modifican los banners de algunas campañas publicitarias: alatorios, según fechas, etc
        #cliente = pb_talleres_del_sur(cliente, ahora)
        #cliente = pb_boehringer_combo_hasta_SEP(cliente, ahora)
        #cliente = pb_boehringer_nexgard_spectra_hasta_SEP(cliente, ahora)
        #cliente = pb_elanco_hasta_JUN(cliente, ahora)
        #cliente = pb_stangest(cliente, ahora)
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

    try:
        os.mkdir(nombre_archivo)
    except OSError as e:
        print("Error creando la carpeta.")
        if e.errno != errno.EEXIST:
            raise
        salir_app()
    return nombre_archivo, ultimo_publicado+1


def createCampaign(name, subject, content, date_send):
    """Crea y manda (a no ser que la fecha sea diferente) una campaña. Solo se pide los argumentos que cambian de una campaña a otra.
    Una vez creada la campaña se lanza automáticamente a no ser que se ponga una date_send.
    https://acumbamail.com/apidoc/function/createCampaign/

    Esta es la ayuda que manda Acumbamail: https://acumbamail.com/api/1/createCampaign/?auth_token=XXXXX&name=XXXXXX&from_name=my_name&from_email=XXXXXX&subject=XXXXX&lists[0]=XXXX

    Args:
        name (string): Nombre de la campaña (no es público)
        subject (string): El asunto de la campaña
        content (string): El html que contendrá la campaña
        date_send (date): (Opcional) Fecha de comienzo del envío. Sólo para envíos programados. (YYYY-MM-DD HH:MM)

    Args que son comunes y no se piden:
        auth_token (string): Tu token de autenticación de cliente
        from_name (string): Nombre del remitente de la campaña
        listas (dict): Los identificadores de las listas a las que se enviará la campaña, o de los segmentos a los que se quiera enviar precedidos de s. No se puede enviar a más de un segmento de una misma lista, ni a un segmento y a una lista a la que pertenezca
        from_email (string): El email desde el que se enviará la campaña, se puede usar Nombre <email@dominio.com>
        tracking_urls (integer): (Opcional) Sustituir enlaces para seguimiento de clics. Por defecto=1
        complete_json (integer): Para que devuelva un json completo con formato completo. Por defecto=0
        https: Activa "1" o desactiva "0" usando http

    Returns:
        respuesta (json)
    """
    respuesta = ''
    api_url = "https://acumbamail.com/api/1/createCampaign/"
    # Parámetros de la solicitud
    params = {
        "auth_token": datos_de_acceso.TOKEN_ACUMBAMAIL,
        "name": name,
        "from_name": "Suscripciones",
        "from_email": "suscripciones@axoncomunicacion.net",
        "subject": subject,
        "content": content,
        "https": "1",
        "date_send": date_send,
    }
    # añadimos las listas necesarias
    params_combinado = params | datos_de_acceso.DICCIONARIO_DE_LISTAS
    try:
        # Realizar la solicitud POST a la API
        response = requests.post(api_url, data=params_combinado)
        # Verificar el estado de la respuesta
        if response.status_code == 200:
            print()
            print("Campaña creada en Acumbamail con éxito")
            # Puedes imprimir o manejar la respuesta de la API aquí
            respuesta = json.loads(response.text)
        else:
            print(
                f"Error en la solicitud. Código de estado: {response.status_code}")
            salir_app()
    except Exception as e:
        print(f"Error a la hora de solicitar POST a la API: {str(e)}")
        salir_app()
    return respuesta


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


def obtener_asunto(html_content, hay_noticia_destacada):
    """Obtiene de la bbdd el asunto de la campaña. El asunto sera por defecto el primer trabajo de animales de compañía.

    Args:
        html (str): html del archivo.

    Returns:
        str: Asunto de la campaña si encuentra la etiqueta, si no, solamente 'In-formaVET: ' pero avista del error.
    """
    numero = 0
    if hay_noticia_destacada == True:
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
        # asunto = asunto.replace("&aacute;", "á")
        # asunto = asunto.replace("&eacute;", "é")
        # asunto = asunto.replace("&iacute;", "í")
        # asunto = asunto.replace("&oacute;", "ó")
        # asunto = asunto.replace("&uacute;", "ú")
        # asunto = asunto.replace("&Aacute;", "Á")
        # asunto = asunto.replace("&Eacute;", "É")
        # asunto = asunto.replace("&Iacute;", "Í")
        # asunto = asunto.replace("&Oacute;", "Ó")
        # asunto = asunto.replace("&Uacute;", "Ú")
        # asunto = asunto.replace("&ntilde;", "ñ")
        # asunto = asunto.replace("&Ntilde;", "Ñ")
        # asunto = asunto.replace("&iexcl;", "¡")
        # asunto = asunto.replace("&iquest;", "¿")
        # asunto = asunto.replace("&quot;", "â€œ")
        # asunto = asunto.replace("&quot;", "â€")
    else:
        print()
        logging.warning('❌ Cuidado: No hay asunto.')
        os.system(ALERTA)
        return 'In-formaVET: '
    return 'In-formaVET: ' + asunto


def limpieza_de_tituares(titular: str) -> str:
    """Limpia una cadena de texto. Códigos sacados de: https://ascii.cl/es/codigos-html.htm#google_vignette

    Args:
        titular (str): Titular tal y como sale del Wordpress

    Returns:
        str: Titular limpio
    """
    titular = titular.replace("  "," ")
    titular = titular.replace("&#8216;","\"")
    titular = titular.replace("&#8217;","\"")
    titular = titular.replace('ASUNTO','')
    titular = titular.strip()       
    titular = titular.replace('Espacio ECCOA','')
    titular = titular.replace('\'','\"')
    titular = re.sub(r'\.$', '', titular)
    titular = titular.replace('&#171;','«') # comillas anguladas de apertura
    titular = titular.replace('&#187;','»') # comillas anguladas de cierre
    titular = titular.replace('&#8220;','“') # comillas de citación - arriba izquierda
    titular = titular.replace('&#8221;','”') # comillas de citación - arriba derecha
    titular = titular.replace('&#8211;','–') # guión corto
    titular = re.sub(r'\s{2,}', ' ', titular)
    titular = titular.strip()       
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
    """Busca dentro del Word (que es una lista de líneas) la cadena que es la linea que contiene el titular de la sección.

    Args:
        contenido (list): Archivo de Word
        cadena (str): Titular a buscar

    Returns:
        int: Línea en la que esta el titular
    """
    for indice, elemento in enumerate(contenido):
        if elemento == cadena:
            break
    else:
        print()
        logging.warning(f'❌ La sección {cadena} NO está en la lista"')
        os.system(ALERTA)
        modo_manual = True
        #todo ver que pasa
        print()
    return indice


def limpiar_lista(lista: list) -> list:
    """Limpua el contenido de una lista que solo contien str

    Args:
        lista (list): _description_

    Returns:
        list: _description_
    """
    contenido = []
    for elemento in lista:
        elemento = limpieza_de_tituares(elemento)
        if elemento != '':
            contenido.append(elemento)
        else:
            pass
    lista = contenido
    return lista


def imprimir_titulares(titulares: list, seccion: str):
    print()
    print(f'Hay {len(titulares)} {seccion}:')
    for entrada in titulares:
            print(f'- {entrada}')



if __name__ == '__main__':

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

    trabajos_en_bbdd_compania, trabajos_en_bbdd_produccion, ultimo_id = recuperar_trabajos()  # type: ignore
    print('Trabajos de compañía:')
    print(f"-----|-{'-'*110}")
    for trabajo in trabajos_en_bbdd_compania:
        print(f"{trabajo[0]:>4} | {trabajo[1][0:130]}")
    print()
    print('Trabajos de producción:')
    print(f"-----|-{'-'*110}")
    for trabajo in trabajos_en_bbdd_produccion:
        print(f"{trabajo[0]:>4} | {trabajo[1][0:130]}")

    TRABAJOS_A_MOSTRAR = 35
    #todo &offset=10") # con esta añadido nos saltamos los 10 primeros porque siempre hay un desfase. ¿Merece la pena usarlo?: Por ejemplo si no la encuentra a lo mejor si es buena idea añadirlo
    # * Recogemos los últimos trabajos de pequeños animales de la web
    trabajos_web_peq = read_wordpress(
        f"https://axoncomunicacion.net/wp-json/wp/v2/posts?categories[]=477&page=1&per_page={TRABAJOS_A_MOSTRAR}")

    # * Recogemos los últimos trabajos de producción de la web
    trabajos_web_gra = read_wordpress(
        f"https://axoncomunicacion.net/wp-json/wp/v2/posts?categories[]=476&page=1&per_page={TRABAJOS_A_MOSTRAR}")

    """Si en un futuro vemos necesario separa la lista de noticias completas en tres
    print()
    print(f"Últimos {TRABAJOS_A_MOSTRAR} trabajos de pequeños animales:")
    print(f"----|-{'-'*104}")
    for noticia in axon[0:TRABAJOS_A_MOSTRAR]:
        print(f"{noticia['id']:>3} | {noticia['titulo'][0:130]}")

    print()
    print(f"Últimos {TRABAJOS_A_MOSTRAR} trabajos de producción:")
    print(f"----|-{'-'*104}")
    for noticia in axon[TRABAJOS_A_MOSTRAR:(TRABAJOS_A_MOSTRAR*2)]:
        print(f"{noticia['id']:>3} | {noticia['titulo'][0:130]}")
    """

    # * Recogemos las noticias de la web
    NOTICIAS_MOSTRADAS = 100  # No puede ser mayor de 100
    noticias = read_wordpress(
        f'https://axoncomunicacion.net/wp-json/wp/v2/posts?page=1&per_page={NOTICIAS_MOSTRADAS}')

    # * Creamos el diccionario axon[noticia] y eliminamos duplicados
    numero_registros = ultimo_id + 1
    bbdd_a_tratar = trabajos_web_peq + trabajos_web_gra + noticias
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
        f'Hoy salen publicados {str(len(publicidad_horizontal))} banners (sin contar con los extras):')
    for banner in publicidad_horizontal:
        print(f'  -{banner[1]}')

    print()
    print()
    
    # * Leemos el archivo de Word del escritorio
    try:
        archivo_docx = leer_docx(datos_de_acceso.RUTA_AL_WORD_INFORMAVET)
    except Exception as e:
        print()
        """Este código abre el cuadro de dialogo para leer el word con las noticias
        archivo_docx = abrir_archivo()
        archivo_docx = leer_docx(archivo_docx)"""
        logging.warning('Exception occurred while code execution: ' + repr(e))    
        logging.warning(f'❌ No esta el archivo en el escritorio, pasas a modo manual.')
        os.system(ALERTA)
        modo_manual = True
    
    if modo_manual == False:
        # * Analizamos el archivo de Word     
        titular_compania = buscar_seccion(archivo_docx, 'TRABAJOS ANIMALES DE COMPAÑÍA')
        titular_produccion = buscar_seccion(archivo_docx, 'TRABAJOS ANIMALES DE PRODUCCIÓN')
        titular_noticias = buscar_seccion(archivo_docx, 'NOTICIAS GENERALEs ')
        titulares_compania = archivo_docx[titular_compania+1:titular_produccion]
        titulares_compania = limpiar_lista(titulares_compania)
        imprimir_titulares(titulares_compania, 'titulares pequeños')
        titulares_produccion = archivo_docx[titular_produccion+1:titular_noticias]
        titulares_produccion = limpiar_lista(titulares_produccion)
        imprimir_titulares(titulares_produccion, 'titulares producción')
        titulares_noticias = archivo_docx[titular_noticias+1:]
        titulares_noticias = limpiar_lista(titulares_noticias)
        imprimir_titulares(titulares_noticias, 'noticias')    
        
        # * Busca un titular del word dentro de la lista de noticias
        coincidencias_compania = []
        for trabajo in trabajos_en_bbdd_compania:
            if trabajo[1] in titulares_compania:
                coincidencias_compania.append(trabajo[0])
                
        coincidencias_produccion = []
        for trabajo in trabajos_en_bbdd_produccion:        
            if trabajo[1][0:25] == 'Opinión de Antonio Palomo':
                coincidencias_produccion.append(144)
            if trabajo[1] in titulares_produccion:
                coincidencias_produccion.append(trabajo[0])


        coincidencias_noticias = []
        for titular in titulares_noticias:    
            for noticia in noticias_web:
                #print(f"{noticia['id']:>4} | {noticia['titulo'][0:130]}")
                if titular in noticia['titulo']:
                    coincidencias_noticias.append(noticia['id'])           

        print()        
        print(f'{coincidencias_compania=}')
        print(f'{coincidencias_produccion=}')
        print(f'{coincidencias_noticias=}')
        
        salir_app()
    
    #! a partir de aquí es manual
    print()
    print('Los trabajos/noticias separadas con espacios.')
    print()
    noticias_destacadas, existe_noticia_destacada = noticias_destacadas(noticias_web) # type: ignore
    print()
    logging.debug('Trabajos de animales de compañía y producción')
    trabajos_compania = input_trabajos_a_publicar('compania')
    trabajos_compania = trabajos_a_mostrar(
        'compania', trabajos_compania, numero_registros)
    trabajos_produccion = input_trabajos_a_publicar('produccion')
    trabajos_produccion = trabajos_a_mostrar(
        'produccion', trabajos_produccion, numero_registros)

    # * Igualamos las dos listas
    if len(trabajos_compania) != len(trabajos_produccion):  # type: ignore
        trabajos_compania, trabajos_produccion = igualar_listas(
            trabajos_compania, trabajos_produccion)  # type: ignore

    html_trabajos = fusion_trabajos_y_banners(
        trabajos_compania, trabajos_produccion, publicidad_horizontal)

    bloque_final_con_noticias = gestion_noticias(noticias_web)

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
    # todo: añadir año

    # * Vamos uniendo las partes
    resultado = ''
    resultado += comienzo_en_curso + bloques.pb_laservet   
    resultado += bloques.agenda + noticias_destacadas + html_trabajos # type: ignore

    # * Chequea si todos los banner están publicados. Si no lo están se publican y avisa
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
    resultado += banners.setna
    resultado += bloques.fin

    # * Codificamos a html
    logging.debug('Codificamos a html')
    # ? para cuerpos de email charset=ISO-8859-1
    resultado = html.unescape(resultado)
    # resultado = resultado.replace("á", "&aacute;")
    # resultado = resultado.replace("é", "&eacute;")
    # resultado = resultado.replace("í", "&iacute;")
    # resultado = resultado.replace("ó", "&oacute;")
    # resultado = resultado.replace("ú", "&uacute;")
    # resultado = resultado.replace("Á", "&Aacute;")
    # resultado = resultado.replace("É", "&Eacute;")
    # resultado = resultado.replace("Í", "&Iacute;")
    # resultado = resultado.replace("Ó", "&Oacute;")
    # resultado = resultado.replace("Ú", "&Uacute;")
    # resultado = resultado.replace("ñ", "&ntilde;")
    # resultado = resultado.replace("Ñ", "&Ntilde;")
    # resultado = resultado.replace("¡", "&iexcl;")
    # resultado = resultado.replace("¿", "&iquest;")
    # resultado = resultado.replace("Â", "")
    # resultado = resultado.replace("â€œ", "&quot;")
    # resultado = resultado.replace("â€", "&quot;")

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
    print('Archivo generado con éxito: 👍')
    print()
    print('Edita el archivo abierto en Dreamweaver.')
    print()
    print()
    input('Pulsa RETORNO cuanto termines de editar y guardar el archivo en Dreamweaver. ')

    # * Creamos la campaña
    name = 'Informa-vet ' + str(boletin)
    date_send = '2024-12-30 23:00'
    # Guardamos el archivo que esta en la web (después de su edición en Dreamweaver)
    html_content = requests.get(datos_de_acceso.RUTA_PLANTILAS + archivo)
    if html_content.status_code != 200:
        print('❌ Cuidado: Error al leer la plantilla de la web. Sigue de forma manual.')
        salir_app()
    html_content = html_content.text.replace(
        '<img src="', '<img src="https://axoncomunicacion.net/masivos/axon_news/')
    subject = obtener_asunto(html_content, existe_noticia_destacada)
    respuesta = createCampaign(name, subject, html_content, date_send)
    #* Solo continua si la campaña se creo con éxito, si no fue así en la función createCampaign se salio de la aplicación
    url = 'https://acumbamail.com/app/campaign/' + \
        str(respuesta['id']) + '/summary/'  # type: ignore
    print()
    print('Esperando a que Acumbamail cree la campaña.')
    time.sleep(1)
    abrir_pagina_web(url)

    print()
    print('Fin de la aplicación: 👍')
    print()
