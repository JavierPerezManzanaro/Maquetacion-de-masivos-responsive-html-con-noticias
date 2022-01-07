
![Versión 3.1](https://img.shields.io/badge/Versión-3.1.1-green) 
![Lenguaje Python](https://img.shields.io/badge/Lenguaje-Python-green) 
![Versión de Python 3.8.5](https://img.shields.io/badge/Versión%20de%20Python-3.8.5-green) 
---

# Maquetación de masivos *resposive* para campañas de e-mail
## Descripción
Este proyecto surge de la necesidad de automatizar la creación de un masivo para campañas de e-mail *responsive* (se adapta a todas las pantallas) diario.

La aplicación recopila trabajos (de una bbdd sqlite3), una serie de noticias de un blog de la empresa y los banners que tienen que salir publicados.

Al final del proceso se obtiene:
- un **archivo html** 
- una **carpeta con las imágenes nuevas**.

Esta aplicación esta pensada para funcionar bajo la estructura de archivos de mi empresa, por lo que para otros casos abra que realizar modificaciones.

Si se abre el archivo nada mas generarlo se veran algunos vínculos que fallan en su ordenador (y en local). Obviamente son imágenes comunes que no se copian en cada masivo, se enlazan a un repositorio general.


---
## Instrucciones de configuración
### Datos_de_acceso.py
Tenemos que crear un archivo con ese nombre.

Dentro tenemos que definir dos variables: "usuario" y "contrasena" (sin ñ) que deben ser los datos de acceso al blog de WordPress.


---
## Instrucciones de instalación
- Clonar el repositorio en local
- Módulos a importar:
    - Para "Informavet.py":
      - [python-wordpress-xmlrpc 2.3](https://github.com/maxcutler/python-wordpress-xmlrpc) puente entre Python y WordPress.
    - Para "Inserción de noticias en bbdd.py":
      - [gazpacho](https://pypi.org/project/gazpacho/) para hacer web scraping.
      - [tkinter](https://docs.python.org/es/3/library/tkinter.html) para mostrar la vebtana donde pegaremos el código html que contiene el trabajo que queremos añadir a la bbdd. 


---
## Instrucciones de uso 
Las instrucciones puede variar según el flujo de trabajo de cada empresa. En mi caso es así:

### ¿Están los trabajos en la bbdd?
1. Buscar si están en la base de datos los trabajos que tienen que salir publicados en el masivo diario abriendo "bbdd.sqlite3".

    1.1. Si están los trabajos de compañía y de producción paso al punto 2 (en Creación del masivo).

    1.2. Si no están: En este punto hay varias formas de actuar. La mas eficiente para mi es crear esos trabajos como noticias (en el fondo siguen la misma extructura, solo cambia el color del titular), después cambio el color del titular y las coloco en su sitio (todo esto con Dreamwaver, por ejemplo). Mas tarde introduzco ese trabajo en la bbdd ejecutando "Inserción de noticias en bbdd.py".

### Creación del masivo 
2. Ejecuto la aplicación principal: "Informavet.py":

    2.1. La aplicación nos pregunta por el número del masivo. Hay que introducir un número. La aplicación creara la carpeta y el archivo html según ese número añadiendo una "c" al nombre: **"¿Qué número de InformaVet es? "**

    2.2. La aplicación va a mostrar tres listas:
    
      - Trabajos de compañía (extraídos de la bbdd.sqlite3).
      - Trabajos de producción (extraídos de la bbdd.sqlite3).
      - Últimas 20 noticias de Axón comunicación (extraídos de la web basada en WordPress).

    2.3. La aplicación pregunta (**"¿Qué noticia es la destacada? "**) para colocar la primera noticia que va a salir. Esta sale publicada a dos columnas.

      - Si introducimos un 0 la aplicación se salta este paso.

    2.4. **"¿Trabajos de animales de compañía para publicar? "** Introducimos uno a uno, separados por espacios (sin comas), cada uno de los trabajos.

      - Si introducimos un 0 la aplicación se salta este paso.

      - Al final, en el archivo html, se verán todos los trabajos de animales de compañía en la columna de la izquierda.

    2.5. **"¿Trabajos de animales de producción para publicar?  "** Introducimos uno a uno, separados por espacios (sin comas), cada uno de los trabajos.

      - Si introducimos un 0 la aplicación se salta este paso.

      - Al final, en el archivo html, se verán todos los trabajos de animales de producción en la columna de la derecha.

    2.5. **"¿Qué noticias quieres publicar? "** Introducimos uno a uno, separados por espacios (sin comas), cada uno de los trabajos.

      - Si introducimos solamente un 0 la aplicación se salta este paso.

      - Al final, en el archivo html, se verán todas estas noticias a dos columnas.

      - Si entre noticias ponemos un 0 la aplicación va a dejar ese hueco para un banner cuadrado o vertical.

3. La aplicación genera el archivo html con los trabajos, los banner en el centro, las noticias y el bloque final (hemerotecas).

4. Hay que editar este archivo con cualquier editor html (Dreamweaver, por ejemplo) para enfrentar las noticias (las filas y columnas son celdas de tablas) y colocar los banners en su sitio.


---
## Manifiesto de los archivos del repositorio
- banners.py

  Archivo donde se guardan los banners. En versiones posteriores esto se integrara en la bbdd.

- bbdd.sqlite3

  Base de datos que contiene los trabajos publicados y los banners publicitarios.

- bloques.py

  Archivo que contiene las variables que conforman las partes del documento html.

- datos_de_acceso.py

  Archivo donde se guardan las claves para entrar el blog basado en WordPress.

- Informavet.py

  Aplicación que genera el masivo *responsive* en html.

- Inserción de noticias en bbdd.py

  Aplicación encargada de añadir trabajos a la bbdd "bbdd.sqlite3".

  Como los trabajos ya se han aplicado en su inmensa mayoría esta aplicación me abre un cuadro de dialogo para que pueda pegar el código html que define la tabla que contiene el trabajo.

  Si el título se repite solo se queda grabado el último registro.


- README.md

  El archivo que estas leyendo.


---
## Historial de versiones

### Próxima
- Incluir la librería: Logging
- Gestionar un tipo de trabajo de animales de producción que se repite semanalmente.
- Si no introducimos nada en alguna de las tres preguntas saltamos a la siguiente pregunta dejando ese bloque vacio.

### 3.1.1
- Añado un try/except para evitar errores a la hora de tratar trabajos.
- Correcciones en el README.md
- Adaptación al flujo de trabajo.

### 3.1
- Corrección de errores generales.
- Incluimos una gestión básica de los 4 banners que van todos los días.
- Añadimos la gestión de trabajos.
- Sacamos a un archivo separado "datos_de_acceso.py" las contraseñas.
- Se limpia bien el cuerpo de las noticias que se cuelgan en la web: dobles espacios, espacios en bruto, etc.
- Unificamos el uso del termino "grandes" que pasa a ser de "producción".
- Unificamos el uso del termino de "peq" que pasa a ser de "compania".
- Creamos la bbdd en sqlite3 con los trabajos.

### 3
- Corrección de errores generales.
- Codificación 8-utf.

### 2
- Varias modificaciones.

### 1
- Versión base.


---
## Licencias y derechos de autor
CC (Creative Commons) de Reconocimiento – NoComercial – SinObraDerivada
![CC (Creative Commons) de Reconocimiento – NoComercial – SinObraDerivada](https://raw.githubusercontent.com/JavierPerezManzanaro/Creacion-de-masivos-responsive-html-con-noticias/main/Reconocimiento-no-comercial-sin-obra-derivada.png)

---
## Información de contacto del autor
Javier Pérez
javierperez@perasalvino.es


---
## Errores conocidos
- Al acceder a las noticias publicadas en el blog los borradores generar un error. La solución temporal consiste en entrar en el blog como administrador y eliminar esas noticias. Después las podemos sacar de la papelera y dejarlas como borrador otra vez.


---
## Motivación
Después de finalizar mis estudios de DAM empece a buscar un proyecto donde poder desarrollar los conocimientos aprendidos.
Y que mejor que un proceso repetitivo y pesado que hay que hacer todos los días :-)


---
## Créditos y agradecimientos
- A toda la comunidad web que me ha permitido ir ampliando mi formación.
- A mi familia por su infinita paciencia.
