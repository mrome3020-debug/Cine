from flask import Flask, render_template, request, redirect, session, url_for
import base64

from Salas import salas
from Horarios import horarios
from DB import obtener_peliculas_para_main, obtener_rango_fechas_emision, formatear_fecha_corta
from Validacion_admin import administradores
from Main_admin import register_admin_routes


app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui'

register_admin_routes(app)


def obtener_mime(nombre_archivo):
	extension = nombre_archivo.rsplit('.', 1)[1].lower() if nombre_archivo and '.' in nombre_archivo else ''
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
		mime = obtener_mime(portada_nombre or 'imagen.jpg')
		encoded = base64.b64encode(portada).decode('utf-8')
		return f"data:{mime};base64,{encoded}"
	if isinstance(portada, str):
		return portada
	return None


def formatear_duracion_corta(duracion):
	valor = str(duracion).strip()
	if not valor:
		return ''
	if ':' in valor:
		partes = valor.split(':')
		if len(partes) == 2 and partes[0].isdigit() and partes[1].isdigit():
			return f"{int(partes[0]):02d}:{int(partes[1]):02d} h"
	return f"{valor} h"


@app.route('/')
def main():
	peliculas_raw = obtener_peliculas_para_main(limit=40)
	peliculas = []
	for pelicula in peliculas_raw:
		fecha_inicio, fecha_fin, _ = obtener_rango_fechas_emision(pelicula['Fechas_emision'], pelicula['Fecha_estreno'])
		peliculas.append(
			{
				'nombre': pelicula['Nombre'],
				'generos': pelicula['Generos'],
				'duracion': formatear_duracion_corta(pelicula['Duracion']),
				'calificacion': pelicula['Calificacion'],
				'fecha_estreno': formatear_fecha_corta(fecha_inicio),
				'fecha_hasta': formatear_fecha_corta(fecha_fin) if fecha_fin and fecha_fin != fecha_inicio else '',
				'portada_src': construir_src_portada(pelicula['Portada'], pelicula['Portada_nombre']),
			}
		)

	return render_template(
		'Main.html',
		salas=salas,
		horarios=horarios,
		peliculas=peliculas,
	)


@app.route('/ingresar_admin')
def ingresar_admin():
	if not session.get('acceso_validacion_admin'):
		return redirect(url_for('main'))
	return render_template('Validacion_admin.html', error=None)


@app.route('/ingresar_admin_gateway')
def ingresar_admin_gateway():
	session['acceso_validacion_admin'] = True
	return redirect(url_for('ingresar_admin'))


@app.route('/validar_admin', methods=['POST'])
def validar_admin_web():
	if not session.get('acceso_validacion_admin'):
		return redirect(url_for('main'))

	usuario = request.form.get('usuario', '').strip()
	contrasena = request.form.get('contraseña', '').strip()

	if usuario in administradores and contrasena == administradores[usuario]['password']:
		session['usuario'] = administradores[usuario]['nombre']
		session.pop('acceso_validacion_admin', None)
		return redirect(url_for('admin'))

	return render_template('Validacion_admin.html', error='Usuario o contraseña incorrectos')


if __name__ == '__main__':
	app.run(debug=True, port=5000)
