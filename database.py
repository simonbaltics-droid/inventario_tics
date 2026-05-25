import sqlite3

def conectar():
    return sqlite3.connect("inventario.db", check_same_thread=False)

def crear_tablas():
    conn = conectar()
    c = conn.cursor()

    c.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        correo TEXT,
        password TEXT,
        rol TEXT,
        oficina TEXT
    )
    ''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS activos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        tipo TEXT,
        proceso TEXT,
        oficina TEXT,
        responsable TEXT,
        ubicacion TEXT,
        confidencialidad TEXT,
        integridad TEXT,
        disponibilidad TEXT,
        datos_personales TEXT
    )
    ''')

    conn.commit()