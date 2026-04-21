import sqlite3


def obtener_conexion(row_factory=False):
    conn = sqlite3.connect('Peliculas.db')
    if row_factory:
        conn.row_factory = sqlite3.Row
    return conn


def obtener_peliculas_para_main(limit=10):
    conn = obtener_conexion(row_factory=True)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT Nombre, Generos, Duracion, Calificacion, Fecha_estreno, Portada, Portada_nombre
        FROM PELICULAS
        ORDER BY Fecha_estreno ASC
        LIMIT ?
        """,
        (limit,),
    )
    peliculas = cursor.fetchall()
    conn.close()
    return peliculas


def eliminar_portada_por_rowid(rowid):
    """Elimina portada y nombre de portada para una pelicula por rowid.
    Devuelve True si se pudo ejecutar la operación.
    """
    conn = obtener_conexion()
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(PELICULAS)")
    columnas = [col[1] for col in cursor.fetchall()]

    sets = []
    if 'Portada' in columnas:
        sets.append("Portada = NULL")
    if 'Portada_nombre' in columnas:
        sets.append("Portada_nombre = NULL")

    # Si no existen columnas de portada, no bloqueamos el flujo de edición.
    if not sets:
        conn.close()
        return True

    query = f"UPDATE PELICULAS SET {', '.join(sets)} WHERE rowid = ?"
    cursor.execute(query, (rowid,))
    conn.commit()
    conn.close()
    return True


def normalizar_portadas_nulas():
    """Convierte valores vacíos de portada en NULL para evitar falsos positivos de imagen."""
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(PELICULAS)")
    columnas = [col[1] for col in cursor.fetchall()]

    if 'Portada' in columnas:
        cursor.execute("UPDATE PELICULAS SET Portada = NULL WHERE Portada = ''")
    if 'Portada_nombre' in columnas:
        cursor.execute("UPDATE PELICULAS SET Portada_nombre = NULL WHERE Portada_nombre = ''")

    conn.commit()
    conn.close()


def normalizar_clasificacion_mpa():
    """Convierte clasificaciones numéricas antiguas al estándar MPA."""
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(PELICULAS)")
    columnas = [col[1] for col in cursor.fetchall()]

    if 'Clasificacion' not in columnas:
        conn.close()
        return

    cursor.execute("SELECT rowid, Clasificacion FROM PELICULAS")
    filas = cursor.fetchall()

    def mapear_a_mpa(valor):
        if valor in ('G', 'PG', 'PG-13', 'R', 'NC-17'):
            return valor
        try:
            numero = int(valor)
        except (TypeError, ValueError):
            return valor

        if numero <= 7:
            return 'G'
        if numero <= 12:
            return 'PG'
        if numero <= 15:
            return 'PG-13'
        if numero <= 17:
            return 'R'
        return 'NC-17'

    for rowid, clasificacion in filas:
        nueva = mapear_a_mpa(clasificacion)
        if nueva != clasificacion:
            cursor.execute("UPDATE PELICULAS SET Clasificacion = ? WHERE rowid = ?", (nueva, rowid))

    conn.commit()
    conn.close()


def normalizar_duracion_hhmm():
    """Convierte duración histórica en minutos al formato HH:MM."""
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(PELICULAS)")
    columnas = [col[1] for col in cursor.fetchall()]

    if 'Duracion' not in columnas:
        conn.close()
        return

    cursor.execute("SELECT rowid, Duracion FROM PELICULAS")
    filas = cursor.fetchall()

    for rowid, duracion in filas:
        if duracion is None:
            continue

        valor = str(duracion).strip()
        if ':' in valor:
            partes = valor.split(':')
            if len(partes) == 2 and partes[0].isdigit() and partes[1].isdigit() and 0 <= int(partes[1]) <= 59:
                cursor.execute("UPDATE PELICULAS SET Duracion = ? WHERE rowid = ?", (f"{int(partes[0]):02d}:{int(partes[1]):02d}", rowid))
                continue

        try:
            minutos_totales = int(float(valor))
        except ValueError:
            continue

        horas = minutos_totales // 60
        minutos = minutos_totales % 60
        cursor.execute("UPDATE PELICULAS SET Duracion = ? WHERE rowid = ?", (f"{horas:02d}:{minutos:02d}", rowid))

    conn.commit()
    conn.close()


def inicializar_db():
    conn = obtener_conexion()
    cursor = conn.cursor()

    # Verificar las tablas disponibles
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tablas = cursor.fetchall()
    print("Tablas en la base de datos:", tablas)

    if ('PELICULAS',) in tablas:
        # Obtener la estructura de la tabla
        cursor.execute("PRAGMA table_info(PELICULAS)")
        columnas = cursor.fetchall()
        nombres_columnas = [col[1] for col in columnas]

        # Añadir columna Fecha_estreno si no existe
        if 'Fecha_estreno' not in nombres_columnas:
            cursor.execute("ALTER TABLE PELICULAS ADD COLUMN Fecha_estreno TEXT")
            conn.commit()
            print("Columna 'Fecha_estreno' añadida a la tabla PELICULAS.")

        # Añadir columna Portada si no existe (guarda bytes de imagen)
        if 'Portada' not in nombres_columnas:
            cursor.execute("ALTER TABLE PELICULAS ADD COLUMN Portada BLOB")
            conn.commit()
            print("Columna 'Portada' añadida a la tabla PELICULAS.")

        # Añadir columna para guardar el nombre original del archivo de portada
        if 'Portada_nombre' not in nombres_columnas:
            cursor.execute("ALTER TABLE PELICULAS ADD COLUMN Portada_nombre TEXT")
            conn.commit()
            print("Columna 'Portada_nombre' añadida a la tabla PELICULAS.")

        # Ejecutar una consulta para seleccionar todos los registros de la tabla PELICULAS
        cursor.execute("SELECT * FROM PELICULAS")
        peliculas = cursor.fetchall()

        if peliculas:
            print("Datos de la tabla PELICULAS:")
            for pelicula in peliculas:
                print(pelicula)

            # Actualizar las fechas de estreno para las películas existentes
            fechas_estreno = {
                'El Último Viaje': '2026-03-15',
                'Sombras del Pasado': '2026-05-20',
                'Risas Inesperadas': '2026-07-10',
                'Guerra de Titanes': '2026-09-05',
                'Misterio en la Niebla': '2026-11-12',
                'Amor Eterno': '2026-02-28',
                'Exploradores del Abismo': '2026-04-18',
                'La Rebelión': '2026-06-22',
                'Código Secreto': '2026-08-30',
                'Sueños Perdidos': '2026-10-14',
            }

            for nombre, fecha in fechas_estreno.items():
                cursor.execute("UPDATE PELICULAS SET Fecha_estreno = ? WHERE Nombre = ?", (fecha, nombre))

            conn.commit()
            print("Fechas de estreno actualizadas.")

            # Mostrar los datos actualizados
            cursor.execute("SELECT * FROM PELICULAS")
            peliculas_actualizadas = cursor.fetchall()
            print("Datos actualizados de la tabla PELICULAS:")
            for pelicula in peliculas_actualizadas:
                print(pelicula)
        else:
            print("La tabla PELICULAS está vacía.")

            # 10 películas de 2026 con fecha de estreno
            peliculas_a_insertar = [
                ('El Último Viaje', 1, 'Ciencia Ficción', 'PG', '02:00', 'Una aventura épica en el espacio.', 8.5, '2026-03-15', None, None),
                ('Sombras del Pasado', 2, 'Drama', 'PG-13', '01:35', 'Una historia de redención y amor.', 7.8, '2026-05-20', None, None),
                ('Risas Inesperadas', 3, 'Comedia', 'G', '01:25', 'Una comedia ligera sobre malentendidos.', 6.9, '2026-07-10', None, None),
                ('Guerra de Titanes', 1, 'Acción', 'NC-17', '02:20', 'Batallas épicas entre dioses y humanos.', 9.0, '2026-09-05', None, None),
                ('Misterio en la Niebla', 4, 'Thriller', 'R', '01:50', 'Un detective resuelve un crimen en una ciudad brumosa.', 8.2, '2026-11-12', None, None),
                ('Amor Eterno', 2, 'Romance', 'PG', '01:40', 'Una historia de amor que trasciende el tiempo.', 7.5, '2026-02-28', None, None),
                ('Exploradores del Abismo', 1, 'Aventura', 'PG', '02:05', 'Una expedición al fondo del océano.', 8.7, '2026-04-18', None, None),
                ('La Rebelión', 3, 'Fantasía', 'PG-13', '02:10', 'Una joven lucha contra un régimen opresivo.', 8.0, '2026-06-22', None, None),
                ('Código Secreto', 4, 'Suspenso', 'R', '01:45', 'Espías en una misión de alto riesgo.', 7.9, '2026-08-30', None, None),
                ('Sueños Perdidos', 2, 'Drama', 'PG-13', '01:30', 'Reflexiones sobre la vida y las decisiones.', 8.1, '2026-10-14', None, None),
            ]

            cursor.executemany(
                "INSERT INTO PELICULAS (Nombre, Proveedor, Generos, Clasificacion, Duracion, Descripcion, Calificacion, Fecha_estreno, Portada, Portada_nombre) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                peliculas_a_insertar,
            )
            conn.commit()
            print("Se han insertado 10 películas en la tabla PELICULAS con fechas de estreno.")

            # Mostrar los datos después de la inserción
            cursor.execute("SELECT * FROM PELICULAS")
            peliculas = cursor.fetchall()
            print("Datos de la tabla PELICULAS:")
            for pelicula in peliculas:
                print(pelicula)
    else:
        print("La tabla PELICULAS no existe en la base de datos.")

    conn.close()
    normalizar_portadas_nulas()
    normalizar_clasificacion_mpa()
    normalizar_duracion_hhmm()


if __name__ == "__main__":
    inicializar_db()
