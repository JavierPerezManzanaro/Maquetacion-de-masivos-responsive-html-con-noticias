
import os


RUTA = '/Users/javierpm/Documents/Documentos personales/Javier/Axon, teletrabajo/Sitio en axoncomunicacion.es/masivos/axon_news/'

nombre_archivo = '1387c copia.html'


archivo_con_ruta = os.path.join(RUTA, nombre_archivo)


print()
print()
print()

#* Abrimos el archivo
try:
    with open(archivo_con_ruta, 'r') as file:
        archivo = file.read()
    print(f'Archivo {nombre_archivo} abirto exitosamente')
except Exception as e:
    print(f'Error al acceder a {nombre_archivo}: {e}')


contenido_html = archivo.replace(
        '<img src="', '<img src="https://axoncomunicacion.net/masivos/axon_news/')


#* Cerramos el archivo
try:
    with open(archivo_con_ruta, 'w') as file:
        file.write(contenido_html)
    print(f'Archivo {nombre_archivo} guardado exitosamente')
except Exception as e:
    print(f'Error al guardar {nombre_archivo}: {e}')
