# Definiendo el Tiempo de cada Horario
class Horario:
    def __init__(self, nombre, inicio, fin):
        self.nombre = nombre
        self.inicio = inicio
        self.fin = fin
    
    def __str__(self):
        return f"{self.nombre} - {self.inicio} a {self.fin}"
    
    def __repr__(self):
        return f"Horario('{self.nombre}', '{self.inicio}', '{self.fin}')"


# Crear los tres horarios
horario_1 = Horario("Horario 1", "16:00", "18:00")
horario_2 = Horario("Horario 2", "18:30", "20:30")
horario_3 = Horario("Horario 3", "21:00", "23:00")

# Lista de horarios disponibles
horarios = [horario_1, horario_2, horario_3]
