from flask import render_template, request, redirect, url_for, session
import sqlite3
import base64
from werkzeug.utils import secure_filename
from werkzeug.datastructures import MultiDict
from django_forms import PeliculaCreateForm, PeliculaEditForm
from DB import eliminar_portada_por_rowid

def obtener_mime(nombre_archivo):
    extension = nombre_archivo.rsplit('.', 1)[1].lower() if '.' in nombre_archivo else ''
    if extension in ('jpg', 'jpeg'):
        return 'image/jpeg'
    if extension == 'png':
        return 'image/png'
    if extension == 'gif':
        return 'image/gif'
    if extension == 'webp':
        return 'image/webp'
    return 'application/octet-stream'


def construir_src_portada(portada, portada_nombre):
    if portada is None:
        return None
    if isinstance(portada, bytes):
        nombre = portada_nombre or 'imagen.jpg'
        mime = obtener_mime(nombre)
        encoded = base64.b64encode(portada).decode('utf-8')
        return f"data:{mime};base64,{encoded}"
    if isinstance(portada, str):
        return portada
    return None


def formatear_errores_formulario(form):
    errores = []
    for campo, errores_campo in form.errors.items():
        for err in errores_campo:
            errores.append(f"{campo}: {err}")
    return '; '.join(errores)


def limpiar_archivos_vacios(files):
    """Elimina entradas de archivos vacíos para compatibilidad con Django FileField."""
    limpios = MultiDict()
    for key, value in files.items(multi=True):
        if value and getattr(value, 'filename', '').strip():
            limpios.add(key, value)
    return limpios

def get_db_connection():
    conn = sqlite3.connect('Peliculas.db')
    conn.row_factory = sqlite3.Row
    return conn


def _requiere_admin_activo():
    return 'usuario' in session


def register_admin_routes(app):
    @app.route('/admin')
    def admin():
        if not _requiere_admin_activo():
            return redirect(url_for('ingresar_admin'))
        conn = get_db_connection()
        peliculas = conn.execute('SELECT rowid, * FROM PELICULAS').fetchall()
        conn.close()
        return render_template('admin_peliculas.html', peliculas=peliculas, usuario=session['usuario'])

    @app.route('/portadas')
    def ver_portadas():
        if not _requiere_admin_activo():
            return redirect(url_for('ingresar_admin'))

        conn = get_db_connection()
        filas = conn.execute('SELECT rowid, Nombre, Portada, Portada_nombre FROM PELICULAS').fetchall()
        conn.close()

        portadas = []
        for fila in filas:
            src = construir_src_portada(fila['Portada'], fila['Portada_nombre'])
            if src:
                portadas.append({'id': fila['rowid'], 'nombre': fila['Nombre'], 'src': src})

        return render_template('Portadas.html', portadas=portadas, usuario=session['usuario'])

    @app.route('/add_pelicula', methods=['POST'])
    def add_pelicula():
        if not _requiere_admin_activo():
            return redirect(url_for('ingresar_admin'))

        form = PeliculaCreateForm(request.form, limpiar_archivos_vacios(request.files))
        if not form.is_valid():
            return f'Datos inválidos ({formatear_errores_formulario(form)})', 400

        datos = form.cleaned_data
        nombre = datos['nombre']
        proveedor = datos['proveedor']
        generos = datos['generos']
        clasificacion = datos['clasificacion']
        duracion = datos['duracion']
        descripcion = datos['descripcion']
        calificacion = datos['calificacion']
        fecha_estreno = datos['fecha_estreno'].strftime('%Y-%m-%d')
        portada_archivo = datos.get('portada')
        portada_bytes = None
        portada_nombre = None

        if portada_archivo:
            nombre_seguro = secure_filename(portada_archivo.name)
            portada_bytes = portada_archivo.read()
            portada_nombre = nombre_seguro

        conn = get_db_connection()
        conn.execute('INSERT INTO PELICULAS (Nombre, Proveedor, Generos, Clasificacion, Duracion, Descripcion, Calificacion, Fecha_estreno, Portada, Portada_nombre) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                     (nombre, proveedor, generos, clasificacion, duracion, descripcion, calificacion, fecha_estreno, portada_bytes, portada_nombre))
        conn.commit()
        conn.close()
        return redirect(url_for('admin'))

    @app.route('/edit_pelicula', methods=['POST'])
    def edit_pelicula():
        if not _requiere_admin_activo():
            return redirect(url_for('ingresar_admin'))

        form = PeliculaEditForm(request.form, limpiar_archivos_vacios(request.files))
        if not form.is_valid():
            return f'Datos inválidos ({formatear_errores_formulario(form)})', 400

        datos = form.cleaned_data
        id = datos['id']
        nombre = datos['nombre']
        proveedor = datos['proveedor']
        generos = datos['generos']
        clasificacion = datos['clasificacion']
        duracion = datos['duracion']
        descripcion = datos['descripcion']
        calificacion = datos['calificacion']
        fecha_estreno = datos['fecha_estreno'].strftime('%Y-%m-%d')
        portada_archivo = datos.get('portada')
        eliminar_portada = bool(datos.get('eliminar_portada'))
        portada_bytes = None
        portada_nombre = None

        if portada_archivo:
            nombre_seguro = secure_filename(portada_archivo.name)
            portada_bytes = portada_archivo.read()
            portada_nombre = nombre_seguro

        conn = get_db_connection()
        if eliminar_portada:
            conn.execute('UPDATE PELICULAS SET Nombre=?, Proveedor=?, Generos=?, Clasificacion=?, Duracion=?, Descripcion=?, Calificacion=?, Fecha_estreno=? WHERE rowid=?',
                         (nombre, proveedor, generos, clasificacion, duracion, descripcion, calificacion, fecha_estreno, id))
            conn.commit()
            conn.close()

            eliminar_portada_por_rowid(id)
            return redirect(url_for('admin'))
        elif portada_bytes is not None:
            conn.execute('UPDATE PELICULAS SET Nombre=?, Proveedor=?, Generos=?, Clasificacion=?, Duracion=?, Descripcion=?, Calificacion=?, Fecha_estreno=?, Portada=?, Portada_nombre=? WHERE rowid=?',
                         (nombre, proveedor, generos, clasificacion, duracion, descripcion, calificacion, fecha_estreno, portada_bytes, portada_nombre, id))
        else:
            conn.execute('UPDATE PELICULAS SET Nombre=?, Proveedor=?, Generos=?, Clasificacion=?, Duracion=?, Descripcion=?, Calificacion=?, Fecha_estreno=?, Portada=CASE WHEN Portada = "" THEN NULL ELSE Portada END WHERE rowid=?',
                         (nombre, proveedor, generos, clasificacion, duracion, descripcion, calificacion, fecha_estreno, id))
        conn.commit()
        conn.close()
        return redirect(url_for('admin'))

    @app.route('/delete_pelicula', methods=['POST'])
    def delete_pelicula():
        if not _requiere_admin_activo():
            return redirect(url_for('ingresar_admin'))

        id = int(request.form['id'])
        conn = get_db_connection()
        conn.execute('DELETE FROM PELICULAS WHERE rowid=?', (id,))
        conn.commit()
        conn.close()
        return redirect(url_for('admin'))

    @app.route('/logout')
    def logout():
        session.pop('usuario', None)
        return redirect(url_for('main'))
