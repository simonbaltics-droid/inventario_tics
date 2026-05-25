import bcrypt
from database import conectar

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

def verificar(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed)

def registrar(correo, password, oficina, rol="usuario"):
    conn = conectar()
    c = conn.cursor()

    hashed = hash_password(password)

    c.execute("""
    INSERT INTO usuarios (correo, password, rol, oficina)
    VALUES (?, ?, ?, ?)
    """, (correo, hashed, rol, oficina))

    conn.commit()

def login(correo, password):
    conn = conectar()
    c = conn.cursor()

    c.execute("SELECT * FROM usuarios WHERE correo=?", (correo,))
    user = c.fetchone()

    if user and verificar(password, user[2]):
        return user
    return None