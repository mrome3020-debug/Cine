from django.urls import path

import Main
import Main_admin


urlpatterns = [
    path('', Main.main_view, name='main'),
    path('reservar_entrada/', Main.reservar_entrada_web, name='reservar_entrada'),
    path('entradas_reservadas/', Main.entradas_reservadas_web, name='entradas_reservadas'),
    path('cancelar_reserva/', Main.cancelar_reserva_web, name='cancelar_reserva'),
    path('ingresar_admin/', Main.ingresar_admin, name='ingresar_admin'),
    path('validar_admin/', Main.validar_admin_web, name='validar_admin'),
    path('registrar_cliente/', Main.registrar_cliente_web, name='registrar_cliente'),
    path('admin/', Main_admin.admin, name='admin_panel'),
    path('portadas/', Main_admin.ver_portadas, name='ver_portadas'),
    path('add_pelicula/', Main_admin.add_pelicula, name='add_pelicula'),
    path('edit_pelicula/', Main_admin.edit_pelicula, name='edit_pelicula'),
    path('delete_pelicula/', Main_admin.delete_pelicula, name='delete_pelicula'),
    path('logout/', Main_admin.logout, name='logout'),
]
