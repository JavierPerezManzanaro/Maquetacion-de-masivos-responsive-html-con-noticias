import sqlite3

def limpiar_espacios(db_path, tabla):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Reemplazar el espacio no rompible (U+00A0) por un espacio normal (U+0020)
    cursor.execute(f"""
        UPDATE {tabla} 
        SET titular = REPLACE(titular, CHAR(160), ' ')
    """)
    
    conn.commit()
    conn.close()
    print("Actualización completada.")

if __name__ == "__main__":
    db_path = input("Introduce la ruta de la base de datos: ")
    tabla = input("Introduce el nombre de la tabla: ")
    limpiar_espacios(db_path, tabla)
