# source 'venv_informavet/bin/activate'

#! CUIDADO
# todo por hacer
# ? aviso
# * explicación



from datetime import datetime, date
from os import close, link
import requests
import os
import re
from PIL import Image
from pprint import pprint
import errno
import random
import sqlite3
import logging
import subprocess
import base64
import locale

# * librerias propias
import bloques
import datos_de_acceso
import banners
import funciones




# * *******************
# * Funciones de la app
# * *******************

def execution_time(func):
    """Función para medir tiempo de ejecucuón

    Args:
        func (_type_): _description_
    """
    def wrapper(*args, **kwargs):
        initial_time = datetime.now()
        func(*args, **kwargs)
        final_time = datetime.now()
        time_elapsed = final_time - initial_time
        print(f'La función tardo: {time_elapsed.total_seconds()} segundos')
    return wrapper


def strip_tags(value: str) -> str:
    """
    Elimina el código html <…> y […].

    Args:
        value (str): Cadena a limpiar

    Returns:
        (str): Cadena limpia
    """
    logging.debug('Entra')
    value = re.sub(r'<[^>]*?>', ' ', value)  # elimina <...>
    value = re.sub(r'\[[^>]*?\]', ' ', value)  # elimina [...]
    return value


# decorador @execution_time
def tabla_interior(tipo: str, imagen: str, titular: str, texto: str, url: str, nombre_imagen: int) -> str:
    """Genera la tabla html que contiene un trabajo o la noticia.

    Args:
        tipo (str): el tipo que es: compania, produccion, comun
        imagen (str): url local (bbdd, trabajos) o absoluta (noticias)
        titular (str)
        texto (str)
        url (srt)
        nombre_imagen (srt)

    Returns:
        (str): tabla en html con el trabajo o la noticia
    """
    logging.debug('Entra')
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
        logging.warning(
            '❌ Elemento no generado porque no coincide el tipo con ninguno de los predefinidos')
        os.system(ALERTA)

    # Analiza donde esta la imagen (en remoto o en local)
    if 'https' in imagen:
        imagen_local, ancho, alto = descarga_imagen(imagen, nombre_imagen, 320)
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


def descarga_imagen(url: str, nombre: int, ancho: int):
    """Descarga las imagenes y las ajusta al tamaño.

    Args:
        url (str): es la url: axon[noticia]['imagen']
        nombre (int): número de la noticia/trabajo que sera el nombre del archivo
        ancho (int): ancho a usar

    Returns:
        imagen_local (str): ruta de la imagen
        ancho (int): ancho de la imagen 320px
        alto (int): alto de la imágen
    """
    logging.debug('Entra')
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
        alto = int((int(imagen.size[1]) * ancho) / int(imagen.size[0]))
        imagen = imagen.resize((ancho, alto))
        imagen.save(imagen_local)

    return imagen_local, ancho, alto


def creacion_banners(publicidad_horizontal):
    """Va generando uno a uno cada uno de los banners horizontales periodicos.
    Elige uno al azar, lo crea y lo elimina.

    Args:
        publicidad_horizontal (list): lista compuesta por los datos de la bbdd sqlite3

    Returns:
        str: código html del banner
    """
    logging.debug('Entra')
    if len(publicidad_horizontal) > 1:
        banner_seleccionado = random.choice(publicidad_horizontal)
        logging.info(f'Banner {len(publicidad_horizontal)}, {banner_seleccionado[1]} -> colocado')
        banner_en_curso = bloques.banner_horizontal_raw
        banner_en_curso = banner_en_curso.replace('##url##', str(banner_seleccionado[3]))
        banner_en_curso = banner_en_curso.replace('##imagen##', str(banner_seleccionado[2]))
        banner_en_curso = banner_en_curso.replace('##alt##', str(banner_seleccionado[5]))
        publicidad_horizontal = publicidad_horizontal.remove(banner_seleccionado)
        return banner_en_curso
    elif len(publicidad_horizontal) == 1:
        logging.info(
            f'Banner {len(publicidad_horizontal)}, {publicidad_horizontal[0][1]} -> colocado')  # [0][1] porque es una lista que contiene una tupla
        banner_en_curso = bloques.banner_horizontal_raw
        banner_en_curso = banner_en_curso.replace('##url##', str(publicidad_horizontal[0][3]))
        banner_en_curso = banner_en_curso.replace('##imagen##', str(publicidad_horizontal[0][2]))
        banner_en_curso = banner_en_curso.replace('##alt##', str(publicidad_horizontal[0][5]))
        publicidad_horizontal = publicidad_horizontal.clear()
        return banner_en_curso
    elif len(publicidad_horizontal) == 0:
        banner_en_curso = ''
        return banner_en_curso


def trabajos_a_publicar(tipo: str)-> list:
    """Pregunta por los trabajos o noticias de cada una de las dos secciones.

    Args:
        tipo (str): Tipo de trabajo: 'compania' o 'produccion'

    Returns:
        trabajos: Lista con los trabajo o noticias de cada función
    """
    logging.debug('Entra')
    trabajos = ''
    if tipo == 'compania':
        trabajos = input('¿Trabajos de animales de compañía para publicar?   ')
    elif tipo == 'produccion':
        trabajos = input('¿Trabajos de animales de producción para publicar? ')
    trabajos = trabajos.strip()
    trabajos = trabajos.split(' ')
    return trabajos


def trabajos_a_mostrar(tipo: str, trabajos: list, axon:list)-> list:
    """Crea el código html con los trabajos o noticias de compañia y de producción.

    Args:
        tipo (str): _description_
        trabajos (list): _description_

    Returns:
        _type_: _description_
    """
    logging.debug('Entra')
    posicion_publicidad = 'right' if tipo == 'compania' else 'left'
    cerramos_bbdd = 0
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
            if trabajo_seleccionado < (numero_registros - noticias_mostradas) and trabajo_seleccionado != 0:
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
                cerramos_bbdd = 1
            if trabajo_seleccionado >= (numero_registros - noticias_mostradas):
                # * entra si es una noticia de la web y es tratada como trabajo
                logging.info(f'Trabajo de la web: {trabajo_seleccionado}')
                criterio = lambda axon: axon["id"] == trabajo_seleccionado
                noticia_filtrada = list(filter(criterio, axon))
                trabajos_lista.append(tabla_interior(   tipo,
                                                        noticia_filtrada[0]['imagen'],
                                                        noticia_filtrada[0]['titulo'],
                                                        noticia_filtrada[0]['contenido'],
                                                        noticia_filtrada[0]['url'],
                                                        trabajo_seleccionado))
                logging.warning(
                    '🟡 Noticia como trabajo: Recuerda editarla y meterla en la bbdd')
        if cerramos_bbdd == 1:
            cursorObj.close()
    except Exception as e:
        logging.warning('❌ Esta sección no se va a publicar')
        logging.warning('Exception occurred while code execution: ' + repr(e))
        os.system(ALERTA)
    return trabajos_lista


def igualar_listas(trabajos_compania: list, trabajos_produccion: list)-> tuple:
    """Iguala las dos listas

    Args:
        trabajos_compania (list): trabajos de animales de compañia
        trabajos_produccion (list): trabajops de animales de producción

    Returns:
        trabajos_compania, trabajos_produccion: las dos listas con la misma longuitud
    """
    logging.debug('Entra')
    while len(trabajos_compania) > len(trabajos_produccion):
        logging.info('Se añade una publicidad a la lista de trabajos_produccion')
        publicidad = bloques.publicidad.replace('##posicion##', 'right')
        trabajos_produccion.append(publicidad)
    while len(trabajos_compania) < len(trabajos_produccion):
        logging.info('Se añade una publicidad a la lista de trabajos_compania')
        publicidad = bloques.publicidad.replace('##posicion##', 'left')
        trabajos_compania.append(publicidad)
    return trabajos_compania, trabajos_produccion


def recuperar_trabajos():
    """Recuperamos de la bbdd en sql3 los trabajos de animales de compañia (pequeños) y los de producción (grandes).

    Returns:
        list:
            trabajos_en_bbdd_compania -> lista con todos los trabajos
            trabajos_en_bbdd_produccion -> lista con todos los trabajos
    """
    logging.debug('Entra')
    trabajos_en_bbdd_compania = []
    trabajos_en_bbdd_produccion  = []
    try:
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
        return trabajos_en_bbdd_compania, trabajos_en_bbdd_produccion
    except Exception as e:
        logging.warning('❌ No se pudo acceder a la tabla de trabajos')
        logging.warning('Exception occurred while code execution: ' + repr(e))
        os.system(ALERTA)


def noticias_destacadas(axon: list)->str:
    """Función que gestiona las noticias destacadas. Esta programado para admitir varias.

    Args:
        axon (list): Lista de noticias

    Returns:
        str: html con las noticias destacadas con banner entre medias
    """
    logging.debug('Entra')
    noticias_destacadas = ''
    print()
    noticias = input("¿Qué noticias son las destacadas?  ")
    noticias = noticias.strip()
    try:
        noticias = noticias.split(' ')
        for noticia in noticias:
            noticia_destacada = bloques.noticia_destacada
            noticia = int(noticia)
            logging.info(f'Tratanto la noticia destacada: {noticia}')
            criterio = lambda axon: axon["id"] == noticia
            noticia_filtrada = list(filter(criterio, axon))
            imagen_local, ancho, alto = descarga_imagen(noticia_filtrada[0]['imagen'], noticia, 320)
            noticia_destacada = noticia_destacada.replace('##imagen##', str(imagen_local))
            noticia_destacada = noticia_destacada.replace('##ancho##', str(ancho))
            noticia_destacada = noticia_destacada.replace('##alto##', str(alto))
            noticia_destacada = noticia_destacada.replace('##noticia_titular##', noticia_filtrada[0]['titulo'])
            noticia_destacada = noticia_destacada.replace('##contenido##', noticia_filtrada[0]['contenido'])
            noticia_destacada = noticia_destacada.replace('##noticia_enlace##', noticia_filtrada[0]['url'])
            noticia_destacada = noticia_destacada + creacion_banners(publicidad_horizontal)
            noticias_destacadas = noticias_destacadas + noticia_destacada
    except Exception as e:
        logging.warning('❌ Esta sección no se va a publicar')
        noticias_destacadas = ''
    return noticias_destacadas


def read_wordpress_posts()-> list:
    """Lee los post en el WordPress indicados por numero_de_noticias

    Returns:
        list: Lista en bruto con todos los post solicitados
    """
    logging.debug('Entra')
    wordpress_credentials = datos_de_acceso.wordpress_user + ":" + datos_de_acceso.wordpress_password
    wordpress_token = base64.b64encode(wordpress_credentials.encode())
    # wordpress_header = {'Authorization': 'Basic ' + wordpress_token.decode('utf-8')}
    api_url = f'https://axoncomunicacion.net/wp-json/wp/v2/posts?page=1&per_page={noticias_mostradas}'
    response = requests.get(api_url)
    response_json = response.json()
    return response_json


def gestion_publicidad()->list:
    """Se conecta a la bbdd sqlite3, a la tabla de "publicidad", para recoger todos los banner que se publican ese día

    Returns:
        list: Lista con los banners a publicar en el día
    """
    logging.debug('Entra')
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
    elif ahora.isoweekday() == 6:  # solo esta por si programo un sábado
        DIA = 'l' #? esta para el lunes, cambiar si es otro día
    elif ahora.isoweekday() == 7:  # solo esta por si programo un domingo
        DIA = 'l' #? esta para el lunes, cambiar si es otro día
    try:
        con = sqlite3.connect('bbdd.sqlite3')
        cursorObj = con.cursor()
        cursorObj.execute(
            'SELECT * FROM publicidad WHERE ' + DIA + ' = "1" and exclusiva = "horizontal";') # type: ignore
        publicidad_horizontal = cursorObj.fetchall()
        cursorObj.close()
    except Exception as e:
        logging.warning('❌ No se pudo acceder a la tabla de publicidades')
        logging.warning('   Exception occurred while code execution: ' + repr(e))
        os.system(ALERTA)
        publicidad_horizontal = []
    return publicidad_horizontal


def creacion_lista_noticias(numero_registros: int, noticias: list)-> list:
    """Crea la lista que lleva el diccionario que contiene cada noticia por separado

    Args:
        numero_registros (int): número por el que empieza la lista de noticias
        noticias (list): noticias

    Returns:
        list: La lista de axon[noticia]
    """
    logging.debug('Entra')
    axon = []
    longitud_de_noticia = 400
    for noticia in noticias:
        contenido_tratado = ''
        contenido_tratado = noticia['content']['rendered']
        contenido_tratado = strip_tags(contenido_tratado)
        contenido_tratado = re.sub('&nbsp;', ' ', contenido_tratado)
        contenido_tratado = re.sub('  ', ' ', contenido_tratado)
        contenido_tratado = contenido_tratado.strip(' ')
        contenido_tratado = contenido_tratado.replace(noticia['title']['rendered'], '', 1)
        contenido_tratado = contenido_tratado[0:longitud_de_noticia] + '... '
        axon.append( { 'id': numero_registros,
                        'url': noticia['link'],
                        'imagen': noticia['yoast_head_json']['og_image'][0]['url'],
                        'titulo': noticia['title']['rendered'],
                        'contenido': contenido_tratado} )
        numero_registros += 1
    return axon


def fusion_trabajos_y_banners(trabajos_compania: list, trabajos_produccion:list , publicidad_horizontal)->str:
    """Fusionamos los trabajos_compania y de trabajos_produccion y entre cada tabla horizontal colocamos un banner

    Args:
        trabajos_compania (list): _description_
        trabajos_produccion (list): _description_
        publicidad_horizontal (_type_): _description_

    Returns:
        str: el html de la parte de los trabajos
    """
    logging.debug('Entra')
    html_trabajos = ''
    # creamos las que van enfrentadas
    for enfrentadas in range(0, len(trabajos_compania)):
        html_trabajos = html_trabajos + bloques.bloque_exterior_funcion + creacion_banners(publicidad_horizontal) # type: ignore
        html_trabajos = html_trabajos.replace(
            '##bloque izq##', trabajos_compania[enfrentadas], 1)
        html_trabajos = html_trabajos.replace(
            '##bloque der##', trabajos_produccion[enfrentadas], 1)
    return html_trabajos


def gestion_noticias(axon: list)-> str:
    """Es funciçon se encarga de toda la gestión de ls noticias:
    desde si untroducción hasta el fianl, cuando sale como html con los banners

    Args:
        axon (list): Lista de las noticias

    Returns:
        str: El html de las noticias con los banners
    """
    # * Gestión de las noticias
    logging.debug('Entra')
    numero = 0
    print()
    noticias = input("¿Qué noticias quieres publicar? ")
    noticias = noticias.strip()
    noticias_colocadas = []
    try:
        noticias = noticias.split(' ')
        pase = 1
        for noticia in noticias:
            noticia = int(noticia)
            logging.info(f'Tratanto la noticia: {noticia}')
            if noticia == 0:
                # * Si es 0 es un bloque de pb cuadrado
                if pase % 2 != 0:
                    publicidad = bloques.publicidad.replace('##posicion##', 'left')
                    noticias_colocadas.append(publicidad)
                else:
                    publicidad = bloques.publicidad.replace('##posicion##', 'right')
                    noticias_colocadas.append(publicidad)
            else:
                # * Si no es pb, es una noticia
                criterio = lambda axon: axon["id"] == noticia
                noticia_filtrada = list(filter(criterio, axon))
                noticias_colocadas.append(
                    tabla_interior( 'comun',
                                    noticia_filtrada[0]['imagen'], noticia_filtrada[0]['titulo'],
                                    noticia_filtrada[0]['contenido'], noticia_filtrada[0]['url'],
                                    noticia_filtrada[0]['id']))
            pase += 1
    except Exception as e:
        logging.warning('❌ Esta sección no se va a publicar')
        logging.warning('   Exception occurred while code execution: ' + repr(e))
        os.system(ALERTA)
        noticias_colocadas = ''
    longitud = len(noticias_colocadas)
    print(f"Noticias generadas: {longitud}")
    # Creamos el último si es impar: noticia + banner cuadrado
    ultimo_si_es_impar = ''
    if longitud % 2 != 0:
        ultimo_si_es_impar = bloques.bloque_exterior
        ultimo_si_es_impar = ultimo_si_es_impar.replace(
            '##bloque izq##', noticias_colocadas[-1], 1)  # usamos el último
        ultimo_si_es_impar = ultimo_si_es_impar.replace('##bloque izq##', '', 1)
        ultimo_si_es_impar = ultimo_si_es_impar.replace('##posicion##', 'left')
        # Agregamos pb cuadrada
        ultimo_si_es_impar = ultimo_si_es_impar.replace('##bloque der##', banners.banner_laservet_vega_cuadrado)
        logging.warning('Eliminar el banner del laser Vega porque usamos el banner cuadrado')
        longitud -= 1
    #  Creamos el cuerpo sin las noticias: esqueleto de par de noticias y debajo un banner
    bloque_final_con_noticias = ''
    for numero in range(0, (int(longitud/2))):
        bloque_final_con_noticias = bloque_final_con_noticias + bloques.bloque_exterior
        bloque_final_con_noticias = bloque_final_con_noticias + creacion_banners(publicidad_horizontal) # type: ignore
    # Metemos las noticias menos la última
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
    # Unimos los dos bloques (la noticias por pares y la última)
    bloque_final_con_noticias = bloque_final_con_noticias + ultimo_si_es_impar
    return bloque_final_con_noticias


def pb_bioiberica(publicidad_horizontal: list)-> list:
    """Se gestiona la publicación de Bioiberica.

    Args:
        publicidad_horizontal (list): lista de banners horizontales

    Returns:
        list: lista de banners horizontales actualizada
    """
    logging.debug('Entra')
    semana = ahora.isocalendar()[1]
    paso_bioiberica = False
    for banner in publicidad_horizontal:
        # * Publicidad de ecuphar: distintos cada semana
        if banner[1] == 'Ecuphar: Daxocox' and semana % 2 == 0:
            publicidad_horizontal.remove(banner)
        if banner[1] == 'Ecuphar: Leisguard' and semana % 2 != 0:
            publicidad_horizontal.remove(banner)
        # * Publicidad de bioiberica: aleatorios
        if banner[1] == 'Bio Iberica' and paso_bioiberica == False: #ponemos el primer banner de la lista sqlite3
            seleccion = random.randint(0, 1)
            if seleccion == 1:
                publicidad_horizontal.remove(banner)
                paso_bioiberica = True
        if banner[1] == 'Bio Iberica: Atopivet Collar' and paso_bioiberica == False:
            publicidad_horizontal.remove(banner)
    return publicidad_horizontal


def pb_royal_canin(publicidad_horizontal: list)->list:
    """Se gestiona la publicación de Royal Canin. Esta publicac va por periodos.
    Funciona así: si toca se mete en una nueva variable,
    después eliminamos todos los banner de esa empresa en publicidad_horizontal y
    por último añadimos a publicidad_horizontal la nueva variable
    #todo: se puede hacer de una forma mas elegante?
    
    Args:
        publicidad_horizontal (list): lista de banners horizontales

    Returns:
        list: lista de banners horizontales actualizada
    """
    logging.debug('Entra')
    banner_Royal = ''
    paso_Royal = False
    # * hay que cambiar también el nombre de los banners de la tabla de publicidad del sqlite3
    banner_gato = 'Royal canin gato: del 1 al 14 de junio'
    banner_perro = 'Royal canin perro: del 15 al 30 de junio'
    for banner in publicidad_horizontal:
        # * recorremos todos los banner y si esta dentro de la fecha lo selccionamos
        # * y ha pasado de la fecha avisamos
        if ahora < datetime(2023, 6, 15, 0, 0, 0) and banner[1] == banner_gato: #?poner la fecha en el datetime
            #print(f'Hoy sale el {banner_gato}')
            paso_Royal = True
            banner_Royal = banner
        if ahora >= datetime(2023, 6, 15, 0, 0, 0) and banner[1] == banner_perro: #?poner la fecha en el datetime
            #print(f'Hoy sale el {banner_perro}')
            paso_Royal = True
            banner_Royal = banner
        if ahora > datetime(2023, 6, 30, 0, 0, 0) and banner[1] == banner_perro: #?poner la fecha en el datetime
            print()
            logging.warning('❌ Banner de royal Canin caducado')
            os.system(ALERTA)
    for banner in publicidad_horizontal:
        # * marcamos los dos bannes de royal canin para borrarlos despues
        if banner[1] == banner_perro:
            paso_Royal = True
            Royal_borrar_1 = banner
        if banner[1] == banner_gato:
            paso_Royal = True
            Royal_borrar_2 = banner
    if paso_Royal == True:
        # * borramos los dos banners de Royal canin y añadimos el seleccionado
        publicidad_horizontal.remove(Royal_borrar_1)
        publicidad_horizontal.remove(Royal_borrar_2)
        publicidad_horizontal.append(banner_Royal)
    return publicidad_horizontal


# * ****************
# * empezamos la app
# * ****************

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

    ahora = datetime.now()
    # ? Si queremos hacer el masivo de otro día descomentamos la línea inferior (aaaa/mm/dd):
    # ahora = datetime.strptime('2023/5/23', '%Y/%m/%d')

    # Variables usadas en mas de una función
    noticias_mostradas = 20
    imagen_local = ''
    ancho = 0
    alto = 0
    
    # Varibles usadas en la app
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
    ALERTA = "afplay alerta.mp3"


    # * Creamos y actualizamos la lista de banner a incluir
    publicidad_horizontal = gestion_publicidad()
    publicidad_horizontal = pb_bioiberica(publicidad_horizontal)
    publicidad_horizontal = pb_royal_canin(publicidad_horizontal)


    # * Empezamos con la app
    print()
    print()
    print(f'Fecha del masivo: {ahora.strftime("%A, %d de %B de %Y")}')
    print()
    print(f'Hoy salen publicados {str(len(publicidad_horizontal))} banners (sin contar con los extra):')
    for banner in publicidad_horizontal:
        print(f'  -{banner[1]}')
    print()
    boletin = int(input("¿Qué número del masivo vas a publicar? "))


    # * Creamos la carpeta
    nombre_archivo = str(boletin)+'c'
    try:
        os.mkdir(nombre_archivo)
    except OSError as e:
        print("Borrando carpeta anterior.")
        if e.errno != errno.EEXIST:
            raise

    print()
    print("0 = Dejar hueco relleno")
    print("Nº  | Título")
    print()

    # * Mostramos los trabajos
    trabajos_en_bbdd_compania,trabajos_en_bbdd_produccion = recuperar_trabajos() # type: ignore

    print('Trabajos de compañía:')
    print(f"----|-{'-'*110}")
    for trabajo in trabajos_en_bbdd_compania:
        print(f"{trabajo[0]:>3} | {trabajo[1][0:130]}")
    print()

    print('Trabajos de producción:')
    print(f"----|-{'-'*110}")
    for trabajo in trabajos_en_bbdd_produccion:
        print(f"{trabajo[0]:>3} | {trabajo[1][0:130]}")


    # * Recogemos las noticias de la web
    noticias = read_wordpress_posts()


    # * Creamos el diccionario axon[noticia]
    numero_registros = len(trabajos_en_bbdd_compania) + len(trabajos_en_bbdd_produccion) + 2 #! 1
    axon = creacion_lista_noticias(numero_registros, noticias)

    print()
    print(f"Últimas {noticias_mostradas} noticias:")
    print(f"----|-{'-'*104}")
    for noticia in axon:
        print(f"{noticia['id']:>3} | {noticia['titulo'][0:130]}")

    print()
    print()
    print()
    print('Los trabajos/noticias separadas con espacios.')
    print()
    noticias_destacadas = noticias_destacadas(axon) # type: ignore
    print()


    # * Trabajos de animales de compañia y producción, se crean las listas
    logging.debug('Trabajos de animales de compañia y producción')
    trabajos_compania = trabajos_a_publicar('compania')
    trabajos_compania = trabajos_a_mostrar('compania', trabajos_compania, axon)
    trabajos_produccion = trabajos_a_publicar('produccion')
    trabajos_produccion = trabajos_a_mostrar('produccion', trabajos_produccion, axon)

    # * Igualamos las dos listas
    if len(trabajos_compania) != len(trabajos_produccion): # type: ignore
        trabajos_compania, trabajos_produccion = igualar_listas(trabajos_compania, trabajos_produccion) # type: ignore

    html_trabajos = fusion_trabajos_y_banners(trabajos_compania, trabajos_produccion, publicidad_horizontal)


    bloque_final_con_noticias = gestion_noticias(axon)


    # * Gestionamos la cabecera
    comienzo_en_curso = bloques.comienzo
    comienzo_en_curso = comienzo_en_curso.replace('##nombre_archivo##', nombre_archivo)
    comienzo_en_curso = comienzo_en_curso.replace('##numero##', str(boletin))
    comienzo_en_curso = comienzo_en_curso.replace(
        '##mes##', meses[str(ahora.month)])
    # todo: añadir año

    # * Vamos uniendo las partes
    resultado = ''
    resultado = resultado + comienzo_en_curso + noticias_destacadas + html_trabajos # type: ignore

    # * Chequea si todos los banner estan publicados. Si no lo estan se publican y avisa
    if len(publicidad_horizontal) >= 1:
        print()
        print()
        logging.warning(
            '❌ Cuidado: los banners horizontales no se han colocado bien')
        os.system(ALERTA)
        print()
        print()
        for n in range(len(publicidad_horizontal)):
            resultado = resultado + creacion_banners(publicidad_horizontal)


    # * Vamos uniendo las partes
    resultado = resultado + bloque_final_con_noticias
    resultado = resultado + banners.setna
    resultado = resultado + bloques.fin


    # * Codificamos a html
    logging.debug('Codificamos a html')
    # ? para cuerpos de email charset=ISO-8859-1
    resultado = resultado.replace("á", "&aacute;")
    resultado = resultado.replace("é", "&eacute;")
    resultado = resultado.replace("í", "&iacute;")
    resultado = resultado.replace("ó", "&oacute;")
    resultado = resultado.replace("ú", "&uacute;")
    resultado = resultado.replace("Á", "&Aacute;")
    resultado = resultado.replace("É", "&Eacute;")
    resultado = resultado.replace("Í", "&Iacute;")
    resultado = resultado.replace("Ó", "&Oacute;")
    resultado = resultado.replace("Ú", "&Uacute;")
    resultado = resultado.replace("ñ", "&ntilde;")
    resultado = resultado.replace("Ñ", "&Ntilde;")
    resultado = resultado.replace("¡", "&iexcl;")
    resultado = resultado.replace("¿", "&iquest;")
    resultado = resultado.replace("Â", "")
    resultado = resultado.replace("â€œ", "&quot;")
    resultado = resultado.replace("â€", "&quot;")

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
    logging.debug('Creamos el archivo')
    archivo = str(boletin)+"c.html"
    with open(archivo, mode="w", encoding="utf-8") as fichero:
        print(resultado, file=fichero)

    # * Movemos el archivo y la carpeta de imágenes a la carpeta de destino y abrimos el archivo html
    os.replace(archivo, datos_de_acceso.ruta_local+archivo)
    os.replace(str(boletin)+'c', datos_de_acceso.ruta_local+str(boletin)+'c')
    comando = 'open ' + '"'+ datos_de_acceso.repositorio + '"'
    subprocess.run(comando, shell=True)
    comando = 'open ' + '"'+ datos_de_acceso.ruta_local + archivo + '"'
    subprocess.run(comando, shell=True)

    print()
    print('Archivo generado: 👍')
    print()
    logging.debug('Fin')
