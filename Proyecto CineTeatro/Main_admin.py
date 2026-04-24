import base64

from django.http import HttpResponseBadRequest
from django.shortcuts import redirect, render
from django.utils.datastructures import MultiValueDict
from django.utils.text import get_valid_filename

from DB import (
    eliminar_portada_por_rowid,
    ensure_fechas_emision_schema,
    formatear_fecha_corta,
    obtener_conexion,
    obtener_rango_fechas_emision,
    serializar_fechas_emision,
)
from django_forms import PeliculaCreateForm, PeliculaEditForm


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
    """Elimina entradas de archivos vacios para compatibilidad con Django FileField."""
    limpios = MultiValueDict()
    for key, values in files.lists():
        for value in values:
            if value and getattr(value, 'name', '').strip():
                limpios.appendlist(key, value)
    return limpios


def get_db_connection():
    return obtener_conexion(row_factory=True)


def _requiere_admin_activo(request):
    return request.session.get('rol') == 'admin'


def _normalizar_pelicula(fila):
    data = dict(fila)
    data['fechas_emision_resumen'] = data.get('Fechas_emision') or data.get('Fecha_estreno') or ''
    data['portada_src'] = construir_src_portada(data.get('Portada'), data.get('Portada_nombre'))
    return data


def admin(request):
    if not _requiere_admin_activo(request):
        return redirect('ingresar_admin')

    ensure_fechas_emision_schema()
    conn = get_db_connection()
    peliculas = conn.execute('SELECT rowid, * FROM PELICULAS').fetchall()
    conn.close()

    peliculas_contexto = [_normalizar_pelicula(pelicula) for pelicula in peliculas]
    return render(
        request,
        'admin_peliculas.html',
        {
            'peliculas': peliculas_contexto,
            'usuario': request.session['usuario'],
        },
    )


def ver_portadas(request):
    if not _requiere_admin_activo(request):
        return redirect('ingresar_admin')

    ensure_fechas_emision_schema()
    conn = get_db_connection()
    filas = conn.execute(
        'SELECT rowid, Nombre, Portada, Portada_nombre, Fecha_estreno, Fechas_emision FROM PELICULAS'
    ).fetchall()
    conn.close()

    portadas = []
    for fila in filas:
        src = construir_src_portada(fila['Portada'], fila['Portada_nombre'])
        if src:
            estreno, hasta, _ = obtener_rango_fechas_emision(fila['Fechas_emision'], fila['Fecha_estreno'])
            portadas.append(
                {
                    'id': fila['rowid'],
                    'nombre': fila['Nombre'],
                    'src': src,
                    'estreno': formatear_fecha_corta(estreno),
                    'hasta': formatear_fecha_corta(hasta) if hasta and hasta != estreno else '',
                }
            )

    return render(
        request,
        'Portadas.html',
        {
            'portadas': portadas,
            'usuario': request.session['usuario'],
        },
    )


def add_pelicula(request):
    if not _requiere_admin_activo(request):
        return redirect('ingresar_admin')
    if request.method != 'POST':
        return redirect('admin_panel')

    form = PeliculaCreateForm(request.POST, limpiar_archivos_vacios(request.FILES))
    if not form.is_valid():
        return HttpResponseBadRequest(f"Datos invalidos ({formatear_errores_formulario(form)})")

    datos = form.cleaned_data
    fechas_emision = datos['fechas_emision']
    fecha_estreno = fechas_emision[0]
    fechas_emision_texto = serializar_fechas_emision(fechas_emision)
    portada_archivo = datos.get('portada')
    portada_bytes = None
    portada_nombre = None

    if portada_archivo:
        portada_nombre = get_valid_filename(portada_archivo.name)
        portada_bytes = portada_archivo.read()

    ensure_fechas_emision_schema()
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO PELICULAS (Nombre, Proveedor, Generos, Clasificacion, Duracion, Descripcion, Calificacion, Fecha_estreno, Fechas_emision, Portada, Portada_nombre) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
        (
            datos['nombre'],
            datos['proveedor'],
            datos['generos'],
            datos['clasificacion'],
            datos['duracion'],
            datos['descripcion'],
            datos['calificacion'],
            fecha_estreno,
            fechas_emision_texto,
            portada_bytes,
            portada_nombre,
        ),
    )
    conn.commit()
    conn.close()
    return redirect('admin_panel')


def edit_pelicula(request):
    if not _requiere_admin_activo(request):
        return redirect('ingresar_admin')
    if request.method != 'POST':
        return redirect('admin_panel')

    form = PeliculaEditForm(request.POST, limpiar_archivos_vacios(request.FILES))
    if not form.is_valid():
        return HttpResponseBadRequest(f"Datos invalidos ({formatear_errores_formulario(form)})")

    datos = form.cleaned_data
    pelicula_id = datos['id']
    fechas_emision = datos['fechas_emision']
    fecha_estreno = fechas_emision[0]
    fechas_emision_texto = serializar_fechas_emision(fechas_emision)
    portada_archivo = datos.get('portada')
    eliminar_portada = bool(datos.get('eliminar_portada'))
    portada_bytes = None
    portada_nombre = None

    if portada_archivo:
        portada_nombre = get_valid_filename(portada_archivo.name)
        portada_bytes = portada_archivo.read()

    ensure_fechas_emision_schema()
    conn = get_db_connection()
    if eliminar_portada:
        conn.execute(
            'UPDATE PELICULAS SET Nombre=?, Proveedor=?, Generos=?, Clasificacion=?, Duracion=?, Descripcion=?, Calificacion=?, Fecha_estreno=?, Fechas_emision=? WHERE rowid=?',
            (
                datos['nombre'],
                datos['proveedor'],
                datos['generos'],
                datos['clasificacion'],
                datos['duracion'],
                datos['descripcion'],
                datos['calificacion'],
                fecha_estreno,
                fechas_emision_texto,
                pelicula_id,
            ),
        )
        conn.commit()
        conn.close()

        eliminar_portada_por_rowid(pelicula_id)
        return redirect('admin_panel')

    if portada_bytes is not None:
        conn.execute(
            'UPDATE PELICULAS SET Nombre=?, Proveedor=?, Generos=?, Clasificacion=?, Duracion=?, Descripcion=?, Calificacion=?, Fecha_estreno=?, Fechas_emision=?, Portada=?, Portada_nombre=? WHERE rowid=?',
            (
                datos['nombre'],
                datos['proveedor'],
                datos['generos'],
                datos['clasificacion'],
                datos['duracion'],
                datos['descripcion'],
                datos['calificacion'],
                fecha_estreno,
                fechas_emision_texto,
                portada_bytes,
                portada_nombre,
                pelicula_id,
            ),
        )
    else:
        conn.execute(
            'UPDATE PELICULAS SET Nombre=?, Proveedor=?, Generos=?, Clasificacion=?, Duracion=?, Descripcion=?, Calificacion=?, Fecha_estreno=?, Fechas_emision=?, Portada=CASE WHEN Portada = "" THEN NULL ELSE Portada END WHERE rowid=?',
            (
                datos['nombre'],
                datos['proveedor'],
                datos['generos'],
                datos['clasificacion'],
                datos['duracion'],
                datos['descripcion'],
                datos['calificacion'],
                fecha_estreno,
                fechas_emision_texto,
                pelicula_id,
            ),
        )
    conn.commit()
    conn.close()
    return redirect('admin_panel')


def delete_pelicula(request):
    if not _requiere_admin_activo(request):
        return redirect('ingresar_admin')
    if request.method != 'POST':
        return redirect('admin_panel')

    pelicula_id = int(request.POST['id'])
    conn = get_db_connection()
    conn.execute('DELETE FROM PELICULAS WHERE rowid=?', (pelicula_id,))
    conn.commit()
    conn.close()
    return redirect('admin_panel')


def logout(request):
    request.session.pop('usuario', None)
    request.session.pop('rol', None)
    request.session.pop('cliente_gmail', None)
    return redirect('main')
