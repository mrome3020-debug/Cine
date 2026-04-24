#Definiendo la clase "Salas" y sus asientos
class Sala:
    def __init__(self, nombre, asientos):
        self.nombre = nombre
        self.asientos = asientos
    
    def __str__(self):
        return f"{self.nombre} - {self.asientos} asientos"
    
    def __repr__(self):
        return f"Sala('{self.nombre}', {self.asientos})"


# Creando las dos salas
sala_principal = Sala("Sala Principal", 300)
mini_cine = Sala("Mini Cine", 90)

# Listado de salas disponibles
salas = [sala_principal, mini_cine]
