from getpass import getpass


# Diccionario de administradores con sus credenciales
administradores = {
    "Grupo2": {
        "password": "1234",
        "nombre": "Grupo 2"
    }
}


def validar_administrador():
    """
    Función de validación en dos pasos para administradores.
    Pide usuario y contraseña, manteniendo el usuario correcto si la contraseña falla.
    """
    usuario = None
    
# Pedir usuario si no está establecido o fue incorrecto    
    while True:
        if usuario is None:
            usuario = input("Usuario: ").strip()
        
# Verificar si el usuario existe
        if usuario not in administradores:
            print("Usuario incorrecto. Intente de nuevo.")
            usuario = None  # Resetear usuario para pedirlo de nuevo
            continue
        
# Pedir contraseña (oculta)
        contraseña = getpass("Contraseña: ").strip()
        
# Verificar contraseña
        if contraseña == administradores[usuario]["password"]:
            print(f"\n¡Bienvenido, {administradores[usuario]['nombre']}!")
            return administradores[usuario]["nombre"]
        else:
            print("Contraseña incorrecta. Intente de nuevo.")
# Mantener el usuario correcto y pedir contraseña de nuevo


# Función para probar la validación (opcional)
if __name__ == "__main__":
    admin_logueado = validar_administrador()
    print(f"Administrador autenticado: {admin_logueado}")
