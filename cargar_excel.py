import pandas as pd
import sqlite3

df = pd.read_excel("MATRIZ_RIESGOS_TICS.xlsx")

# Limpiar filas vacías
df = df.dropna(how="all")

# ✅ Crear ID SIEMPRE
df = df.reset_index(drop=True)
df["id"] = df.index + 1

# ✅ Mover ID al inicio
cols = ["id"] + [col for col in df.columns if col != "id"]
df = df[cols]

# ✅ Limpiar nombres de columnas (MUY IMPORTANTE)
df.columns = df.columns.str.strip()
df.columns = df.columns.str.replace(" ", "_")
df.columns = df.columns.str.lower()

conn = sqlite3.connect("inventario.db")

df.to_sql("activos_completo", conn, if_exists="replace", index=False)

conn.close()

print("✅ Excel cargado correctamente con ID")