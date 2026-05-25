import streamlit as st
from database import crear_tablas, conectar
from auth import login, registrar

crear_tablas()

import sqlite3
import bcrypt

conn = sqlite3.connect("inventario.db")
c = conn.cursor()

# Verificar si ya existe el admin
c.execute("SELECT * FROM usuarios WHERE correo = 'admin@tic.gov.co'")
admin = c.fetchone()

if not admin:
    password = bcrypt.hashpw("admin123".encode(), bcrypt.gensalt())

    c.execute("""
    INSERT INTO usuarios (correo, password, rol, oficina)
    VALUES (?, ?, ?, ?)
    """, ("admin@tic.gov.co", password, "admin", "TIC"))

    conn.commit()

conn.close()

st.title("📊 Inventario Activos TIC")

# Sesión
if "usuario" not in st.session_state:
    st.session_state["usuario"] = None

# ---------------- LOGIN ----------------
if st.session_state["usuario"] is None:

    st.subheader("🔐 Iniciar sesión")

    correo = st.text_input("Correo")
    password = st.text_input("Contraseña", type="password")

    if st.button("Ingresar"):
        user = login(correo, password)
        if user:
            st.session_state["usuario"] = user
            st.success("Bienvenido")
            st.rerun()
        else:
            st.error("Datos incorrectos")

# ---------------- PANEL ----------------
else:
    usuario = st.session_state["usuario"]
    rol = usuario[3]
    oficina = usuario[4]

    st.sidebar.success(f"Usuario: {usuario[1]} ({rol})")

    conn = conectar()
    c = conn.cursor()

    menu = ["Ver activos", "Crear activo"]

    # ✅ SOLO ADMIN VE ESTO
    if rol == "admin":
        menu.append("Administrar usuarios")
        menu.append("Ver matriz completa")
        menu.append("Editar matriz")
        menu.append("Editor tipo Excel")
        menu.append("Cerrar sesión")

    opcion = st.sidebar.selectbox("Menú", menu)

    # ---------------- CREAR ACTIVO ----------------
    if opcion == "Crear activo":
        st.subheader("Crear activo")

        nombre = st.text_input("Nombre")
        tipo = st.text_input("Tipo")
        proceso = st.text_input("Proceso")
        responsable = st.text_input("Responsable")
        ubicacion = st.text_input("Ubicación")

        conf = st.selectbox("Confidencialidad", ["Alta", "Media", "Baja"])
        inte = st.selectbox("Integridad", ["Alta", "Media", "Baja"])
        disp = st.selectbox("Disponibilidad", ["Alta", "Media", "Baja"])
        datos = st.selectbox("Datos personales", ["Sí", "No"])

        if st.button("Guardar"):
            c.execute("""
            INSERT INTO activos 
            (nombre, tipo, proceso, oficina, responsable, ubicacion, confidencialidad, integridad, disponibilidad, datos_personales)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (nombre, tipo, proceso, oficina, responsable, ubicacion, conf, inte, disp, datos))

            conn.commit()
            st.success("Guardado")

    # ---------------- VER ACTIVOS ----------------
    elif opcion == "Ver activos":
        st.subheader("Activos")

        if rol == "admin":
            c.execute("SELECT * FROM activos")
        else:
            c.execute("SELECT * FROM activos WHERE oficina=?", (oficina,))

        datos = c.fetchall()

        for a in datos:
            st.expander(a[1]).write(a)

    # ---------------- ADMIN USUARIOS ----------------
    elif opcion == "Administrar usuarios" and rol == "admin":
        st.subheader("👥 Crear usuarios")

        correo_n = st.text_input("Correo nuevo")
        password_n = st.text_input("Clave", type="password")
        oficina_n = st.text_input("Oficina")

        rol_n = st.selectbox("Rol", ["usuario", "admin"])

        if st.button("Crear usuario"):
            registrar(correo_n, password_n, oficina_n, rol_n)
            st.success("Usuario creado")

    # ---------------- CERRAR SESIÓN ----------------
    elif opcion == "Cerrar sesión":
        st.session_state["usuario"] = None
        st.rerun()

    # ---------------- VER MATRIZ COMPLETA ----------------
    elif opcion == "Ver matriz completa" and rol == "admin":
        st.subheader("📊 Matriz completa (Excel cargado)")

        import pandas as pd
        conn = conectar()

        df = pd.read_sql("SELECT * FROM activos_completo", conn)

        st.dataframe(df)

        st.info("Esta es la matriz original cargada desde Excel 2019")

    # ---------------- EDITAR MATRIZ ----------------
    elif opcion == "Editar matriz" and rol == "admin":
        st.subheader("✏️ Editar matriz de activos")

        import pandas as pd
        conn = conectar()

        df = pd.read_sql("SELECT * FROM activos_completo", conn)

        # Seleccionar registro
        id_sel = st.selectbox("Selecciona ID del registro", df["id"])

        fila = df[df["id"] == id_sel].iloc[0]

        st.write("### Editar información")
        # st.write(df.columns)
        # st.write(df.head())

        # CAMPOS EDITABLES (puedes ampliar luego)
        nombre = st.text_input("Nombre", str(fila.get("Nombre", "")))
        descripcion = st.text_area("Descripción", str(fila.get("Descripción", "")))
        oficina = st.text_input("Oficina", str(fila.get("Oficina", "")))

        conf = st.selectbox("Confidencialidad", ["Alta", "Media", "Baja"], index=1)
        inte = st.selectbox("Integridad", ["Alta", "Media", "Baja"], index=1)
        disp = st.selectbox("Disponibilidad", ["Alta", "Media", "Baja"], index=1)

        if st.button("Actualizar registro"):
            conn.execute("""
            UPDATE activos_completo
            SET Nombre = ?, Descripción = ?, Oficina = ?
            WHERE id = ?
            """, (nombre, descripcion, oficina, id_sel))

            conn.commit()
            st.success("✅ Registro actualizado")
    # ---------------- EDITOR TIPO EXCEL ----------------
    elif opcion == "Editor tipo Excel":

        st.subheader("📊 Editor de matriz tipo Excel")

        import pandas as pd
        conn = conectar()

        df = pd.read_sql("SELECT * FROM activos_completo", conn)

        # Limpieza
        df = df.fillna("")
        df = df.astype(str)

        # 👉 Guardar en session_state
        if "df_editado" not in st.session_state:
            st.session_state["df_editado"] = df

        df_editado = st.data_editor(
            st.session_state["df_editado"],
            disabled=["id"],
            use_container_width=True,
            num_rows="dynamic"
        )

        # ✅ ACTUALIZAR EN MEMORIA
        st.session_state["df_editado"] = df_editado

        if st.button("💾 Guardar cambios"):

            try:
                conn = conectar()  # nueva conexión limpia

                df_editado.to_sql(
                    "activos_completo",
                    conn,
                    if_exists="replace",
                    index=False
                )

                conn.commit()
                conn.close()

                st.success("✅ Cambios guardados correctamente")
                st.rerun()
            except Exception as e:
                st.error(f"Error al guardar: {e}")