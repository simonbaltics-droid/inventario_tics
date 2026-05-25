import bcrypt
import sqlite3

conn = sqlite3.connect("inventario.db")
c = conn.cursor()

password = "admin123".encode()
hashed = bcrypt.hashpw(password, bcrypt.gensalt())

c.execute("""
INSERT INTO usuarios (correo, password, rol, oficina)
VALUES (?, ?, ?, ?)
""", ("admin@tic.gov.co", hashed, "admin", "TIC"))

conn.commit()

print("✅ Admin creado correctamente")