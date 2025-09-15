def inspect_unicode(text):
    print("Carácter | Código Unicode | Descripción")
    print("-" * 40)
    for char in text:
        print(f"{char!r} | U+{ord(char):04X} | {unicodedata.name(char, 'DESCONOCIDO')}")

if __name__ == "__main__":
    import unicodedata
    texto = input("Introduce una cadena de texto: ")
    inspect_unicode(texto)
    
    
"""
Pegar las cadenas para ver si hay o no:

de Codonopsis Pilosulae y Astragalus Membranaceus en el    
    La patogenicidad de Salmonella isla-14 es un factor crítico de virulencia responsable de la infección sistémica en pollos
    Una dosis viva atenuada de la vacuna contra Salmonella Typhimurium
    """