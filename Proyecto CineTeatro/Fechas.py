from datetime import datetime, timedelta
import calendar

# Definiendo el calendario
class Fecha:
    def __init__(self):
        self.hoy = datetime.now()
        self.mes_actual = self.hoy.month
        self.año_actual = self.hoy.year
        self.dia_actual = self.hoy.day
    
    def obtener_calendario_mes(self, mes, año):
        """Retorna una matriz con el calendario del mes especificado"""
        cal = calendar.monthcalendar(año, mes)
        return cal
    
    def es_seleccionable(self, dia, mes, año):
        """Verifica si una fecha es seleccionable (no está en el pasado, y el día actual solo hasta las 23:00)"""
        fecha_a_verificar = datetime(año, mes, dia)
        fecha_actual = datetime(self.hoy.year, self.hoy.month, self.hoy.day)
        
        if fecha_a_verificar < fecha_actual:
            return False  # Pasado
        elif fecha_a_verificar > fecha_actual:
            return True   # Futuro
        else:
            # Es el día actual
            return self.hoy.hour < 23
    
    def obtener_nombre_mes(self, mes):
        """Retorna el nombre del mes"""
        meses = {
            1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
            5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
            9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
        }
        return meses.get(mes, "")
    
    def mostrar_calendario(self, mes, año):
        """Muestra el calendario del mes con días seleccionables y no seleccionables"""
        nombre_mes = self.obtener_nombre_mes(mes)
        print(f"\n{'='*50}")
        print(f"{nombre_mes.upper()} {año}")
        print(f"{'='*50}")
        print("Lu  Ma  Mi  Ju  Vi  Sa  Do")
        print("-" * 50)
        
        cal = self.obtener_calendario_mes(mes, año)
        
        for semana in cal:
            linea = ""
            for dia in semana:
                if dia == 0:
                    linea += "    "  # Espacio para días de otros meses
                else:
                    # Verificar si es seleccionable
                    if self.es_seleccionable(dia, mes, año):
                        linea += f"{dia:2d}* "  # Asterisco para seleccionable
                    else:
                        linea += f"({dia:2d})"  # Paréntesis para no seleccionable
                    linea += " "
            print(linea)
    
    def obtener_meses_disponibles(self):
        """Retorna los datos del mes actual y siguiente"""
        meses_disponibles = []
        
        # Mes actual
        meses_disponibles.append({
            'mes': self.mes_actual,
            'año': self.año_actual,
            'nombre': self.obtener_nombre_mes(self.mes_actual)
        })
        
        # Mes siguiente
        siguiente_mes = self.mes_actual + 1
        siguiente_año = self.año_actual
        if siguiente_mes > 12:
            siguiente_mes = 1
            siguiente_año += 1
        
        meses_disponibles.append({
            'mes': siguiente_mes,
            'año': siguiente_año,
            'nombre': self.obtener_nombre_mes(siguiente_mes)
        })
        
        return meses_disponibles
    
    def mostrar_calendario_completo(self):
        """Muestra el calendario del mes actual y siguiente"""
        print(f"\nCALENDARIO DISPONIBLE - Hoy: {self.hoy.strftime('%d/%m/%Y')}")
        
        meses = self.obtener_meses_disponibles()
        
        for mes_info in meses:
            self.mostrar_calendario(mes_info['mes'], mes_info['año'])
        
        print(f"\n{'='*50}")
        print("* = Día seleccionable")
        print("(  ) = Día no seleccionable (pasado)")
        print(f"{'='*50}\n")
    
    def obtener_fechas_seleccionables(self):
        """Retorna una lista de todas las fechas seleccionables"""
        fechas_seleccionables = []
        
        meses = self.obtener_meses_disponibles()
        
        for mes_info in meses:
            cal = self.obtener_calendario_mes(mes_info['mes'], mes_info['año'])
            for semana in cal:
                for dia in semana:
                    if dia != 0 and self.es_seleccionable(dia, mes_info['mes'], mes_info['año']):
                        fecha = datetime(mes_info['año'], mes_info['mes'], dia)
                        fechas_seleccionables.append(fecha)
        
        return fechas_seleccionables


# Crear instancia del calendario
calendario = Fecha()

# Mostrar el calendario completo
if __name__ == "__main__":
    calendario.mostrar_calendario_completo()
