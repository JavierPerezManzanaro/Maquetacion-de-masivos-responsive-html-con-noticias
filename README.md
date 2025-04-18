![Lenguaje Python](https://img.shields.io/badge/Lenguaje-Python-green)
![Versión de Python 3.10](https://img.shields.io/badge/Versión%20de%20Python-3.10-green)


---

# Maquetación de masivos *responsive* para campañas de e-mail
## Descripción
Este proyecto surge de la necesidad de automatizar la creación de masivos para campañas de e-mail *responsive* (se adapta a todas las pantallas) diarias.

La aplicación recopila trabajos (de una bbdd sqlite3), una serie de noticias de un blog de la empresa y los banners que tienen que salir publicados.

Al final del proceso se obtiene:
- un **archivo html**
- una **carpeta con las imágenes nuevas**.
- una campaña creada en Acumbamail con ese masivo

Esta aplicación esta pensada para funcionar bajo la estructura de archivos de mi empresa, por lo que para otros casos abra que realizar modificaciones.

Si se abre el archivo html nada mas generarlo vera que algunos vínculos fallan en su ordenador (y en local). Obviamente son imágenes comunes que no se copian en cada masivo, se enlazan a un repositorio general.


---
## Instrucciones de configuración
### datos_de_acceso.py
Tenemos que crear un archivo con ese nombre.
Dentro tenemos que definir estas variables:
- url_general = String del blog: 'https://dominio.net'
- imagen_en_blanco = tiene que ser una url (str) que apunte a una imagen en blanco. Suelo usar un gif de 1x1 px en transparente.
- ruta_local: carpeta local donde se almacenan los documentos.
- datos de acceso y gestión en Acumbamail.

---
## Instrucciones de instalación
- Clonar el repositorio en local.
- Recomiendo modifificar esta preferencia en VSC: terminal.integrated.scrollback para que nos muestre todos los registros de las bbdd que tiene que mostrar. Por defecto viene 1000 pero se peude ampliar: https://code.visualstudio.com/docs/terminal/basics
- Tener instalado Python 3.10.
- Módulos a importar:
    - Para 'Creador de masivos.py':
      - [cv2](https://pypi.org/project/opencv-python/) Tratamiento de las imágenes.
      - [imutils](https://github.com/PyImageSearch/imutils) Ayuda para el tratamiento de las imágenes.
      - [tkinter](https://docs.python.org/es/3/library/tkinter.html) para mostrar la ventana donde pegaremos el código html que contiene el trabajo que queremos añadir a la bbdd.
      - Para versión menores de la 5:
          - [python-wordpress-xmlrpc 2.3](https://pypi.org/project/python-wordpress-xmlrpc/) Puente entre Python y WordPress.
          - [requests 2.28.1](https://pypi.org/project/requests/)
    - Para 'Inserción de noticias en bbdd.py':
      - [gazpacho](https://pypi.org/project/gazpacho/) para hacer web scraping.
      - [tkinter](https://docs.python.org/es/3/library/tkinter.html) para mostrar la ventana donde pegaremos el código html que contiene el trabajo que queremos añadir a la bbdd.



---
## Instrucciones de uso
Las instrucciones puede variar según el flujo de trabajo de cada empresa. En mi caso es así:


### Creación del masivo
1. Ejecuto la aplicación principal: 'Creador de masivos.py':

    1.1. La aplicación nos pregunta por el día. Si no introducimos nada se entiende que es para el día de hoy. Si ponemos "+1", "1" o "mañana" a el día actual se le suma uno.

    1.2. La aplicación va a mostrar tres listas:

      - Trabajos de compañía (extraídos de la bbdd.sqlite3).
      - Trabajos de producción (extraídos de la bbdd.sqlite3).
      - Últimas noticias y/o trabajos de Axón comunicación (extraídos de la web basada en WordPress).

    1.3. La aplicación pregunta (**'¿Qué noticia es la destacada? '**) para colocar la primera noticia que va a salir. Esta sale publicada a dos columnas.

      - Si introducimos algo que no sea un número de una noticia la aplicación se salta este paso.

    1.4. **'¿Trabajos de animales de compañía para publicar? '** Introducimos uno a uno, separados por espacios (sin comas), cada uno de los trabajos.

      - Si introducimos solamente un 0 la aplicación se salta este paso.

      - Si introducimos un 0 junto con otros trabajos la aplicación dejara en esa posición un hueco para un banner vertical.

      - Si el número esta en la lista de noticias y/o trabajos de la web nos abrirá una ventana para introducir el cuerpo de esa noticia en la bbdd de forma automática.

      - Al final, en el archivo html, se verán todos los trabajos de animales de compañía en la columna de la izquierda.

    1.5. **'¿Trabajos de animales de producción para publicar?  '** Introducimos uno a uno, separados por espacios (sin comas), cada uno de los trabajos.

      - Si introducimos solamente un 0 la aplicación se salta este paso.

      - Si introducimos un 0 junto con otros trabajos la aplicación dejara en esa posición un hueco para un banner vertical.

      - Si el número esta en la lista de noticias y/o trabajos de la web nos abrirá una ventana para introducir el cuerpo de esa noticia en la bbdd de forma automática

      - Al final, en el archivo html, se verán todos los trabajos de animales de producción en la columna de la derecha.

    1.7. **'¿Qué noticias quieres publicar? '** Introducimos uno a uno, separados por espacios (sin comas), cada uno de los trabajos.

      - Si introducimos solamente un 0 la aplicación se salta este paso.

      - Si introducimos un 0 junto con otras noticias la aplicación dejara en esa posición un hueco para un banner vertical.

      - Al final, en el archivo html, se verán todas estas noticias a dos columnas.

2. La aplicación genera el archivo html con los trabajos, los banner, las noticias y el bloque final (hemerotecas).

3. Hay que editar este archivo con cualquier editor html (Dreamweaver, por ejemplo) para enfrentar las noticias (las filas y columnas son celdas de tablas) y colocar los banners en su sitio si fuera necesario.


---
## Manifiesto de los archivos del repositorio
- banners.py

  Archivo donde se guardan los banners. En versiones posteriores esto se integrara en la bbdd.

- bbdd.sqlite3

  Base de datos que contiene los trabajos y los banners publicados.

- bloques.py

  Archivo que contiene las variables que conforman las partes del documento html.

- datos_de_acceso.py

  Archivo donde se guardan las claves y otra información privada.

- 'Creador de masivos.py'

  Aplicación que genera el masivo *responsive* en html.

- Inserción de noticias en bbdd.py

  Aplicación encargada de añadir trabajos a la bbdd 'bbdd.sqlite3'.

  Como los trabajos ya se han aplicado en su inmensa mayoría esta aplicación me abre un cuadro de dialogo para que pueda pegar el código html que define la tabla que contiene el trabajo.

  Si el título se repite solo se queda grabado el último registro.

- README.md

  El archivo que estas leyendo.

- preferencias.json

  Preferencias de la aplicación. Por ahora sin uso.

- requirements.txt

  Módulos usados.


---
## Errores conocidos
- A la hora de añadir trabajos que están como noticias se abre: por una parte en el navegador con el trabajo; y por otra, -en una ventana de "Python Launcher"- una ventana de dialogo para introducir el cuerpo de la noticia. Pues bien, en esa ventana de dialogo (por lo menos sobre Mac con el sistema Sonoma (14.0) y superiores) no se activa siempre el botón de "Introducir datos". Parece que es un problema más de "Python Launcher" que de la aplicación. En cualquier caso con cambiar el tamaño de la ventana queda solucionado.
- [SOLUCIONADO]: Al acceder a las noticias publicadas en el blog los borradores generar un error. La solución temporal consiste en entrar en el blog como administrador y eliminar esas noticias. Después las podemos sacar de la papelera y dejarlas como borrador otra vez.


---
## Historial de versiones


### Características para añadir por orden
- Calcular el numero de noticias necesarias para el numero de banners del día. Si faltan noticias se deben meter banners cuadrados de forma automática. La formula es: (trabajos + noticias) / 2 = número optimo de banners
- ¿Y si no encuentra algún trabajo o noticia? Por ahora avisa, en próximas versiones se modificara.
- Unificar g o p de grandes o de producción en bbdd (mejor opción) y en aplicación. 
- Ordenar de forma natural (contando los acentos y otros caracteres) los trabajos.
- Actualizar el sistema de sonido para que sea compatible con el resto de sistemas.

### 7.2
- Cambio el criterio para completar el contenido de las noticias. Antes era por caracteres, ahora es por palabras.
- Bug solucionado: Ahora gestiona de forma correcta las noticias destacadas.
- Bug solucionado: Si el titular termina con " -" esto se borra.
- Bug solucionado: Se selecciona el asunto de forma correcta.
- En la función "limpieza_de_tituares" se añade el comando para sustituir caracteres no imprimibles por espacios.
- Se añade la carpeta "Utilidades Unicode" para poder ver y cambiar en la bbdd los caracteres Unicode.
- En la función "comprobar_si_estan_todos" ahora muestra los titulares no encontrados, si existen.
- Automatiza la pregunta de trabajos y de noticias: Si se han encontrado se rellena automaticamente.
- Unificación de nombre de algunas variables y funciones.

### 7.1
- Añadimos la busqueda en el Word de las noticias destacadas.
- Ponemos color en la terminal para facilitar el uso de la aplicación usando "colorama".
- Si las noticias son impares deja el segundo hueco para el banner de Peq Ani Rev. Ahora ademas borra ese banner horizontal.
- Mejoro el algoritmo de búsqueda de titulares del Word. Unifico el uso de « y » a " (comillas dobles).

### 7
- En esta versión se presentan muchas mejoras y novedades.
- Ahora busca en el escritorio el archivo de Word donde estan los titulares de las noticias y trabajos. Si no lo encuentra  pasa a modo manual. Esto esta adaptado al flujo de trabajo de mi empresa pero se puede cambiar. Esta comentada la opción de que se muestre un cuadro de dialogo para seleccionar el archivo de Word que contiene los titulares (pasa a manual si Cancelamos el cuadro de selección de archivo de Word). 
- Se mejora la función que crea la carpeta donde se almacenan las imágenes.
- Usar la Agenda del número anterior en vez de una variable.
- Borra las imagenes png
- La inclusión en la bbdd no se realiza bien cuando es un trabajo de Grandes animales. Solucionado.
- Se admite 0 como entrada en "¿Fecha de emisión? (nada o para otro día: aaaa/mm/dd ó +1): ". Equivale a la fecha actual.
- Se mejora el tratamiento de los errores.


### 6.3.6
- Refactorización: Función "descarga_imagen" -> ahora admite imágenes en formato webp que transforma a formato jpg.
- Refactorización: Modifico la parte del código que coloca el banner cuadrado si son impares. Antes se colocaba al final y ahora se coloca en segunda posición con un banner especifico que esta en la variable.
- Ahora se admite guiones '-' a la hora de meter la fecha.
- Correcciones menores.


### 6.3.5
- Unificamos el tipo de comillas (simple, dobles, de sargento, etc) que se muestran. Todas pasan a ser comillas dobles: ".
- Mejoras menores.
- Correcciones ortográficas.
- Correcciones y actualización de README.md

### 6.3.4
- Mejoramos el funcionamiento de la función "descarga_imagen". Se simplifica y se avisa de que hay una imagen webp para cambiarla manualmente.
- Pequeñas mejoras.

### 6.3.3
- Mejoras menores.
- Mejoramos como se exportan las noticias. Ahora las comillas de sargento se muestran como comillas simples, los dobles espacios y los espacios antes y después desaparecen.

### 6.3.2
- Si hay una noticia destacada da a elegir que asunto hay que usar.
- Importamos el módulo "html" para mejorar la codificación. Se usa en el asunto y en cuerpo.

### 6.3.1
- Añado otro criterio para la ordenación de los banner: 'interno destacado': ver nota de la versión 5.2
- Abrimos la página web del masivo (en local) para comprobar si es correcto.

### 6.3
- Cambio de año de forma automática.
- Añado otro criterio para la ordenación de los banner: 'cliente final': ver nota de la versión 5.2
- Correcciones de errores menores.


### 6.2
- Extraigo las funciones de la gestion de los banners a otro archivo.
- Correcciones de errores menores.

### 6.1
- Aplico formato Autopep8.
- Otras mejoras menores.
- Corrijo la función obtener_asunto().
- Correcciones de errores menores.

### 6
- Añadimos la API de Acumbamail (empresa con la que tenemos la gestión de los masivos) para la creación automática de cada campaña. Para impedir su lanzamiento se programa para finales de año. Esto abra que cambiarlo desde la web cuando queramos lanzar la campaña. Documentación oficial: https://acumbamail.com/apidoc/
- Renombro las variables globales que están definidas en "datos_de_acceso.py" (no esta subido al repositorio) a MAYÚSCULAS.
- Cambio la obtención del último trabajo añadido mediante un "SELECT MAX(id)" para optimizar la lista de trabajos y noticias.
- Creamos la función limpiar_input para limpiar y depurar las listas de noticias o trabajos.
- Otras mejoras menores.

### 5.5.2
- Cambio el orden a la hora de mostrar los datos en la terminal.
- Ya no es necesario introducir el nombre del archivo html. Ahora lee la carpeta que los contiene y saca el siguiente número.
- La fecha de salida: Refactorizo la parte de la fecha y creo una función.
- Otras mejoras menores.

### 5.5.1
- Añado la función de "+1", "1" o "mañana" a la hora de introducir la fecha de lanzamiento del masivo.

### 5.5
- Mejoro y unifico la gestión de los banners: Ahora los tres funcionan igual:
    De la bbdd pasan todos los modelos de cada empresa a la lista. En cada función (una por cada empresa) se selecciona un banner por alguno de los criterios (o bien al azar, o por fechas, etc) y se borran el resto de banner de esa empresa.
- Cambio la forma de modificar el día de creación. Antes era una variable, ahora pregunta. Si no se pone nada se entiende que el dia actual.
- Añado un archivo de preferencias en JSON para gestionar mejor los banners. Todavía sin uso.
- Otras mejoras menores.
- Correcciones de errores menores.

### 5.4.1
- Mejoramos la gestión de la publicidad.
- Se declaran las variables lo mas cerca de su uso.
- Eliminación de comentarios sobrantes.
- Correcciones de errores menores.

### 5.4
- Forzamos a mostrar, dentro de las noticias, los últimos trabajos publicados para poder usarlos. Hace dos peticiones mas al API de Wordpress que lleva su tiempo pero es menor que generad un trabajo de nuevo.
- Reescribimos comentarios.
- Eliminamos comentarios sobrantes.
- Correcciones de errores menores.

### 5.3.1
- Refactorizo la función que gestiona banners de dos empresas y los separo en dos funciones.
- Otras mejoras menores.
- Correcciones de errores menores.

### 5.3
- Cambio el módulo encargado del tratamiento de las imagenes. El módulo anterior, Pillow, no esta actualizados para el procesador M2 de Apple. Lo cambio por el módulo CV2.
- Refactorizo la función: descarga_imagen. Ahora trabajo con ancho fijo de 320px y quito el atributo de altura de la imagen en el archivo "bloques.py".
- Correcciones de errores menores.

### 5.2.1
- Al automatizar los nuevos trabajos se abre la URL en el navegador para copiar y pegar el texto del cuero del trabajo directamente.
- Correcciones de errores menores.

### 5.2
- Ordenar los banners por grupos según su importancia. Hay cuatro grupos:
  -"destacado": los destacados que van a salir arriba, estos salen por orden de aparición en la bbdd.
  -"cliente": estos se seleccionan al azar dentro del día que les toque.
  -"interno": estos se seleccionan al azar dentro del día que les toque.
  -"final": Los últimos. Van en orden
- Correcciones de errores menores.

### 5.1.1
- Correcciones de errores menores.

### 5.1
- Automatizar los nuevos trabajos para que se inserten en la bbdd sqlite3 de forma automática.
- Ya no es necesario usar "Inserción de noticias en bbdd.py"

### 5.01
- Si la lista de noticias son impares en el último hueco metemos banner cuadrado del láser.
- Mejoramos la documentación de las funciones.
- Modificar la ubicación de algunas variables según su ámbito.
- Correcciones de errores menores.

### 5
- Cambiamos el sistema de comunicación con el blog. A partir de esta versión se usa el API de WordPress
- Mucha parte de la app central pasa a ser funciones.
- Cambiamos la estructura de datos de las noticias: lista compuesta por diccionarios.
- Implementamos las búsquedas mediante *list* y *filter*.
- Refactorización de algunas funciones y procesos.
- Correcciones de errores menores.

### Cambios necesarios en python-wordpress-xmlrpc si se usan versiones anteriores a la 5
Este módulo no es compatible con la versión Python 3.10. Hay que realizar un pequeño cambio en el código.
En el archivo "wordpress_xmlrpc/base.py" hay que modificar dos lineas:
1: pasa a ser: **import collections.abc**
128: pasa a ser: **elif isinstance(raw_result, collections.abc.Iterable):**
Explicación:
[https://github.com/maxcutler/python-wordpress-xmlrpc/pull/148/files/69ba89706c47ac2c39fae41137bb2d38dee4ae5a](https://github.com/maxcutler/python-wordpress-xmlrpc/pull/148/files/69ba89706c47ac2c39fae41137bb2d38dee4ae5a)
[https://github.com/maxcutler/python-wordpress-xmlrpc/pull/148](https://github.com/maxcutler/python-wordpress-xmlrpc/pull/148)

### 4.6.3
- Correcciones de errores menores.

### 4.6.2
- Si, por equivocación, el usuario mete dos espacios para separar las noticias ya no da error.
- Añado requirements.txt
- Se mejora la documentación.
- Se unifica el sonido de ALERTA.
- El archivo HTML y la carpeta con las imágenes ahora son trasladados a la carpeta de trabajo. Esta ruta es datos_de_acceso.ruta_local
- Apertura automática (en mac) del archivo HTML.

### 4.6.1
- Añado un decorador para medir el tiempo de una función.
- Cambio la nomenclatura de las variables constantes.
- Cambio 're.sub' por 'str.replace' (python:S5361).

### 4.6
- Actualizo la aplicación a Python 3.10
- Creo un entorno de desarrollo.
- Cambio el sistema de sonido. Ahora uso "os.system("afplay " + sonido)" que funciona de forma nativa en nuestro sistema. En este caso solo en Mac. Ya se actualizara para otros sistemas.
- Amplio y mejoro la documentación.
- Correcciones de errores menores.

### 4.5.3
- Mejoras:
  - Las variable que son de paso (variables semáforo) ahora son booleanas.
- Correcciones de errores menores.

### 4.5.2
- Mejoras:
  - Refactorización de las funciones de entrada de trabajos.
- Correcciones de errores menores.

### 4.5.1
- Novedades:
  - Ahora es posible hacer el masivo de cualquier día.
- Mejoras:
  - Unifico logging.
  - Mejoro el algoritmo que gestiona los banners de publicidad.
- Cambios en los banners.

### 4.5
- Novedades:
  - Implemento el módulo **logging** para la depuración y control de errores de código.
- Mejoras:
  - Unifico nombre de las variables.
- Correcciones de errores menores.

### 4.4
- Novedades:
  - Uno, en una función, el imput de trabajos de compañía y producción para no repetir código. La nueva función se llama 'trabajos_a_mostrar' y se encarga de preguntar por los trabajo/noticias de cada una de las secciones: Animales de compañía o animales de producción.
  - Añado Type hints a las funciones.
  - Refactorización de la función tabla_interior con respecto al origen de las imágenes.
- Mejoras:
  - Amplio, unifico y mejoro la documentación de la app.
- Correcciones de errores menores.

### 4.3
- Novedades:
  - Ahora es posible introducir en el apartado de trabajos de animales de compañía y de producción una noticia. Se podría automatizar su inclusión en la bbdd pero no lo realizo porque siempre hay que modificar el texto.
  - Cambio de nombre el archivo principal. Ahora se llama: 'Creador de masivos.py'
- Aplico la función strip() a los inputs para evitar este tipo de errores debidos a los espacios en blanco.
- Correcciones de errores menores.

### 4.2.2
- Llevo a datos_de_acceso.py las urls de la empresa por temas de privacidad.

### 4.2.1
- Gestión de un tipo de trabajo de animales de producción que se repite semanalmente.
- Solución del error: la entrada no tiene imagen.
- Correcciones de errores menores.

### 4.2
- Añadimos sonido en alertas que requieren nuestra intervención.
- Correcciones de errores menores.

### 4.1
- Se gestiona los banners que rotan: por ejemplo una vez cada uno o cada semana.
- Cambio weekday por isoweekday al ser más humano :-)
- Correcciones de errores menores.

### 4
- Gestión de la publicidad. En esta versión solamente se trabajan los banners horizontales. Los verticales se ponen de forma manual. Ver punto 'Gestión de los banners'.
- Añado un try/except para evitar errores a la hora de tratar la noticia destacada.
- Añado un try/except para evitar errores a la hora de tratar las noticias.
- Correcciones de errores menores.
- Ampliación y correcciones en el README.md

### 3.2
- Fusión de trabajos compañía y de producción para mostrarlos en su ubicación final, enfrentados.
- Correcciones de errores menores.

### 3.1.2
- Mejoras en 'Inserción de noticias en bbdd.py':
  - Ahora se pueden incluir etiquetas html (cursivas o subindices, por ejemplo) en el título o en el texto.
- Correcciones en el README.md

### 3.1.1
- Añado un try/except para evitar errores a la hora de tratar trabajos.
- Correcciones en el README.md
- Adaptación al flujo de trabajo.
- Cambio el trabajo con la fecha apara poder meter banners algunos días en concreto.

### 3.1
- Corrección de errores generales.
- Incluimos una gestión básica de los 4 banners que van todos los días.
- Añadimos la gestión de trabajos.
- Sacamos a un archivo separado 'datos_de_acceso.py' las contraseñas.
- Se limpia bien el cuerpo de las noticias que se cuelgan en la web: dobles espacios, espacios en bruto, etc.
- Unificamos el uso del termino 'grandes' que pasa a ser de 'producción'.
- Unificamos el uso del termino de 'peq' que pasa a ser de 'compania'.
- Creamos la bbdd en sqlite3 con los trabajos.

### 3
- Corrección de errores generales.
- Codificación 8-utf.

### 2
- Varias modificaciones.

### 1
- Versión base.



---
## Gestión de los banners
Existen varios tipos de banners:

### Horizontales con repetición semanal
- Estos se gestionan de forma automática. Solamente es necesario introducirlos en la bbdd sqlite3, tabla Publicidad. En el campo del día de la semana abra que poner un '1' si queremos que salga ese día.
- Si estos banners son rotativos (según días o semanas, por ejemplo): se crean los dos modelos en la bbdd y después del SELECT que hace la selección de los banners es donde son borrados, según los criterios del <code>if</code>, el que no se use.

### Horizontales de forma aislada
- Estos salen unos días en concreto y son tratados de forma manual.
- El formato de la fecha es aaaa-mm-dd. Se realizara una lista con los días que queremos que sean publicados y al comparar con día actual se incluirán o no.
- Tenemos que crear el html del banner y pegarlo en el archivo 'banners.py'.
- Buscar en la aplicación: '#* Banners Horizontales de forma aislada.' para ver los casos.

### Verticales
- Actualmente son pocos y diarios y su gestión es manual.
- En próximas versiones se incluirán en la bbdd.


---
## Licencias y derechos de autor
CC (Creative Commons) de Reconocimiento – NoComercial – SinObraDerivada
![CC (Creative Commons) de Reconocimiento – NoComercial – SinObraDerivada](https://raw.githubusercontent.com/JavierPerezManzanaro/Maquetacion-de-masivos-responsive-html-con-noticias/main/Reconocimiento-no-comercial-sin-obra-derivada.png)


---
## Información de contacto del autor
Javier Pérez
javierperez@perasalvino.es


---
## Motivación
Después de finalizar mis estudios de DAM empece a buscar un proyecto donde poder desarrollar los conocimientos aprendidos.
Y que mejor que un proceso repetitivo y pesado que hay que hacer todos los días :-)


---
## Créditos y agradecimientos
- A toda la comunidad web que me ha permitido ir ampliando mi formación.
- A mi familia por su infinita paciencia.
