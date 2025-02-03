# texto = "Investigación de la proteína de unión a colina de CbpD en la patogénesis de Streptococcus suis tipo 2 "

# for caracter in texto:
#     print(f"'{caracter}': U+{ord(caracter):04X}")


import unicodedata

# Lista de caracteres de espacio Unicode problemáticos
espacios_raros = [
    "\u00A0", "\u2000", "\u2001", "\u2002", "\u2003", "\u2004", "\u2005",
    "\u2006", "\u2007", "\u2008", "\u2009", "\u200A", "\u202F", "\u205F"
]

def limpiar_espacios(texto):
    """Reemplaza todos los espacios Unicode raros por un espacio normal"""
    for espacio in espacios_raros:
        texto = texto.replace(espacio, " ")
    return texto

# Ejemplo de texto con espacios raros
texto_word = "Investigación de la proteína de unión a colina de CbpD en la patogénesis de Streptococcus suis tipo 2 "

print("Texto original:")
print(texto_word)

# Limpiar el texto
texto_limpio = limpiar_espacios(texto_word)

print("\nTexto limpio:")
print(texto_limpio)
